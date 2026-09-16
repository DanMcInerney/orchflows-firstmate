#!/usr/bin/env python3
"""Prepare the home that holds your saved Orchflows FirstMate workflow libraries: setup and doctor (Python 3.11+).

The checkout you installed as a plugin is the core; FirstMate owns every agent, worktree and record.
This CLI only creates the home's tree and the plugin catalogs that list the libraries you author there.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import uuid

if __name__ == "__main__":
    sys.dont_write_bytecode = True


CORE_NAME = "orchflows-firstmate"
RESERVED_NAMES = frozenset((CORE_NAME, "orchflows"))
CATALOG_NAME = "orchflows-firstmate-home"
CATALOGS = (".agents/plugins/marketplace.json", ".claude-plugin/marketplace.json")
NAME = re.compile(r"[a-z0-9][a-z0-9_-]{0,63}\Z")
HOME_README = """# Orchflows FirstMate home

Your saved workflow libraries live in `libraries/<name>/`; `artifacts/` is scratch and ignored.
The core is the orchflows-firstmate checkout installed in the harness that runs your FirstMate primary;
its `docs/home.md` and `docs/firstmate.md` cover this home, and the home is also a local-only FirstMate project.
Rerun `python <checkout>/scripts/orchflows.py setup` after adding or changing a library to refresh the catalogs.
"""
HOME_GITIGNORE = """/artifacts/
**/__pycache__/
**/*.py[cod]
"""


def home_path(value: str | Path | None = None) -> Path:
    selected = value if value is not None else os.environ.get("ORCHFLOWS_FIRSTMATE_HOME")
    return Path(selected).expanduser().resolve() if selected else (Path.home() / ".orchflows-firstmate").resolve()


def check_setup_home(home: Path) -> None:
    """Refuse a home that overlaps a normal Orchflows home or carries its catalogs."""
    protected = [(Path.home() / ".orchflows").resolve()]
    if os.environ.get("ORCHFLOWS_HOME"):
        protected.append(Path(os.environ["ORCHFLOWS_HOME"]).expanduser().resolve())
    for normal_home in protected:
        if home.is_relative_to(normal_home) or normal_home.is_relative_to(home):
            raise ValueError(f"FirstMate package home overlaps the normal Orchflows home: {home}")
    if (home / ".local/packages/orchflows").exists():
        raise ValueError(f"Normal Orchflows core already exists in this home: {home}")
    for relative in CATALOGS:
        path = home / relative
        if not path.is_file():
            continue
        try:
            catalog = json.loads(path.read_text(encoding="utf-8"))
        except (UnicodeError, json.JSONDecodeError):
            continue  # Setup may repair a damaged catalog in its own home.
        if isinstance(catalog, dict) and catalog.get("name") in {"orchflows-home", "orchflows-local"}:
            raise ValueError(f"Normal Orchflows catalog is protected: {path}")


def _is_link(path: Path) -> bool:
    try:
        return path.is_symlink() or bool(getattr(path.lstat(), "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT)
    except FileNotFoundError:
        return False


def _manifest(root: Path) -> dict:
    path = root / "plugin.json"
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"No package manifest found in {root}") from exc
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Malformed package manifest {path}: {exc}") from exc
    if not isinstance(manifest, dict) or not isinstance(manifest.get("name"), str) or not NAME.fullmatch(manifest["name"]):
        raise ValueError(f"Package manifest needs a valid name: {path}")
    if not isinstance(manifest.get("version"), str) or not manifest["version"]:
        raise ValueError(f"Package manifest needs a version: {path}")
    return {"name": manifest["name"], "version": manifest["version"]}


def _libraries(home: Path) -> tuple[list[dict], list[str]]:
    entries, issues = [], []
    directory = home / "libraries"
    if not directory.is_dir():
        return entries, [f"Missing libraries directory: {directory}"]
    for path in sorted(directory.iterdir()):
        if path.name.startswith(".") or not path.is_dir():
            continue
        try:
            if _is_link(path):
                raise ValueError(f"Library is a link; not catalogued: {path}")
            manifest = _manifest(path)
            if not (path / "skills").is_dir():
                raise ValueError(f"Library lacks a skills directory: {path}")
            entries.append({**manifest, "package_root": str(path)})
        except (OSError, ValueError) as exc:
            issues.append(str(exc))
    names = [entry["name"] for entry in entries]
    issues.extend(f"Ambiguous library name: {name}" for name in sorted(set(names)) if names.count(name) > 1 or name in RESERVED_NAMES)
    return entries, issues


def _catalog_texts(home: Path, libraries: list[dict]) -> dict[str, str]:
    names = [entry["name"] for entry in libraries]
    sources = {entry["name"]: "./" + Path(entry["package_root"]).relative_to(home).as_posix()
               for entry in libraries if entry["name"] not in RESERVED_NAMES and names.count(entry["name"]) == 1}
    catalogs = {
        ".agents/plugins/marketplace.json": {
            "name": CATALOG_NAME,
            "interface": {"displayName": "Orchflows FirstMate Home"},
            "plugins": [{"name": name, "source": {"source": "local", "path": source},
                         "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                         "category": "Productivity"} for name, source in sources.items()],
        },
        ".claude-plugin/marketplace.json": {
            "name": CATALOG_NAME, "owner": {"name": CATALOG_NAME},
            "plugins": [{"name": name, "source": source} for name, source in sources.items()],
        },
    }
    return {relative: json.dumps(catalog, indent=2) + "\n" for relative, catalog in catalogs.items()}


def _seed_text(path: Path, contents: str) -> str:
    if _is_link(path) or path.exists():
        return "preserved"
    path.write_text(contents, encoding="utf-8", newline="\n")
    return "created"


def _replace_text(path: Path, contents: str) -> str:
    if path.is_file() and path.read_text(encoding="utf-8") == contents:
        return "current"
    temporary = path.with_name(f".{path.name}-{uuid.uuid4().hex}.tmp")
    try:
        with temporary.open("x", encoding="utf-8", newline="") as stream:
            stream.write(contents)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)
    return "written"


def _init_git(home: Path) -> tuple[str, list[str]]:
    if (home / ".git").exists():
        return "preserved", []
    git = shutil.which("git")
    if not git:
        return "unavailable", []
    result = subprocess.run([git, "-C", str(home), "init", "--quiet"], capture_output=True, text=True, check=False)
    if result.returncode:
        return "unavailable", [f"Git initialization failed: {result.stderr.strip()}"]
    return "initialized", []


def setup(home: Path) -> dict:
    home = home.resolve()
    check_setup_home(home)
    for relative in ("libraries", ".agents", ".agents/plugins", ".claude-plugin", ".git", "README.md", ".gitignore", *CATALOGS):
        if _is_link(home / relative):
            raise ValueError(f"Setup does not write through links: {home / relative}")
    for relative in ("libraries", ".agents/plugins", ".claude-plugin"):
        (home / relative).mkdir(parents=True, exist_ok=True)
    files = {"README.md": _seed_text(home / "README.md", HOME_README),
             ".gitignore": _seed_text(home / ".gitignore", HOME_GITIGNORE)}
    libraries, issues = _libraries(home)
    for relative, text in _catalog_texts(home, libraries).items():
        files[relative] = _replace_text(home / relative, text)
    git, git_issues = _init_git(home)
    issues.extend(git_issues)
    return {"status": "partial" if issues else "ready", "home": str(home), "files": files,
            "libraries": libraries, "git": git, "issues": issues}


def doctor(home: Path) -> dict:
    home = home.resolve()
    libraries, issues = _libraries(home)
    checks = {"libraries": libraries, "catalogs": {}}
    issues.extend(f"Missing home entry: {relative}" for relative in ("README.md", ".gitignore") if not (home / relative).exists())
    for relative, text in _catalog_texts(home, libraries).items():
        path = home / relative
        stale = not path.is_file() or path.read_text(encoding="utf-8") != text
        checks["catalogs"][relative] = "stale" if stale else "ok"
        if stale:
            issues.append(f"Catalog {relative} does not match the libraries; rerun setup")
    return {"status": "incomplete" if issues else "ready", "home": str(home), "checks": checks, "issues": issues}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    home_help = "Package home (default: ORCHFLOWS_FIRSTMATE_HOME or ~/.orchflows-firstmate)"
    commands.add_parser("setup", help="Create or refresh the home and its library catalogs").add_argument("--home", help=home_help)
    commands.add_parser("doctor", help="Check a home without changing it").add_argument("--home", help=home_help)
    args = parser.parse_args(argv)
    try:
        result = setup(home_path(args.home)) if args.command == "setup" else doctor(home_path(args.home))
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps(result, separators=(",", ":")))
    return 1 if result.get("issues") else 0


if __name__ == "__main__":
    raise SystemExit(main())
