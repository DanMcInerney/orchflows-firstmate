"""Project enablement and retained instruction context for existing FirstMate owners.

This module supplies configuration and launch inputs. TaskGroups and fm-spawn
remain the owners of task identity, dispatch, metadata and lifecycle behavior.
"""
import os
from pathlib import Path
import re
import sys
import tempfile

from fm_task_group_launch import role
from fm_task_group_delivery import LOCAL_DELIVERY, local_delivery, root_delivery, validate_root_launch_worktree
from fm_task_group_primitives import admit, attachment_primitive, is_dynamic
from fm_task_group_store import (GroupError, canonical, clean_commit, digest, group_lock,
                                 identifier, package_inventory, read_bytes, read_json,
                                 safe_path, snapshot_package, sync_directory, write_bytes,
                                 write_json)

_MANIFESTS = ("plugin.json", ".claude-plugin/plugin.json", ".codex-plugin/plugin.json")
_REQUIRED = ("skills/orch-work/SKILL.md", "skills/orch-review/SKILL.md",
             "scripts/firstmate.py", "scripts/package_identity.py")
_LIBRARY_DIR = "firstmate-libraries"
_MARKER = "firstmate-libraries.json"
_RESERVED = {"orchflows", "orchflows-firstmate", "orchflows-firstmate-home",
             "design-loop", _LIBRARY_DIR}
_OVERRIDES = ("FM_STATE_OVERRIDE", "FM_DATA_OVERRIDE", "FM_PROJECTS_OVERRIDE",
              "FM_CONFIG_OVERRIDE")


def _linux(owner):
    if not sys.platform.startswith("linux") or owner.runtime.windows:
        raise GroupError("Orchflows project enablement requires Linux")


def _manifest(root, *, core=False):
    value = read_json(root / "plugin.json")
    name = identifier(value.get("name"), "package name")
    version = value.get("version")
    if (not isinstance(version, str) or not version.strip() or len(version) > 128 or
            any(ord(char) < 32 for char in version)):
        raise GroupError("package manifest requires a nonempty version")
    if core and name != "orchflows-firstmate":
        raise GroupError("enable requires the standalone orchflows-firstmate package")
    for relative in _MANIFESTS[1:]:
        path = root / relative
        if core or path.exists() or path.is_symlink():
            other = read_json(path)
            if (other.get("name"), other.get("version")) != (name, version):
                raise GroupError("package manifests disagree on name or version")
    if not core and value.get("skills", "./skills/") not in ("./skills/", "./skills", "skills/", "skills"):
        raise GroupError("selected library must declare its local skills directory")
    return value


def _library(source):
    source = safe_path(source, directory=True)
    manifest = _manifest(source)
    name = manifest["name"]
    if name in _RESERVED or source.name == "design-loop":
        raise GroupError("reserved or inactive library cannot be selected")
    inventory = package_inventory(source)
    skills = []
    for entry in inventory:
        parts = Path(entry["path"]).parts
        if len(parts) == 3 and parts[0] == "skills" and parts[2] == "SKILL.md":
            identifier(parts[1], "library skill name")
            skills.append(entry["path"])
    if not skills:
        raise GroupError("selected library must contain skills/*/SKILL.md")
    return source, name, inventory, skills


def _store(owner):
    return safe_path(owner.home / "data" / ".orchflows", directory=True, exists=False)


def _configuration(owner):
    path = safe_path(owner.home / "config" / "orchflows.json", exists=False)
    if not path.exists():
        return {"schema": 1, "projects": {}}
    value = read_json(path)
    if (set(value) != {"schema", "projects"} or type(value["schema"]) is not int or
            value["schema"] != 1 or not isinstance(value["projects"], dict)):
        raise GroupError("invalid Orchflows project configuration")
    for project, entry in value["projects"].items():
        if (not isinstance(project, str) or
                str(safe_path(project, directory=True, exists=False)) != project or
                not isinstance(entry, dict) or
                set(entry) not in ({"package_path", "package_digest", "primitive", "review_policy"},
                                   {"package_path", "package_digest", "primitive", "review_policy", "workflow"})):
            raise GroupError("invalid Orchflows project entry")
        identity = entry["package_digest"]
        if not isinstance(identity, str) or not re.fullmatch(r"[0-9a-f]{64}", identity):
            raise GroupError("invalid enabled package digest")
        if entry["package_path"] != str(_store(owner) / ("package-" + identity)):
            raise GroupError("enabled package path differs from its immutable identity")
        admit(entry["primitive"], entry["review_policy"], entry.get("workflow"))
    return value


def _copy_inventory(source, target, inventory):
    target.mkdir(parents=True)
    for entry in inventory:
        destination = target / entry["path"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        payload = read_bytes(source / entry["path"], 64 * 1024 * 1024)
        if digest(payload) != entry["sha256"]:
            raise GroupError("package changed during enablement")
        write_bytes(destination, payload, exclusive=True)
    if package_inventory(source) != inventory or package_inventory(target) != inventory:
        raise GroupError("package changed during enablement")


def _write_config(owner, value):
    directory = safe_path(owner.home / "config", directory=True, exists=False)
    directory.mkdir(exist_ok=True)
    write_json(directory / "orchflows.json", value)


def supports_launch_context(package):
    """Missing capability metadata denotes the retained legacy client contract."""
    marker = safe_path(Path(package) / "scripts/firstmate-client.json", exists=False)
    if not marker.exists():
        return False
    value = read_json(marker)
    expected = {"schema": 1, "launch_context_schema": 1}
    dynamic = {**expected, "workflows": ["dynamic"]}
    local = {**dynamic, "root_deliveries": [LOCAL_DELIVERY]}
    if (value not in (expected, dynamic, local) or any(type(value.get(key)) is not int for key in expected)):
        raise GroupError("unsupported retained client capability metadata")
    return True


def supports_dynamic(package):
    return (supports_launch_context(package) and
            read_json(Path(package) / "scripts/firstmate-client.json").get("workflows") == ["dynamic"])


def supports_local_delivery(package):
    return (supports_dynamic(package) and
            read_json(Path(package) / "scripts/firstmate-client.json").get("root_deliveries") == [LOCAL_DELIVERY])


def enable(owner, package, project, primitive="Work", review_policy="none", libraries=(), workflow=None):
    """Freeze one project default without changing already attached tasks."""
    _linux(owner)
    if workflow == "dynamic" and review_policy == "none":
        review_policy = "workflow-review"
    admit(primitive, review_policy, workflow)
    for variable in _OVERRIDES:
        if os.environ.get(variable):
            raise GroupError("Orchflows enablement does not support custom state/data/config/project paths")
    package = safe_path(package, directory=True)
    project = safe_path(project, directory=True)
    commit = clean_commit(project)
    _manifest(package, core=True)
    if not supports_launch_context(package):
        raise GroupError("project enablement requires a client declaring launch-context support")
    if workflow == "dynamic":
        if not supports_dynamic(package):
            raise GroupError("dynamic enablement requires declared dynamic client capability")
        if not read_bytes(package / "skills/orch-dynamic-workflow/SKILL.md").strip():
            raise GroupError("dynamic skill is empty")
    for relative in _REQUIRED:
        if not read_bytes(package / relative).strip():
            raise GroupError("required primitive or client file is empty")
    for relative in (_LIBRARY_DIR, _MARKER):
        path = package / relative
        if path.exists() or path.is_symlink():
            raise GroupError("source package contains reserved FirstMate library paths")
    inventory = package_inventory(package)
    selected = [_library(source) for source in libraries]
    names = [item[1] for item in selected]
    if len(set(names)) != len(names):
        raise GroupError("duplicate selected library name")
    # Fail malformed existing configuration before preparing or publishing data.
    _configuration(owner)
    store = _store(owner)
    with group_lock(store):
        configuration = _configuration(owner)
        with tempfile.TemporaryDirectory(prefix=".enable-", dir=store) as temporary:
            staging = Path(temporary)
            try:
                assembled = staging / "package"
                _copy_inventory(package, assembled, inventory)
                _manifest(assembled, core=True)
                catalog = []
                for source, name, entries, skills in selected:
                    relative = Path(_LIBRARY_DIR) / name
                    _copy_inventory(source, assembled / relative, entries)
                    catalog.append({"name": name, "root": relative.as_posix(),
                                    "skills": [(relative / skill).as_posix() for skill in skills]})
                write_json(assembled / _MARKER, {"schema": 1, "libraries": catalog}, exclusive=True)
                identity = digest(canonical(package_inventory(assembled)))
                destination = safe_path(store / ("package-" + identity), directory=True, exists=False)
                if destination.exists():
                    if digest(canonical(package_inventory(destination))) != identity:
                        raise GroupError("enabled package snapshot changed")
                else:
                    frozen = staging / "snapshot"
                    if snapshot_package(assembled, frozen) != identity:
                        raise GroupError("assembled package changed during enablement")
                    # Moving a directory between parents needs write permission
                    # on that directory on Linux; seal it before config publication.
                    frozen.chmod(0o755)
                    os.replace(frozen, destination)
                    destination.chmod(0o555)
                    sync_directory(store)
                clean_commit(project, commit)
                entry = {"package_path": str(destination), "package_digest": identity,
                         "primitive": primitive, "review_policy": review_policy}
                if workflow is not None:
                    entry["workflow"] = workflow
                configuration["projects"][str(project)] = entry
                _write_config(owner, configuration)
            finally:
                # snapshot_package seals directories; make only this disposable
                # preparation writable if a failed snapshot still needs cleanup.
                for path in staging.rglob("*"):
                    if path.is_dir() and not path.is_symlink():
                        path.chmod(0o700)
        return entry


def disable(owner, project):
    """Remove a future-task default; retained tasks and packages remain owned."""
    _linux(owner)
    project = safe_path(project, directory=True, exists=False)
    if not (owner.home / "config" / "orchflows.json").exists():
        _configuration(owner)
        return False
    with group_lock(_store(owner)):
        configuration = _configuration(owner)
        removed = configuration["projects"].pop(str(project), None)
        if removed is not None:
            _write_config(owner, configuration)
        return removed is not None


def auto_attach(owner, task, kind, backend, harness, project, workflow="default", mode=""):
    """Called by fm-spawn inside its existing launch and project locks."""
    if workflow not in ("default", "dynamic", "none"):
        raise GroupError("workflow selection must be default, dynamic or none")
    task_role = role(owner, task)
    meta = owner.home / "state" / (identifier(task, "task ID") + ".meta")
    if task_role or meta.exists() or meta.is_symlink():
        return task_role
    if workflow == "none":
        return None
    local = kind == "ship" and mode == "local-only" and workflow == "dynamic"
    if kind != "scout" and not local:
        if workflow == "dynamic":
            raise GroupError("dynamic workflow requires a scout or explicit ship --mode local-only")
        return None
    if kind == "scout" and mode:
        raise GroupError("dynamic scout cannot carry a ship delivery mode")
    project = safe_path(project, directory=True)
    entry = _configuration(owner)["projects"].get(str(project))
    if entry is None:
        if workflow == "dynamic":
            raise GroupError("dynamic selection requires an enabled project package")
        return None
    _linux(owner)
    if backend != "herdr" or harness not in ("claude", "codex"):
        raise GroupError("enabled Orchflows scout requires Herdr with Claude or Codex CLI")
    if any(os.environ.get(variable) for variable in _OVERRIDES):
        raise GroupError("enabled Orchflows scout does not support custom state/data/config/project paths")
    package = safe_path(entry["package_path"], directory=True)
    if digest(canonical(package_inventory(package))) != entry["package_digest"]:
        raise GroupError("enabled package snapshot changed")
    selected = "dynamic" if workflow == "dynamic" else entry.get("workflow")
    primitive = "Work" if selected == "dynamic" else entry["primitive"]
    policy = "workflow-review" if selected == "dynamic" else entry["review_policy"]
    if selected == "dynamic" and not supports_dynamic(package):
        raise GroupError("dynamic selection requires declared dynamic client capability")
    owner.attach(task, package, project, primitive, policy, workflow=selected,
                 delivery=local_delivery(task) if local else None)
    return "root"


def launch_context(owner, task, generation):
    """Publish exact-generation inputs after fm-spawn publishes its metadata."""
    if role(owner, task) != "root":
        return ""
    _linux(owner)
    # These callbacks can run while submit owns the task-group lock. fm-spawn's
    # existing task locks serialize this root's metadata/context publication.
    meta, attachment = owner.root_meta(task, generation, check_worktree=False)
    validate_root_launch_worktree(meta, attachment)
    if not supports_launch_context(attachment["package_path"]):
        return ""
    value = {"schema": 1, "firstmate_root": str(owner.code_root), "home": str(owner.home),
             "root": task, "generation": generation,
             "primitive": attachment_primitive(attachment), "package_path": attachment["package_path"]}
    if root_delivery(attachment):
        value["root_delivery"] = attachment["root_delivery"]
    directory = safe_path(owner.group(task) / "contexts", directory=True, exists=False)
    directory.mkdir(exist_ok=True)
    path = safe_path(directory / (identifier(generation, "generation") + ".json"), exists=False)
    if path.exists():
        if canonical(read_json(path)) != canonical(value):
            raise GroupError("immutable launch context changed")
    else:
        write_json(path, value, exclusive=True)
        path.chmod(0o444)
    return str(path)


def library_overlay(attachment):
    """Render only the selected catalog retained in this exact attachment."""
    package = safe_path(attachment["package_path"], directory=True)
    marker = package / _MARKER
    if not marker.exists() and not marker.is_symlink():
        return ""
    catalog = read_json(marker)
    if (set(catalog) != {"schema", "libraries"} or type(catalog["schema"]) is not int or
            catalog["schema"] != 1 or not isinstance(catalog["libraries"], list)):
        raise GroupError("invalid retained FirstMate library catalog")
    lines = ["# Retained Orchflows libraries", "",
             f"Core logical aliases orchflows and orchflows-firstmate resolve to {package}.",
             f"This attachment admits one read-only {attachment_primitive(attachment)} component. "
             "Read each selected library README when present and its skill dependency references. "
             "Custom skills may compose only that admitted primitive. Additional components, writers, "
             "Dynamic, Build and SelfImprove remain gated; never use native-child fallback."]
    if is_dynamic(attachment):
        lines[3] = ("This attachment selects dynamic composition: custom and meta skills may use "
                    "scoped Work components and one fresh read-only Review through this same client. "
                    "Read library READMEs and dependency references. Join and check before Review, then "
                    "perform one repair/check pass. Build, SelfImprove and nesting remain gated; "
                    "never use native-child fallback.")
    if catalog["libraries"]:
        lines.append("On initial launch and every relaunch, read the full retained custom skill selected "
                     "for this task and its required dependency guidance at the catalog paths below before "
                     "continuing. Reapply its deliverable and validation requirements to retained results "
                     "and remaining work. Before ordinary root completion, reread that skill and verify "
                     "its required report content, artifacts and checks are satisfied in the delivered result.")
    names = set()
    for entry in catalog["libraries"]:
        if not isinstance(entry, dict) or set(entry) != {"name", "root", "skills"}:
            raise GroupError("invalid retained library entry")
        name = identifier(entry["name"], "library name")
        relative = Path(_LIBRARY_DIR) / name
        if (name in _RESERVED or name in names or entry["root"] != relative.as_posix() or
                not isinstance(entry["skills"], list) or not entry["skills"]):
            raise GroupError("invalid retained library identity")
        names.add(name)
        root = safe_path(package / relative, directory=True)
        lines.append(f"- {name}: {root}")
        seen = set()
        for skill in entry["skills"]:
            if not isinstance(skill, str):
                raise GroupError("invalid retained library skill")
            parts = Path(skill).parts
            if (len(parts) != 5 or parts[:3] != (_LIBRARY_DIR, name, "skills") or
                    parts[4] != "SKILL.md" or skill in seen or
                    Path(skill).as_posix() != skill):
                raise GroupError("invalid retained library skill path")
            identifier(parts[3], "library skill name")
            seen.add(skill)
            path = safe_path(package / skill)
            if not path.is_file():
                raise GroupError("retained library skill is not a regular file")
            lines.append(f"  - {name}:{parts[3]}: {path}")
    return "\n".join(lines) + "\n"
