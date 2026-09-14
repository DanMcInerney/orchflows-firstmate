#!/usr/bin/env python3
"""Run the owned package and FirstMate fixture suites with native Linux tools."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ("bash", "git", "python3", "lsof", "jq", "node", "tasks-axi", "timeout")
NATIVE = ("bash", "git", "python3", "lsof", "jq", "node", "timeout")
# These tests exercise Windows APIs and cannot run on Ubuntu. Missing Linux
# dependencies are errors; their skipped tests must never look like a pass.
UNITTEST = r"""
import json, os, pathlib, sys, unittest
suite = unittest.defaultTestLoader.discover(sys.argv[1])
result = unittest.TextTestRunner(verbosity=2).run(suite)
skips = [{"test": str(test), "reason": reason} for test, reason in result.skipped]
unexpected = [entry for entry in skips if not entry["reason"].startswith(
    ("native Windows", "requires explicit native Windows"))]
record = {"run": result.testsRun, "passed": result.testsRun - len(result.skipped)
          - len(result.failures) - len(result.errors), "skipped": skips,
          "unexpected_skips": unexpected, "failures": len(result.failures),
          "errors": len(result.errors)}
pathlib.Path(sys.argv[2]).write_text(json.dumps(record, indent=2) + "\n")
sys.exit(0 if result.wasSuccessful() and not unexpected and result.testsRun else 1)
"""


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def identity(root, *, allow_links=False):
    rows = []
    links = 0
    for path in root.rglob("*"):
        if ".git" in path.parts or "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
            continue
        if path.is_symlink():
            if not allow_links or not path.resolve(strict=True).is_relative_to(root.resolve()):
                raise ValueError(f"Source snapshot cannot contain this link: {path}")
            rows.append((path.relative_to(root).as_posix(),
                         hashlib.sha256(os.readlink(path).encode()).hexdigest()))
            links += 1
            continue
        if path.is_file():
            name = path.relative_to(root).as_posix()
            rows.append((name, hashlib.sha256(path.read_bytes()).hexdigest()))
    rows.sort()
    digest = hashlib.sha256("".join(name + "\0" + digest + "\n" for name, digest in rows).encode()).hexdigest()
    return {"files": len(rows), "symlinks": links, "sha256": digest}


def filesystem(path):
    # mountinfo escapes spaces, tabs, newlines and backslashes as octal.
    def unescape(value):
        for number in (32, 9, 10, 92):
            value = value.replace(chr(92) + format(number, "03o"), chr(number))
        return value
    found = []
    for line in Path("/proc/self/mountinfo").read_text().splitlines():
        left, right = line.split(" - ", 1)
        mount = Path(unescape(left.split()[4]))
        if path.is_relative_to(mount):
            found.append((len(mount.parts), right.split()[0]))
    if not found:
        raise ValueError(f"Cannot establish Linux filesystem for {path}")
    return max(found)[1]


def preflight(bin_dirs, work_root):
    if sys.platform != "linux":
        raise ValueError("Run this command with python3 inside Ubuntu/WSL; native Windows development is deferred")
    work_root = work_root.expanduser().resolve()
    ancestor = work_root
    while not ancestor.exists():
        ancestor = ancestor.parent
    fs = filesystem(ancestor)
    if fs not in {"ext4", "ext3", "ext2", "btrfs", "xfs", "tmpfs", "overlay"}:
        raise ValueError(f"Use a Linux filesystem for --work-root (observed {fs}); do not stage under /mnt/c")
    directories = [str(path.expanduser().resolve()) for path in bin_dirs]
    directories.extend(("/usr/local/bin", "/usr/bin", "/bin"))
    search_path = os.pathsep.join(dict.fromkeys(directories))
    selected = {}
    for name in REQUIRED:
        executable = shutil.which(name, path=search_path)
        if not executable:
            raise ValueError(f"Missing Linux dependency: {name}. Install it in Ubuntu or supply --bin-dir")
        resolved = Path(executable).resolve()
        with resolved.open("rb") as stream:
            magic = stream.read(4)
        if name in NATIVE and magic != b"\x7fELF":
            raise ValueError(f"{name} must be a native Linux ELF executable: {resolved}")
        if magic[:2] == b"MZ" or resolved.suffix.lower() == ".exe":
            raise ValueError(f"Windows executable is not allowed: {resolved}")
        selected[name] = {"command": executable, "resolved": str(resolved)}
    return {"platform": platform.platform(), "python": sys.version.split()[0],
            "filesystem": fs, "work_root": str(work_root), "tools": selected}, search_path


def check(args, probe, search_path):
    work_root = Path(probe["work_root"])
    work_root.mkdir(parents=True, exist_ok=True)
    run = Path(tempfile.mkdtemp(prefix="check-", dir=work_root))
    run.chmod(0o700)
    receipt = {"schema": 1, "scope": "Linux package/controller/owner fixtures; no live fleet",
               "status": "running", "started_at": time.time(), "environment": probe, "checks": []}
    print(f"Linux check workspace: {run}", flush=True)
    try:
        snapshot = run / "repo"
        for relative in ("packages/orchflows-firstmate", "integrations/firstmate"):
            src, dest = ROOT / relative, snapshot / relative
            before = identity(src)
            shutil.copytree(src, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"))
            if identity(dest) != before or identity(src) != before:
                raise ValueError(f"Source changed while staging {relative}; retry with a stable worktree")
            receipt.setdefault("inputs", {})[relative] = before
        for directory in ("home", "tmp", "config", "state", "codex", "claude", "logs"):
            (run / directory).mkdir(mode=0o700)
        env = {
            "PATH": search_path, "HOME": str(run / "home"), "TMPDIR": str(run / "tmp"),
            "XDG_CONFIG_HOME": str(run / "config"), "XDG_STATE_HOME": str(run / "state"),
            "CODEX_HOME": str(run / "codex"), "CLAUDE_CONFIG_DIR": str(run / "claude"),
            "PYTHONDONTWRITEBYTECODE": "1", "PYTHONNOUSERSITE": "1",
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null",
            "GIT_TERMINAL_PROMPT": "0", "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8",
            "SHELL": probe["tools"]["bash"]["command"], "TERM": "dumb",
        }
        candidate = run / "firstmate"
        env["FM_STAGE1_FIRSTMATE_ROOT"] = str(candidate)
        python = probe["tools"]["python3"]["command"]

        def execute(name, command):
            log = run / "logs" / (name + ".log")
            start = time.monotonic()
            with log.open("w", encoding="utf-8") as stream:
                process = subprocess.run(command, cwd=snapshot, env=env, stdout=stream,
                                         stderr=subprocess.STDOUT)
            record = {"name": name, "exit": process.returncode,
                      "seconds": round(time.monotonic() - start, 3), "log": str(log)}
            receipt["checks"].append(record)
            write_json(run / "receipt.json", receipt)
            print(f"{name}: {'passed' if process.returncode == 0 else 'FAILED'} ({record['seconds']}s)", flush=True)
            if process.returncode:
                print(log.read_text(encoding="utf-8")[-12000:], file=sys.stderr)
            return process.returncode == 0

        source = args.source.expanduser().resolve()
        git = probe["tools"]["git"]["command"]
        # A research checkout made by Windows Git can contain CRLF while its
        # canonical blobs are clean. Validate that view without changing its
        # config, files or pin, then check out the same objects as native LF.
        manifest = json.loads((snapshot / "integrations/firstmate/manifest.json").read_text())
        pin = manifest["firstmate_commit"]
        def source_git(*arguments):
            return subprocess.run([git, "-c", "core.autocrlf=true", "-C", str(source), *arguments],
                                  env=env, text=True, capture_output=True, check=True).stdout.strip()
        if source_git("rev-parse", "HEAD") != pin:
            raise ValueError("Research FirstMate HEAD differs from the distribution pin")
        if source_git("status", "--porcelain"):
            raise ValueError("Research FirstMate checkout has changes beyond checkout line endings")
        reference = snapshot / ".sources/firstmate"
        reference.parent.mkdir()
        if not execute("reference-clone", [git, "-c", "core.autocrlf=false", "clone",
                                          "--no-hardlinks", "--no-checkout", str(source), str(reference)]):
            raise ValueError("Could not copy the pinned Git objects into Linux storage")
        if not execute("reference-checkout", [git, "-c", "core.autocrlf=false", "-C",
                                             str(reference), "checkout", "--detach", pin]):
            raise ValueError("Could not check out the pinned Linux research reference")
        receipt["firstmate_commit"] = pin
        if not execute("prepare", [python, "-B", "integrations/firstmate/prepare.py",
                                  "--source", str(reference), "--destination", str(candidate)]):
            raise ValueError("FirstMate preparation failed; retained logs identify the refusal")
        receipt["candidate"] = identity(candidate, allow_links=True)
        okay = True
        for label, tests in (("package", "packages/orchflows-firstmate/tests"),
                             ("integration", "integrations/firstmate/tests")):
            results = run / "logs" / (label + ".json")
            passed = execute(label, [python, "-B", "-c", UNITTEST, tests, str(results)])
            if results.exists():
                receipt["checks"][-1]["tests"] = json.loads(results.read_text())
            okay = passed and okay
        for relative, expected in receipt["inputs"].items():
            if identity(snapshot / relative) != expected:
                raise ValueError(f"Tests modified their source snapshot: {relative}")
        receipt["status"] = "passed" if okay else "failed"
        return 0 if okay else 1
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        receipt["status"] = "failed"
        receipt["error"] = str(exc)
        print(str(exc), file=sys.stderr)
        return 1
    finally:
        receipt["finished_at"] = time.time()
        write_json(run / "receipt.json", receipt)
        print(f"Receipt: {run / 'receipt.json'}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("doctor", "check"))
    parser.add_argument("--bin-dir", type=Path, action="append", default=[],
                        help="Explicit directory containing native Linux dependencies; repeatable")
    parser.add_argument("--work-root", type=Path, default=Path("/tmp/orchflows-firstmate-dev"))
    parser.add_argument("--source", type=Path, default=ROOT / ".sources/firstmate",
                        help="Clean pinned FirstMate research checkout")
    args = parser.parse_args()
    try:
        probe, search_path = preflight(args.bin_dir, args.work_root)
        if args.command == "doctor":
            print(json.dumps(probe, indent=2, sort_keys=True))
            return 0
        return check(args, probe, search_path)
    except (OSError, ValueError) as exc:
        parser.exit(2, f"Linux development preflight failed: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
