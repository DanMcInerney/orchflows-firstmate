"""Translate a bound task's declared files into per-launch Claude permissions."""
import re

from fm_task_group_launch import role
from fm_task_group_composition import caller_calls
from fm_task_group_delivery import validate_root_launch_worktree
from fm_task_group_store import GroupError, identifier, safe_path


def file_rule(runtime, tool, path, *, tree=False):
    path = safe_path(path, exists=False)
    absolute = path.as_posix()
    if runtime.windows:
        if not re.fullmatch(r"[A-Za-z]:", path.drive):
            raise GroupError("Claude grants require a local Windows drive")
        # Claude normalizes native drive paths; MSYS mount aliases like /tmp
        # are not Claude permission paths, even when Bash uses those aliases.
        absolute = "/" + path.drive[0].lower() + absolute[2:]
    if not absolute.startswith("/"):
        raise GroupError("Claude permission paths must be absolute")
    # Claude Read/Edit use gitignore patterns and // for an absolute path.
    # Escape literal glob characters rather than widening a user-supplied path.
    escaped = re.sub(r"([\\*?\[\]])", r"\\\1", absolute)
    return f"{tool}(/{escaped}{'/**' if tree else ''})"


def claude_permissions(owner, task, generation):
    identifier(task, "task ID")
    identifier(generation, "generation")
    task_role = role(owner, task)
    if task_role == "root":
        # Spawn publishes permissions before the ordinary ship creates its branch.
        meta, attachment = owner.root_meta(task, generation, check_worktree=False)
        validate_root_launch_worktree(meta, attachment)
    elif task_role == "component":
        binding, record, attachment = owner.component_context(task)
        meta = owner.component_meta(task, binding, record)
    else:
        raise GroupError("Claude grants require a bound task-group worker")
    if meta.get("spawn_gen") != generation or meta.get("harness") != "claude":
        raise GroupError("Claude grants require the current Claude worker generation")
    if not meta.get("tasktmp"):
        raise GroupError("Claude grants require recorded tasktmp")
    tasktmp = safe_path(meta.get("tasktmp", ""), directory=True)
    data = owner.task(task)
    state = owner.home / "state"
    reads = [(attachment["package_path"], True), (state / f"{task}.meta", False),
             (state / f"{task}.status", False), (state / f"{task}.inbox", True),
             (data / "brief.md", False), (data / "launch-brief.md", False),
             (tasktmp, True)]
    writes = [(tasktmp, True), (state / f"{task}.status", False)]
    if task_role == "component" and caller_calls(attachment, binding["request_id"]):
        reads.append((data / "orchflows-context", True))
        # Results arrive after launch. This group's retained evidence is
        # read-only; request/gather authority stays bound to the actual caller.
        reads.append((owner.group(attachment["root"]) / "results", True))
    if task_role == "root":
        reads.extend([(owner.group(task), True), (data / "report.md", False),
                      (owner.code_root / ".agents/skills/captain-hold-lifecycle/SKILL.md", False),
                      (owner.code_root / "bin/fm-captain-hold.sh", False),
                      (owner.code_root / "docs/captain-hold-lifecycle.md", False)])
        writes.append((data / "report.md", False))
    rules = [file_rule(owner.runtime, "Read", path, tree=tree) for path, tree in reads]
    rules.extend(file_rule(owner.runtime, "Edit", path, tree=tree) for path, tree in writes)
    # No mode change, extra working directory, blanket Bash grant or user-home edit.
    return {"allow": list(dict.fromkeys(rules))}
