"""Private namespaces, native dependencies, explicit access-token auth and cleanup."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("linux_dev", ROOT / "tools/linux-dev.py")
linux_dev = importlib.util.module_from_spec(spec)
spec.loader.exec_module(linux_dev)
FIXTURE = {
    "stock.py": '"""Deterministic stock calculation."""\x0a\x0adef total_units(counts):\x0a    return sum(counts)\x0a',
    "labels.py": '"""Deterministic code normalization."""\x0a\x0adef normalize_code(value):\x0a    return value.strip().upper()\x0a',
}
OWNERS = ("fm-herdr-lab.sh", "fm-brief.sh", "fm-task-group.py", "fm-spawn.sh",
          "fm-control.sh", "fm-teardown.sh", "fm-watch-arm.sh", "fm-crew-state.sh")


def metadata(path):
    if not path.is_file():
        return {}
    return dict(line.split("=", 1) for line in path.read_text().splitlines() if "=" in line)


def process_identity(pid):
    proc = Path("/proc") / str(pid)
    try:
        fields = (proc / "stat").read_text().rsplit(") ", 1)[1].split()
        return {"pid": pid, "start": fields[19], "exe": os.readlink(proc / "exe"),
                "cwd": os.readlink(proc / "cwd")}
    except (OSError, IndexError, ValueError):
        return None


def scoped_processes(namespace):
    # An observation, not a license to signal processes selected by pathname.
    found = []
    for proc in Path("/proc").iterdir():
        if not proc.name.isdigit():
            continue
        identity = process_identity(int(proc.name))
        if identity and Path(identity["cwd"]).is_relative_to(namespace):
            found.append(identity)
    return found


def preflight(args):
    probe, search_path = linux_dev.preflight(args.bin_dir, args.work_root)
    for name in ("herdr", "treehouse", "claude"):
        executable = shutil.which(name, path=search_path)
        if not executable:
            raise ValueError(f"Missing native Linux dependency: {name}")
        resolved = Path(executable).resolve()
        with resolved.open("rb") as stream:
            if stream.read(4) != b"\x7fELF":
                raise ValueError(f"{name} must be a native Linux ELF executable")
        probe["tools"][name] = {"command": executable, "resolved": str(resolved)}
    candidate = args.candidate.expanduser().resolve()
    package = args.package.expanduser().resolve()
    for name in OWNERS:
        if not (candidate / "bin" / name).is_file():
            raise ValueError(f"Candidate is missing FirstMate owner {name}; prepare it first")
    for name in ("scripts/firstmate.py", "skills/orch-work/SKILL.md"):
        if not (package / name).is_file():
            raise ValueError(f"Package is missing {name}")
    if candidate == package or candidate.is_relative_to(package) or package.is_relative_to(candidate):
        raise ValueError("Candidate and package must be separate source directories")
    return probe, search_path


def access_token(args, environ):
    token = environ.get("CLAUDE_CODE_OAUTH_TOKEN")
    expiry = args.access_token_expires_at
    method = "explicit environment"
    if args.claude_access_token_file:
        if token:
            raise ValueError("Choose environment auth or an explicit access-token cache, not both")
        source = args.claude_access_token_file.expanduser()
        info = source.lstat()
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid():
            raise ValueError("Selected access-token cache must be a user-owned regular file, not a symlink")
        try:
            data = json.loads(source.read_text(encoding="utf-8"))
            oauth = data["claudeAiOauth"]
            token = oauth["accessToken"]
            expiry = oauth["expiresAt"] / 1000
        except (KeyError, TypeError, ValueError):
            raise ValueError("Selected cache lacks a valid Claude access token and expiration") from None
        method = "explicit cache access-token-only read"
    if not isinstance(token, str) or not token or any(c in token for c in "\x0d\x0a\x00"):
        raise ValueError("Set CLAUDE_CODE_OAUTH_TOKEN or select --claude-access-token-file")
    remaining = None
    if expiry is not None:
        if not isinstance(expiry, (int, float)) or isinstance(expiry, bool) or not math.isfinite(expiry):
            raise ValueError("Access-token expiration must be a Unix timestamp")
        remaining = expiry - time.time()
        if remaining < args.timeout + 180:
            raise ValueError("Access-token lifetime is shorter than the requested timeout plus 180 seconds")
    return token, expiry, {"method": method, "remaining_seconds": round(remaining) if remaining else None,
                           "refresh_token_copied": False, "credential_file_copied": False}


class Runtime:
    def __init__(self, args, probe, search_path):
        self.args, self.probe = args, probe
        work_root = Path(probe["work_root"])
        work_root.mkdir(parents=True, exist_ok=True)
        self.namespace = Path(tempfile.mkdtemp(prefix="a-", dir=work_root))
        self.namespace.chmod(0o700)
        self.out = self.namespace / "evidence"
        self.out.mkdir(mode=0o700)
        self.secrets = []
        self.sentinel = None
        self.sentinel_identity = None
        self.sessions = []
        self.active_homes = []
        self.expiry = None
        self.receipt = {"schema": 1, "scope": "private Linux Claude one-readonly-component acceptance",
                        "status": "running", "namespace": str(self.namespace),
                        "started_at": time.time(), "environment": probe, "runs": []}
        self.env = {
            "HOME": str(self.namespace / "home"), "CLAUDE_CONFIG_DIR": str(self.namespace / "claude"),
            "CODEX_HOME": str(self.namespace / "codex"), "TMPDIR": str(self.namespace / "tmp"),
            "XDG_CONFIG_HOME": str(self.namespace / "c"), "XDG_STATE_HOME": str(self.namespace / "state"),
            "FM_HERDR_LAB_STATE_DIR": str(self.namespace / "lab"), "PATH": search_path,
            "SHELL": probe["tools"]["bash"]["command"], "TERM": "xterm-256color",
            "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8", "DISABLE_AUTOUPDATER": "1",
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_TERMINAL_PROMPT": "0",
            "PYTHONDONTWRITEBYTECODE": "1", "PYTHONNOUSERSITE": "1",
        }
        for name in ("home", "claude", "codex", "tmp", "c/herdr", "state", "lab", "project"):
            (self.namespace / name).mkdir(mode=0o700, parents=True, exist_ok=True)
        (self.namespace / "c/herdr/config.toml").write_text(
            '[terminal]\x0adefault_shell="/bin/bash"\x0ashell_mode="non_login"\x0anew_cwd="home"\x0a'
            '[update]\x0aversion_check=false\x0amanifest_check=false\x0a[session]\x0aresume_agents_on_restore=false\x0a')
        self.write_json(self.namespace / "claude/.claude.json",
                        {"hasCompletedOnboarding": True, "theme": "dark"})

    def clean(self, text):
        for secret in self.secrets:
            text = text.replace(secret, "[redacted]")
        return text

    def write(self, path, text):
        path.write_text(self.clean(text), encoding="utf-8")

    def write_json(self, path, value):
        self.write(path, json.dumps(value, indent=2, sort_keys=True) + "\x0a")

    def save(self):
        self.write_json(self.out / "receipt.json", self.receipt)

    def run(self, args, *, env=None, cwd=None, timeout=90, check=True):
        try:
            result = subprocess.run([str(arg) for arg in args], env=env or self.env,
                                    cwd=cwd or self.namespace / "home", capture_output=True,
                                    text=True, timeout=timeout)
        except subprocess.TimeoutExpired as error:
            self.failed_operation(args, "timeout", error.stdout, error.stderr)
            raise
        result.stdout, result.stderr = self.clean(result.stdout), self.clean(result.stderr)
        if result.returncode:
            log = self.failed_operation(args, result.returncode, result.stdout, result.stderr)
            if check:
                raise RuntimeError(f"Operation {Path(str(args[0])).name} failed with exit {result.returncode}; "
                                   f"inspect {log}")
        return result

    def failed_operation(self, args, outcome, stdout, stderr):
        def as_text(value):
            return value.decode("utf-8", errors="replace") if isinstance(value, bytes) else value or ""
        failures = self.receipt.setdefault("operation_failures", [])
        name = "operation-failure-" + str(len(failures) + 1) + ".log"
        self.write(self.out / name, as_text(stdout) + as_text(stderr))
        # Never record argv or environment: either can contain private inputs.
        failures.append({"operation": Path(str(args[0])).name, "outcome": outcome, "log": name})
        return self.out / name

    def validate_session_paths(self, session):
        # Herdr uses both API and terminal client sockets in this named session.
        # Linux sockaddr_un reserves one of its 108 bytes for the terminator.
        directory = Path(self.env["XDG_CONFIG_HOME"]) / "herdr/sessions" / session
        for name in ("herdr.sock", "herdr-client.sock"):
            path = directory / name
            if len(os.fsencode(path)) > 107:
                raise ValueError("Herdr socket path exceeds Linux capacity; select a shorter --work-root")

    def owner(self, name, *args, **kwargs):
        return self.run(["bash", self.candidate / "bin" / name, *args], **kwargs)

    def lab(self, *args, **kwargs):
        return self.owner("fm-herdr-lab.sh", *args, **kwargs)

    def stage(self):
        for attr in ("candidate", "package"):
            source = getattr(self.args, attr).expanduser().resolve()
            destination = self.namespace / (attr + "-source")
            before = linux_dev.identity(source, allow_links=attr == "candidate")
            shutil.copytree(source, destination, symlinks=True,
                            ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "*.pyo"))
            if linux_dev.identity(destination, allow_links=attr == "candidate") != before:
                raise ValueError(f"{attr} changed during staging")
            if linux_dev.identity(source, allow_links=attr == "candidate") != before:
                raise ValueError(f"{attr} source changed during staging")
            setattr(self, attr, destination)
            self.receipt[attr] = {"source": str(source), **before}
        self.env["FM_ROOT_OVERRIDE"] = str(self.candidate)
        self.receipt["driver"] = linux_dev.identity(ROOT / "tools/linux_acceptance")
        self.receipt["entrypoint_sha256"] = hashlib.sha256((ROOT / "tools/linux-acceptance.py").read_bytes()).hexdigest()

    def authenticate(self):
        token, self.expiry, details = access_token(self.args, os.environ)
        self.secrets.append(token)
        self.env["CLAUDE_CODE_OAUTH_TOKEN"] = token
        self.receipt["authentication"] = details

    def fixture(self):
        project = self.namespace / "project"
        for name, text in FIXTURE.items():
            self.write(project / name, text)
        self.run(["git", "init", "-b", "main", project])
        self.run(["git", "-C", project, "add", "."])
        env = {**self.env, "GIT_AUTHOR_DATE": "2026-09-14T00:00:00Z",
               "GIT_COMMITTER_DATE": "2026-09-14T00:00:00Z"}
        self.run(["git", "-C", project, "-c", "user.name=Acceptance Fixture",
                  "-c", "user.email=fixture@example.invalid", "commit", "-m", "Readonly acceptance fixture"], env=env)
        self.receipt["input_commit"] = self.run(["git", "-C", project, "rev-parse", "HEAD"]).stdout.strip()
        self.receipt["input_files"] = {name: hashlib.sha256(text.encode()).hexdigest() for name, text in FIXTURE.items()}
        return project

    def start_sentinel(self):
        herdr = self.probe["tools"]["herdr"]["command"]
        before = json.loads(self.run([herdr, "session", "list", "--json", "--session", "fm-lab-preflight"]).stdout)
        sessions = before.get("sessions", [])
        expected = str(self.namespace / "c/herdr/herdr.sock")
        if len(sessions) != 1 or sessions[0].get("running") is not False or sessions[0].get("socket_path") != expected:
            raise RuntimeError("Herdr preflight did not prove a fresh private default namespace")
        with (self.namespace / "sentinel.log").open("w") as log:
            self.sentinel = subprocess.Popen([herdr, "server", "--session", "default"], env=self.env,
                                              cwd=self.namespace / "home", stdout=log, stderr=log)
        self.sentinel_identity = process_identity(self.sentinel.pid)
        for _ in range(50):
            status = self.run([herdr, "status", "--json", "--session", "default"], check=False)
            if status.returncode == 0 and json.loads(status.stdout)["server"]["running"]:
                self.receipt["private_sentinel_verified"] = True
                return
            time.sleep(0.2)
        raise RuntimeError("Private Herdr tripwire sentinel did not start")

    def cleanup(self):
        records = []
        def attempt(operation, invoke, **identity):
            try:
                result = invoke()
                records.append({"operation": operation, **identity, "exit": result.returncode})
                self.write(self.out / f"cleanup-{len(records)}.log", result.stdout + result.stderr)
            except Exception as error:
                records.append({"operation": operation, **identity, "error_type": type(error).__name__})
        for home, env in reversed(self.active_homes):
            for path in sorted((home / "state").glob("*.meta")):
                attempt("exit", lambda p=path: self.owner("fm-control.sh", p.stem, "exit", env=env,
                                                         timeout=90, check=False), task=path.stem)
            for path in sorted((home / "state").glob("*.meta")):
                attempt("teardown", lambda p=path: self.owner("fm-teardown.sh", p.stem, env=env,
                                                             timeout=90, check=False), task=path.stem)
        for session in reversed(self.sessions):
            attempt("lab-teardown", lambda s=session: self.lab("teardown", s, timeout=90, check=False),
                    session=session)
        if self.sentinel and self.sentinel.poll() is None:
            if process_identity(self.sentinel.pid) == self.sentinel_identity:
                attempt("private-sentinel-stop", lambda: self.run(
                    [self.probe["tools"]["herdr"]["command"], "session", "stop", "default",
                     "--json", "--session", "default"], check=False))
                try:
                    self.sentinel.wait(timeout=20)
                except subprocess.TimeoutExpired:
                    records.append({"operation": "private-sentinel-exit", "error_type": "TimeoutExpired"})
            else:
                records.append({"operation": "private-sentinel-stop", "error_type": "IdentityMismatch"})
        self.env.pop("CLAUDE_CODE_OAUTH_TOKEN", None)
        self.receipt["cleanup"] = records
        self.receipt["scoped_processes_remaining"] = scoped_processes(self.namespace)
        self.receipt["no_private_credentials"] = not any(
            (self.namespace / name).exists() for name in ("claude/.credentials.json", "codex/auth.json"))
        self.receipt["cleanup_passed"] = all(item.get("exit") == 0 for item in records) and not (
            self.receipt["scoped_processes_remaining"]) and self.receipt["no_private_credentials"]
