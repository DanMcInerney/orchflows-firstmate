"""Prepare an isolated pinned FirstMate candidate; never install into a live home."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess


ROOT = Path(__file__).resolve().parent
BASE = "b182d0f908b78d08c7ccb8dce3775bdca8c5d657"


def run(*args: str, cwd: Path | None = None) -> str:
    return subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def distribution(root: Path) -> tuple[dict, list[Path]]:
    """Verify exactly the bytes that will be deployed before creating a checkout."""
    root = root.resolve()
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    if manifest["schema"] != 1 or manifest["firstmate_commit"] != BASE:
        raise ValueError("Integration manifest source identity differs")
    listed = {}
    for entry in manifest["files"]:
        name = entry["path"]
        relative = PurePosixPath(name)
        if (not isinstance(name, str) or "\\" in name or ":" in name
                or relative.is_absolute() or relative.as_posix() != name
                or ".." in relative.parts or len(relative.parts) < 2
                or relative.parts[0] not in {"patches", "overlay"} or name in listed):
            raise ValueError("Invalid or duplicate integration path")
        path = root / name
        for part in [path, *path.parents]:
            if part == root:
                break
            if part.is_symlink() or (hasattr(part, "is_junction") and part.is_junction()):
                raise ValueError("Integration links are not deployable")
        if not path.is_file() or not path.resolve().is_relative_to(root):
            raise ValueError("Integration path escapes the distribution or is absent")
        if hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
            raise ValueError(f"Integration file differs from its manifest: {name}")
        listed[name] = path
    actual = set()
    for directory in (root / "overlay", root / "patches"):
        for path in directory.rglob("*"):
            if "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
                continue
            if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
                raise ValueError("Integration links are not deployable")
            if path.is_file():
                actual.add(path.relative_to(root).as_posix())
    if actual != set(listed):
        raise ValueError("Integration inventory differs from its manifest")
    patches = manifest["patches"]
    if (not isinstance(patches, list) or not patches or len(patches) != len(set(patches))
            or set(patches) != {name for name in listed if name.startswith("patches/")}):
        raise ValueError("Integration patch sequence differs from its inventory")
    return manifest, [listed[name] for name in sorted(listed) if name.startswith("overlay/")]


def prepare(source: Path, destination: Path) -> dict:
    source, destination = source.resolve(), destination.resolve()
    if destination.exists():
        raise ValueError("Destination must not exist; an existing checkout is never overwritten")
    if destination.is_relative_to(source) or source.is_relative_to(destination):
        raise ValueError("Source and candidate must not overlap")
    if run("git", "rev-parse", "HEAD", cwd=source) != BASE:
        raise ValueError(f"FirstMate source must be checked out at {BASE}")
    if run("git", "status", "--porcelain", cwd=source):
        raise ValueError("FirstMate source must be clean")
    manifest, overlay = distribution(ROOT)
    run("git", "-c", "core.autocrlf=false", "clone", "--no-hardlinks", "--no-checkout", str(source), str(destination))
    run("git", "-c", "core.autocrlf=false", "checkout", "--detach", BASE, cwd=destination)
    for patch in manifest["patches"]:
        path = str(ROOT / patch)
        run("git", "apply", "--check", path, cwd=destination)
        run("git", "apply", path, cwd=destination)
    for path in overlay:
        target = destination / path.relative_to(ROOT / "overlay")
        if target.exists() or target.is_symlink():
            raise ValueError(f"New overlay file would overwrite upstream: {target}")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
        if target.parent.name == "bin":
            target.chmod(0o755)
    return {"status": "prepared", "firstmate_commit": BASE, "candidate": str(destination),
            "scope": "experimental local candidate; no live home or runtime certified"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--destination", required=True, type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(prepare(args.source, args.destination)))
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as exc:
        parser.exit(2, f"Preparation failed; any partial candidate is retained for inspection: {exc}\n")
