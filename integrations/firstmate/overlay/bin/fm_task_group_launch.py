"""Read-only callbacks for FirstMate's existing launch transaction.

Callbacks deliberately do not take the task-group lock: submit owns it while
fm-spawn calls these, and lifecycle owners can hold their existing metadata locks.
"""
import os
from pathlib import Path
import shlex

from fm_task_group_store import GroupError, clean_commit, safe_path


def role(owner, task):
    binding = owner.binding(task)
    attachment_path = owner.group(task) / "attachment.json"
    attachment_present = attachment_path.exists() or attachment_path.is_symlink()
    meta_path = owner.home / "state" / f"{task}.meta"
    current = owner.meta(task) if meta_path.exists() or meta_path.is_symlink() else {}
    advertised = current.get("task_group_role")
    if binding:
        if attachment_present or advertised not in (None, "component"):
            raise GroupError("conflicting task-group roles")
        owner.component_context(task)
        return "component"
    if attachment_present:
        if advertised not in (None, "root"):
            raise GroupError("conflicting task-group roles")
        owner.attachment(task)
        return "root"
    if advertised:
        raise GroupError("task-group metadata has no durable binding")
    return None


def launch_check(owner, task, kind, backend, harness, project, worktree=None):
    task_role = role(owner, task)
    if not task_role:
        return
    for variable in ("FM_STATE_OVERRIDE", "FM_DATA_OVERRIDE", "FM_PROJECTS_OVERRIDE", "FM_CONFIG_OVERRIDE"):
        if os.environ.get(variable):
            raise GroupError("Stage 1 task groups do not support custom state/data/config/project paths")
    if kind != "scout" or backend != "herdr" or harness not in ("claude", "codex"):
        raise GroupError("task-group launch requires a Herdr scout using Claude or Codex CLI")
    if task_role == "component":
        binding, record, attachment = owner.component_context(task)
        if record["state"] != "launching" or record["harness"] != harness:
            raise GroupError("component relaunch is unsupported; preserve the existing request")
        if (owner.home / "state" / f"{task}.meta").exists():
            raise GroupError("component metadata already exists; duplicate launch refused")
        owner.root_meta(binding["parent"], binding["accepted_parent_gen"])
    else:
        attachment = owner.attachment(task)
    project = safe_path(project, directory=True)
    if str(project) != attachment["project"]:
        raise GroupError("launch project differs from immutable attachment")
    clean_commit(project, attachment["input_commit"])
    if worktree:
        worktree = safe_path(worktree, directory=True)
        if worktree == project:
            raise GroupError("task-group worker requires its own isolated worktree")
        clean_commit(worktree, attachment["input_commit"])


def launch_meta(owner, task):
    task_role = role(owner, task)
    if not task_role:
        return ""
    fields = {"task_group_role": task_role, "task_group_epoch": "1"}
    if task_role == "component":
        binding, _, _ = owner.component_context(task)
        fields.update(task_group_parent=binding["parent"], task_group_request=binding["request_id"],
                      task_group_hash=binding["body_hash"], result_disposition="parent")
    return "".join(f"{key}={value}\n" for key, value in fields.items())


def python_command(owner, script):
    if not owner.runtime.windows:
        return "python3 -B " + shlex.quote(str(script))
    return ("env FM_TASK_GROUP_BASH=" + shlex.quote(Path(owner.runtime.bash).as_posix()) +
            " FM_TASK_GROUP_PYTHON=" + shlex.quote(Path(owner.runtime.python).as_posix()) + " " +
            shlex.quote(Path(owner.runtime.python).as_posix()) + " -B " +
            shlex.quote(Path(script).as_posix()))


def command_prefix(owner):
    return (python_command(owner, owner.code_root / "bin" / "fm-task-group.py") +
            " --home " + shlex.quote(owner.runtime.shell(owner.home)))


def component_brief(owner, binding, record, attachment):
    return ("# Task\n\n## Captain's intent\n\n"
            f"Return one read-only Work result to FirstMate root {binding['parent']}.\n\n"
            "## Firstmate spec\n\n"
            f"{record['body']['assignment']}\n\n"
            f"Inspect only this component's worktree at input commit {attachment['input_commit']}. "
            "Do not change project files, dependencies, Git state or the attached package. "
            "Use the assigned package's relevant Make guidance; no native children, fleet children, "
            "or independent review are authorized. Include evidence, file references and remaining gaps.\n\n"
            + component_overlay(owner, binding, attachment))


def component_overlay(owner, binding, attachment):
    child = binding["child"]
    return ("# FirstMate task-group component completion contract\n\n"
            f"Role: component; disposition: return evidence to parent {binding['parent']}; "
            f"request {binding['request_id']}; attachment epoch 1.\n"
            "This component contract governs completion. Do not write ordinary scout done status, "
            "deliver to the captain, open a PR, merge, promote, run no-mistakes, or complete the parent. "
            "Do not invoke Work or Review or another fleet command.\n"
            f"The immutable package is {attachment['package_path']} (SHA-256 {attachment['package_digest']}). "
            f"You may read your worktree, that package, your brief, and your metadata at "
            f"{owner.home / 'state' / (child + '.meta')}.\n"
            "Read the exact spawn_gen and tasktmp values from that metadata. Write a nonempty UTF-8 "
            "report within the recorded tasktmp directory, then invoke:\n\n"
            f"    {command_prefix(owner)} complete {shlex.quote(child)} --generation CURRENT_SPAWN_GEN --report ABSOLUTE_REPORT_PATH\n\n"
            "Replace the two argument values from your actual metadata/report. A busy group can be "
            "retried with the same generation and same report. Success requires a retained complete result; "
            "process exit, a transcript message or ordinary done status does not complete this assignment. "
            "After the controller accepts the report, stop work and leave cleanup to FirstMate.\n")


def launch_overlay(owner, task):
    task_role = role(owner, task)
    if not task_role:
        return ""
    if task_role == "component":
        binding, _, attachment = owner.component_context(task)
        return component_overlay(owner, binding, attachment)
    attachment = owner.attachment(task)
    package = Path(attachment["package_path"])
    # The package client is native Python and intentionally has no MSYS path
    # decoder. Give it native absolute paths; the owner handles metadata paths.
    client_code = owner.code_root.as_posix() if owner.runtime.windows else str(owner.code_root)
    client_home = owner.home.as_posix() if owner.runtime.windows else str(owner.home)
    client = (python_command(owner, package / "scripts" / "firstmate.py") +
              " --firstmate-root " + shlex.quote(client_code) +
              " --home " + shlex.quote(client_home) + " --root " + shlex.quote(task) +
              " --generation CURRENT_SPAWN_GEN --timeout 420")
    windows_note = ("On native Windows, pass a native absolute request path to the package client; "
                    "use cygpath -m to convert a recorded MSYS tasktmp path. " if owner.runtime.windows else "")
    return ("# FirstMate task-group root attachment\n\n"
            f"You remain a normal root scout. The attached orchflows-firstmate package is "
            f"{attachment['package_path']} (SHA-256 {attachment['package_digest']}), epoch 1. "
            f"The fixed read-only input commit is {attachment['input_commit']}. "
            "Stage 1 permits exactly one read-only Work component under FirstMate/Herdr; "
            "other workflows, Review, writers, nesting and native-child fallback are unavailable.\n"
            f"Read and apply the exact attached Work skill at {package / 'skills' / 'orch-work' / 'SKILL.md'}. "
            f"Read your current spawn_gen and tasktmp from {owner.home / 'state' / (task + '.meta')} before each call. "
            "Place the request JSON and all transient files inside your recorded tasktmp directory, "
            "keeping the project worktree clean. The request contains only request_id and assignment. "
            + windows_note +
            "Invoke the attached fork client with the actual generation and absolute request path:\n\n"
            f"    {client} submit --request REQUEST_JSON_PATH\n"
            f"    {client} status\n"
            f"    {client} gather\n\n"
            "A replay uses the same request ID and exact body. After relaunch, reconcile the saved request "
            "with your current generation; do not create a replacement component. A launching or uncertain "
            "request stays unresolved until FirstMate reconciles it. Read the complete retained report and "
            "identity before gather acknowledges receipt. While waiting, keep the join pending; do not "
            "mark done or paused for a person. Once gathered, incorporate evidence into your normal scout "
            f"report at {owner.home / 'data' / task / 'report.md'} and follow FirstMate's ordinary outer completion.\n")
