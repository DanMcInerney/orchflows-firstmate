"""Editable workflow libraries, routed through package setup and FirstMate snapshots."""
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile

from fm_task_group_store import (GroupError, canonical, clean_commit, digest, git, group_lock,
                                 identifier, package_inventory, read_bytes, read_json,
                                 safe_path, sync_directory, write_json)

CORE = "orchflows-firstmate"
SELECTION = "Orchflows selected skill: "


def _config(owner):
    path = safe_path(owner.home / "config/orchflows-home.json", exists=False)
    if not path.exists():
        return None
    value = read_json(path)
    if set(value) != {"schema", "home"} or type(value["schema"]) is not int or value["schema"] != 1:
        raise GroupError("invalid FirstMate workflow home configuration")
    return safe_path(value["home"], directory=True, exists=False)


def workflow_home(owner, explicit=None):
    selected = explicit or os.environ.get("ORCHFLOWS_FIRSTMATE_HOME") or _config(owner)
    return safe_path(Path(selected).expanduser() if selected else owner.home / "data/.orchflows-home",
                     directory=True, exists=False)


def _package(home):
    return safe_path(home / ".local/packages" / CORE, directory=True)


def _module(package):
    """Load the installed package's existing setup/resolve implementation."""
    scripts = safe_path(package / "scripts", directory=True)
    source = safe_path(scripts / "orchflows.py")
    # Package modules are versioned together. A short-lived owner command loads
    # one package; tests can call multiple homes with the same implementation.
    old = sys.path[:]
    sys.path.insert(0, str(scripts))
    try:
        spec = importlib.util.spec_from_file_location("_firstmate_workflow_package", source)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path[:] = old


def _validate_home(home):
    for relative in ("libraries", ".local", ".local/packages", ".agents", ".agents/plugins", ".claude-plugin"):
        safe_path(home / relative, directory=True, exists=False)
    libraries = home / "libraries"
    if libraries.exists():
        from fm_orchflows import _library
        for path in libraries.iterdir():
            if not path.name.startswith("."):
                _library(path)


def setup(owner, package=None, explicit=None):
    from fm_orchflows import _linux
    _linux(owner)
    home = workflow_home(owner, explicit)
    source = safe_path(package, directory=True) if package else _package(home)
    _validate_home(home)
    module = _module(source)
    module._validate_core(source)
    module.check_setup_home(home)
    with group_lock(home / ".local/firstmate"):
        result = module.setup(home, source, skip_host_config=True)
        if result["status"] != "ready":
            raise GroupError("workflow home setup requires attention: " + "; ".join(result["issues"]))
        directory = safe_path(owner.home / "config", directory=True, exists=False)
        directory.mkdir(exist_ok=True)
        write_json(directory / "orchflows-home.json", {"schema": 1, "home": str(home)})
    return result


def identity(value):
    if not isinstance(value, str) or value.count(":") != 1:
        raise GroupError("workflow identity must be library:skill")
    library, skill = value.split(":")
    # Use the portable package home name contract as well as controller IDs.
    for name in (library, skill):
        if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,63}", name):
            raise GroupError("invalid workflow library or skill name")
    return library, skill


def descriptor(manifest, skill):
    firstmate = manifest.get("firstmate", {})
    if not isinstance(firstmate, dict) or set(firstmate) - {"workflows"}:
        raise GroupError("invalid FirstMate library metadata")
    workflows = firstmate.get("workflows", {})
    if not isinstance(workflows, dict):
        raise GroupError("invalid FirstMate workflow declarations")
    value = workflows.get(skill, {})
    if not isinstance(value, dict) or set(value) - {"composition", "preferences", "libraries"}:
        raise GroupError("invalid selected workflow declaration")
    libraries = value.get("libraries", [])
    if (not isinstance(libraries, list) or len(libraries) > 32 or
            any(not isinstance(name, str) for name in libraries) or len(set(libraries)) != len(libraries)):
        raise GroupError("invalid selected workflow dependency libraries")
    for name in libraries:
        identity(str(name) + ":dependency")
    result = {}
    if "composition" in value:
        from fm_task_group_composition import validate_composition
        result["composition"] = validate_composition(value["composition"])
    if "preferences" in value:
        from fm_task_group_controls import validate_preferences
        result["workflow_preferences"] = validate_preferences(value["preferences"])
    return result, libraries


def resolve(owner, selected, explicit=None):
    library, skill = identity(selected)
    home = workflow_home(owner, explicit)
    _validate_home(home)
    package = _package(home)
    resolver = _module(package)
    result = resolver.resolve(home, library, skill=skill)
    root = safe_path(result["package_root"], directory=True)
    safe_path(result["skill_path"])
    # Retain whole libraries, including their scripts/assets and declarations.
    from fm_orchflows import _library
    libraries, seen = [], set()
    metadata = {}
    pending = [(library, skill)]
    while pending:
        name, selected_skill = pending.pop(0)
        entry = resolver.resolve(home, name, skill=selected_skill)
        source = safe_path(entry["package_root"], directory=True)
        manifest = read_json(source / "plugin.json")
        if name not in {"orchflows", CORE} and name not in seen:
            _library(source)
            libraries.append(source)
            seen.add(name)
        if selected_skill is not None:
            settings, dependencies = descriptor(manifest, selected_skill)
            if name == library and selected_skill == skill:
                metadata = settings
            for dependency in dependencies:
                if dependency not in seen and dependency not in {"orchflows", CORE}:
                    pending.append((dependency, None))
    return {**result, "identity": selected, "home": str(home),
            "libraries": [str(path) for path in libraries], **metadata}


def catalog(owner, explicit=None):
    home = workflow_home(owner, explicit)
    _validate_home(home)
    package = _package(home)
    module = _module(package)
    libraries, issues = module._libraries(home)
    if issues:
        raise GroupError("; ".join(issues))
    entries = [{"name": CORE, "package_root": str(package)}, *libraries]
    workflows = []
    for entry in entries:
        source = safe_path(entry["package_root"], directory=True)
        for path in sorted((source / "skills").glob("*/SKILL.md")):
            selected = entry["name"] + ":" + path.parent.name
            identity(selected)
            safe_path(path)
            workflows.append({"identity": selected, "skill_path": str(path)})
    return {"home": str(home), "workflows": workflows}


def brief(owner, selected, explicit=None):
    resolve(owner, selected, explicit)
    return ("# Selected Orchflows workflow\n" + SELECTION + selected + "\n"
            "Read the complete selected skill and its dependency guidance from the retained "
            "launch catalog before working and after relaunch. FirstMate snapshots those inputs "
            "at launch. Loading a skill continues in this caller; only Work/Review delegates.\n")


def brief_selection(owner, task):
    path = safe_path(owner.task(identifier(task)) / "brief.md", exists=False)
    if not path.exists():
        return None
    selected = [line[len(SELECTION):] for line in read_bytes(path).decode("utf-8").splitlines()
                if line.startswith(SELECTION)]
    if len(selected) > 1:
        raise GroupError("brief contains multiple selected workflows")
    if selected:
        identity(selected[0])
        return selected[0]
    return None


def enable_selection(owner, selected, project, explicit=None):
    from fm_orchflows import enable
    resolved = resolve(owner, selected, explicit)
    metadata = {key: resolved[key] for key in ("identity", "composition", "workflow_preferences")
                if key in resolved}
    return enable(owner, _package(Path(resolved["home"])), project,
                  libraries=resolved["libraries"], workflow="dynamic",
                  selection=metadata, library_home=resolved["home"])


def _delivered_library(project, relative, commit):
    """Read only regular Git blobs from a delivered commit on local default."""
    project = safe_path(project, directory=True)
    clean_commit(project)
    path = PurePosixPath(relative)
    if (not relative or path.is_absolute() or path.as_posix() != relative or
            ".." in path.parts or "\\" in relative or ":" in relative):
        raise GroupError("published library must be a relative project directory")
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40,64}", commit):
        raise GroupError("publication requires the exact delivered commit")
    # Match the existing merge-local owner's origin/HEAD, main, master order.
    # Never publish a worker's unmerged task branch or mutable revision expression.
    remote_default = git(project, "symbolic-ref", "--quiet", "--short",
                         "refs/remotes/origin/HEAD", accepted=(0, 1))
    default = (remote_default.removeprefix("origin/") if remote_default else
               next((name for name in ("main", "master")
                     if git(project, "rev-parse", "--verify", "--quiet", "refs/heads/" + name,
                            accepted=(0, 1))), None))
    if not default:
        raise GroupError("publication requires an existing local default branch")
    git(project, "merge-base", "--is-ancestor", commit, "refs/heads/" + default)
    raw = subprocess.run(["git", "-C", str(project), "ls-tree", "-rz", "--full-tree",
                          commit, "--", relative], check=True, capture_output=True, timeout=30).stdout
    entries = []
    for item in raw.split(b"\0"):
        if not item:
            continue
        header, filename = item.split(b"	", 1)
        mode, kind, oid = header.decode("ascii").split()
        name = filename.decode("utf-8")
        if mode not in {"100644", "100755"} or kind != "blob" or not name.startswith(relative + "/"):
            raise GroupError("published library requires regular committed Git blobs")
        target = PurePosixPath(name).relative_to(path)
        if target.is_absolute() or ".." in target.parts:
            raise GroupError("invalid committed library path")
        payload = subprocess.run(["git", "-C", str(project), "cat-file", "blob", oid],
                                 check=True, capture_output=True, timeout=30).stdout
        if len(payload) > 64 * 1024 * 1024:
            raise GroupError("committed library file exceeds publication bound")
        entries.append((target, payload, mode))
    if not entries:
        raise GroupError("delivered commit contains no library")
    return entries


def publish(owner, project, relative, commit, package=None, explicit=None):
    from fm_orchflows import _configuration, _library
    entries = _delivered_library(project, relative, commit)
    home = workflow_home(owner, explicit)
    # Validate delivered bytes before creating/updating a home.
    with tempfile.TemporaryDirectory(prefix="firstmate-workflow-publish-") as temporary:
        source = Path(temporary) / "library"
        source.mkdir()
        for path, payload, mode in entries:
            target = source / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
            target.chmod(int(mode[-3:], 8))
        _, name, inventory, skills = _library(source)
        # Controller identifiers are broader than portable package-home names.
        # Apply the package owner's exact library/skill naming contract before
        # setup or installation can write an entry its catalog cannot resolve.
        package_source = safe_path(package, directory=True) if package else _package(home)
        package_owner = _module(package_source)
        package_owner._manifest(source)
        manifest = read_json(source / "plugin.json")
        for skill in skills:
            skill_name = Path(skill).parts[1]
            package_owner._name(skill_name, "skill")
            descriptor(manifest, skill_name)
        setup(owner, package, explicit)
        with group_lock(home / ".local/firstmate"):
            _validate_home(home)
            destination = safe_path(home / "libraries" / name, directory=True, exists=False)
            # Reuse the package's staged replacement and catalog/setup owner.
            module = _module(_package(home))
            module._install(source, destination, core=False)
            result = module.setup(home, _package(home), skip_host_config=True)
            if result["status"] != "ready":
                raise GroupError("published library catalog requires attention")
            refreshed = []
            for project_path, entry in _configuration(owner)["projects"].items():
                if entry.get("library_home") != str(home) or not entry.get("selected_workflow"):
                    continue
                marker = read_json(Path(entry["package_path"]) / "firstmate-libraries.json")
                if name in [item["name"] for item in marker["libraries"]]:
                    enable_selection(owner, entry["selected_workflow"], project_path, str(home))
                    refreshed.append(project_path)
    return {"home": str(home), "library": name, "commit": commit,
            "library_digest": digest(canonical(inventory)), "refreshed_projects": refreshed}
