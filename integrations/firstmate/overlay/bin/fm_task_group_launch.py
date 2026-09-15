"""Callbacks for FirstMate's existing launch transaction.

Callbacks deliberately do not take the task-group lock: submit owns it while
fm-spawn calls these, and lifecycle owners can hold their existing metadata locks.
"""
import os
from pathlib import Path
import shlex

from fm_task_group_store import GroupError, clean_commit, git, safe_path
from fm_task_group_composition import caller_calls
from fm_task_group_delivery import (LOCAL_DELIVERY, root_delivery, validate_root_worktree,
                                    validate_root_launch_worktree)
from fm_task_group_primitives import (attachment_primitive, component_primitive, is_dynamic,
                                      validate_metadata)


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
        _, record, attachment = owner.component_context(task)
        if advertised:
            validate_metadata(current, attachment, record=record)
        return "component"
    if attachment_present:
        if advertised not in (None, "root"):
            raise GroupError("conflicting task-group roles")
        attachment = owner.attachment(task)
        if advertised:
            validate_metadata(current, attachment)
        return "root"
    if advertised:
        raise GroupError("task-group metadata has no durable binding")
    return None


def launch_check(owner, task, kind, backend, harness, project, worktree=None, mode=""):
    task_role = role(owner, task)
    if not task_role:
        return
    for variable in ("FM_STATE_OVERRIDE", "FM_DATA_OVERRIDE", "FM_PROJECTS_OVERRIDE", "FM_CONFIG_OVERRIDE"):
        if os.environ.get(variable):
            raise GroupError("Stage 1 task groups do not support custom state/data/config/project paths")
    if backend != "herdr" or harness not in ("claude", "codex"):
        raise GroupError("task-group launch requires Herdr using Claude or Codex CLI")
    if task_role == "component":
        binding, record, attachment = owner.component_context(task)
        if record["state"] != "launching" or record["harness"] != harness:
            raise GroupError("component relaunch is unsupported; preserve the existing request")
        if (owner.home / "state" / f"{task}.meta").exists():
            raise GroupError("component metadata already exists; duplicate launch refused")
        owner.caller_meta(binding["parent"], binding["accepted_parent_gen"])
    else:
        attachment = owner.attachment(task)
    delivery = root_delivery(attachment) if task_role == "root" else None
    expected_kind, expected_mode = ("ship", "local-only") if delivery else ("scout", "")
    if (kind, mode) != (expected_kind, expected_mode):
        raise GroupError("launch kind or mode differs from immutable root/component delivery")
    project = safe_path(project, directory=True)
    if str(project) != attachment["project"]:
        raise GroupError("launch project differs from immutable attachment")
    clean_commit(project, attachment["input_commit"])
    if worktree:
        worktree = safe_path(worktree, directory=True)
        if worktree == project:
            raise GroupError("task-group worker requires its own isolated worktree")
        if task_role == "root":
            # Ordinary ship briefs create fm/<id> as the worker's first action.
            # Fresh spawn therefore validates the detached admitted input; an
            # existing root must already retain its promised delivery branch.
            published = (owner.home / "state" / f"{task}.meta").exists()
            if published:
                validate_root_worktree({"worktree": str(worktree)}, attachment)
            else:
                validate_root_launch_worktree({"worktree": str(worktree)}, attachment)
        if task_role == "component":
            clean_commit(worktree, record.get("input_commit", attachment["input_commit"]))
        elif not (is_dynamic(attachment) and (owner.home / "state" / f"{task}.meta").exists()):
            clean_commit(worktree, attachment["input_commit"])


def launch_position(owner, task, worktree):
    """Position fresh dynamic workers through the existing spawn transaction.

    The call site is after isolation/freshening and before launch-check or metadata
    publication. Existing roots retain their joined and dirty work on relaunch.
    """
    task_role = role(owner, task)
    if not task_role:
        return
    binding = None
    if task_role == "component":
        binding, record, attachment = owner.component_context(task)
    else:
        attachment = owner.attachment(task)
    if not is_dynamic(attachment):
        return
    published = (owner.home / "state" / f"{task}.meta").exists()
    if task_role == "root":
        if published:
            return
        input_commit = attachment["input_commit"]
        parent_worktree = None
    else:
        parent, _ = owner.caller_meta(binding["parent"], binding["accepted_parent_gen"])
        if record["state"] != "launching" or published:
            raise GroupError("only a fresh launching component may be positioned")
        input_commit = record["input_commit"]
        parent_worktree = safe_path(parent["worktree"], directory=True)
    worktree = safe_path(worktree, directory=True)
    project = safe_path(attachment["project"], directory=True)
    if worktree in (project, parent_worktree):
        raise GroupError("worker positioning requires its own worktree")
    top = safe_path(git(worktree, "rev-parse", "--show-toplevel"), directory=True)
    common = safe_path(git(worktree, "rev-parse", "--path-format=absolute", "--git-common-dir"), directory=True)
    project_common = safe_path(git(project, "rev-parse", "--path-format=absolute", "--git-common-dir"), directory=True)
    if top != worktree or common != project_common:
        raise GroupError("worker positioning requires an isolated worktree of the attached repository")
    clean_commit(worktree)
    if task_role == "root":
        clean_commit(project, attachment["input_commit"])
        if git(worktree, "symbolic-ref", "--quiet", "--short", "HEAD", accepted=(0, 1)):
            raise GroupError("fresh root positioning requires a detached worktree")
        verify_position(owner, {"root": task}, project, worktree)
    else:
        verify_position(owner, binding, project, worktree)
    git(worktree, "reset", "--hard", input_commit)
    clean_commit(worktree, input_commit)


def verify_position(owner, binding, project, worktree):
    """Ask the existing shell owners to prove this spawn's locks and pool claim."""
    arguments = (["--verify-root-position", binding["root"], str(project), str(worktree)]
                 if "root" in binding else
                 ["--verify-position", binding["parent"], binding["accepted_parent_gen"],
                  binding["child"], str(project), str(worktree)])
    result = owner.runtime.run(
        owner.code_root / "bin" / "fm-task-group-spawn.sh", arguments,
        env=owner.runtime.environment(home=owner.home, code_root=owner.code_root),
        capture_output=True, timeout=10, check=False)
    if result.returncode:
        raise GroupError("worker positioning requires current spawn custody and its own Treehouse slot")


def launch_meta(owner, task):
    task_role = role(owner, task)
    if not task_role:
        return ""
    fields = {"task_group_role": task_role, "task_group_epoch": "1"}
    if task_role == "component":
        binding, record, attachment = owner.component_context(task)
        fields.update(task_group_parent=binding["parent"], task_group_request=binding["request_id"],
                      task_group_hash=binding["body_hash"], result_disposition="parent")
    else:
        attachment = owner.attachment(task)
    if task_role == "root" and root_delivery(attachment):
        fields["task_group_delivery"] = LOCAL_DELIVERY
    primitive = (component_primitive(record, attachment) if task_role == "component"
                 else attachment_primitive(attachment))
    if primitive == "Review" or is_dynamic(attachment):
        fields["task_group_primitive"] = primitive
    if is_dynamic(attachment):
        fields["task_group_workflow"] = "dynamic"
        if task_role == "component":
            fields["task_group_writable"] = str(record["writable"]).lower()
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
    if component_primitive(record, attachment) == "Review":
        return ("# Task\n\n## Captain's intent\n\n"
                f"Return one independent read-only Review result to FirstMate root {binding['parent']}.\n\n"
                "## Firstmate spec\n\n"
                f"{record['body']['assignment']}\n\n"
                + component_overlay(owner, binding, attachment, record))
    if record.get("writable") is True:
        return ("# Task\n\n## Captain's intent\n\n"
                f"Return one scoped Work implementation to FirstMate root {binding['parent']}.\n\n"
                "## Firstmate spec\n\n"
                f"{record['body']['assignment']}\n\n"
                f"Start from this component's input commit {record['input_commit']}. "
                "Make and check only the assigned changes in your isolated worktree. "
                "Commit the complete result with ordinary Git, leaving the worktree clean. "
                "Do not change the parent worktree or attached package. Your output commit is retained "
                "for the root to inspect and cherry-pick; it does not deliver or merge the root task.\n\n"
                + component_overlay(owner, binding, attachment, record))
    return ("# Task\n\n## Captain's intent\n\n"
            f"Return one read-only Work result to FirstMate root {binding['parent']}.\n\n"
            "## Firstmate spec\n\n"
            f"{record['body']['assignment']}\n\n"
            f"Inspect only this component's worktree at input commit {record.get('input_commit', attachment['input_commit'])}. "
            "Do not change project files, dependencies, Git state or the attached package. "
            "Use the assigned package's relevant Make guidance; no native children, fleet children, "
            "or independent review are authorized. Include evidence, file references and remaining gaps.\n\n"
            + component_overlay(owner, binding, attachment, record))


def component_overlay(owner, binding, attachment, record=None):
    if record is None:
        _, record, _ = owner.component_context(binding["child"])
    child = binding["child"]
    review_contract = ""
    if component_primitive(record, attachment) == "Review":
        review_contract = (
            "This is an explicitly authorized independent audit by a fresh Review component. "
            f"Review only this component's worktree at frozen input commit {record.get('input_commit', attachment['input_commit'])}. "
            "Apply the assigned package's relevant Review guidance. Report findings with evidence, "
            "file references and remaining gaps; do not make or delegate repairs. "
            "Do not change project files, dependencies, Git state or the attached package.\n")
    delegated = (record.get("writable") is True and binding["parent"] == attachment["root"]
                 and caller_calls(attachment, binding["request_id"]))
    delegation = ("Use only the Work/Review calls authorized below through the attached client; "
                  "direct fleet commands remain unavailable.\n" if delegated else
                  "Do not invoke Work or Review or another fleet command.\n")
    return ("# FirstMate task-group component completion contract\n\n"
            f"Role: component; disposition: return evidence to parent {binding['parent']}; "
            f"request {binding['request_id']}; attachment epoch 1.\n"
            + review_contract +
            "This component contract governs completion. Do not write ordinary scout done status, "
            "deliver to the captain, open a PR, merge, promote, run no-mistakes, or complete the parent. "
            + delegation +
            f"The immutable package is {attachment['package_path']} (SHA-256 {attachment['package_digest']}). "
            f"You may read your worktree, that package, your brief, and your metadata at "
            f"{owner.home / 'state' / (child + '.meta')}.\n"
            "Read the exact spawn_gen and tasktmp values from that metadata. Write a nonempty UTF-8 "
            "report within the recorded tasktmp directory, then invoke:\n\n"
            f"    {command_prefix(owner)} complete {shlex.quote(child)} --generation CURRENT_SPAWN_GEN --report ABSOLUTE_REPORT_PATH\n\n"
            "Replace the two argument values from your actual metadata/report. A busy group can be "
            "retried with the same generation and same report. Success requires a retained complete result; "
            "process exit, a transcript message or ordinary done status does not complete this assignment. "
            "After the controller accepts the report, stop work and leave cleanup to FirstMate.\n"
            + (composition_overlay(owner, child, attachment, binding["request_id"]) if delegated else ""))


def composition_overlay(owner, task, attachment, caller_request=None):
    authorized = caller_calls(attachment, caller_request)
    if not authorized:
        return ""
    package = Path(attachment["package_path"])
    client = python_command(owner, package / "scripts/firstmate.py")
    listing = ", ".join(call["id"] for call in authorized)
    return ("\n# Authorized caller-context composition\n\n"
            f"Your authorized dynamic workflow_call IDs, in order, are: {listing}. "
            "Loading a workflow's instructions stays in this context; only Work or Review creates an agent. "
            "Every request selects its workflow_call. Each call gathers and joins its Work, requests one fresh "
            "read-only Review, then gathers that Review and performs one repair/check pass. Never repeat a "
            "call's Review; another declared call starts its own bounded dynamic phase. "
            "Finish and gather a phase before beginning the next declared phase. "
            "The whole group, including descendants, shares the 32-request capacity. "
            "Only writable root Work request IDs named as callers in the immutable selected composition "
            "may delegate one level through this same client. Review and read-only components do not delegate. "
            "All descendant results must be read and gathered and their declared calls finished before "
            "returning this component's result. FirstMate owns every launch and lifecycle action.\n"
            f"Use ORCHFLOWS_FIRSTMATE_CONTEXT from your own launch with {client} status, submit --request "
            "REQUEST_JSON_PATH, and gather --request-id REQUEST_ID. "
            "Put request files in your recorded tasktmp, commit your current clean worktree before new Work/Review, "
            "and join retained writer commits into your own worktree.\n")


def launch_overlay(owner, task):
    task_role = role(owner, task)
    if not task_role:
        return ""
    if task_role == "component":
        binding, record, attachment = owner.component_context(task)
        return component_overlay(owner, binding, attachment, record)
    attachment = owner.attachment(task)
    package = Path(attachment["package_path"])
    # The launch owner supplies an immutable current-generation context.
    client = python_command(owner, package / "scripts" / "firstmate.py")
    from fm_orchflows import library_overlay, supports_launch_context
    libraries = library_overlay(attachment)
    if supports_launch_context(package):
        invocation_note = ("The client uses ORCHFLOWS_FIRSTMATE_CONTEXT supplied by this launch; "
                           "do not add authority flags. ")
    else:
        # Retained older packages must keep their original explicit CLI contract.
        code = owner.code_root.as_posix() if owner.runtime.windows else str(owner.code_root)
        home = owner.home.as_posix() if owner.runtime.windows else str(owner.home)
        client += (" --firstmate-root " + shlex.quote(code) + " --home " + shlex.quote(home) +
                   " --root " + shlex.quote(task) + " --generation CURRENT_SPAWN_GEN --timeout 420")
        if attachment_primitive(attachment) == "Review":
            client += " --primitive Review"
        invocation_note = ("This retained client uses explicit arguments. Read the current spawn_gen "
                           "from your metadata before each call and replace CURRENT_SPAWN_GEN below. ")
    if is_dynamic(attachment):
        return (dynamic_root_overlay(owner, task, attachment, client, invocation_note)
                + (composition_overlay(owner, task, attachment) if attachment.get("composition") else "")
                + libraries)
    if attachment_primitive(attachment) == "Review":
        return review_root_overlay(owner, task, attachment, client, invocation_note) + libraries
    windows_note = ("On native Windows, pass a native absolute request path to the package client; "
                    "use cygpath -m to convert a recorded MSYS tasktmp path. " if owner.runtime.windows else "")
    return ("# FirstMate task-group root attachment\n\n"
            f"You remain a normal root scout. The attached orchflows-firstmate package is "
            f"{attachment['package_path']} (SHA-256 {attachment['package_digest']}), epoch 1. "
            f"The fixed read-only input commit is {attachment['input_commit']}. "
            "Stage 1 permits exactly one read-only Work component under FirstMate/Herdr; "
            "Review, writers, nesting and native-child fallback are unavailable.\n"
            f"Read and apply the exact attached Work skill at {package / 'skills' / 'orch-work' / 'SKILL.md'}. "
            f"Read your tasktmp from {owner.home / 'state' / (task + '.meta')}. "
            + invocation_note +
            "Place the request JSON and all transient files inside your recorded tasktmp directory, "
            "keeping the project worktree clean. The request contains only request_id and assignment. "
            + windows_note +
            "Invoke the attached fork client with the absolute request path:\n\n"
            f"    {client} submit --request REQUEST_JSON_PATH\n"
            f"    {client} status\n"
            f"    {client} gather\n\n"
            "A replay uses the same request ID and exact body. After relaunch, reconcile the saved request "
            "with your current generation; do not create a replacement component. A launching or uncertain "
            "request stays unresolved until FirstMate reconciles it. Read the complete retained report and "
            "identity before gather acknowledges receipt. While waiting, keep the join pending; do not "
            "mark done or paused for a person. Once gathered, incorporate evidence into your normal scout "
            f"report at {owner.home / 'data' / task / 'report.md'} and follow FirstMate's ordinary outer completion.\n" + libraries)


def review_root_overlay(owner, task, attachment, client, invocation_note):
    package = Path(attachment["package_path"])
    return ("# FirstMate task-group root attachment\n\n"
            "You remain a normal root scout with one explicitly authorized independent audit. "
            f"The attached orchflows-firstmate package is {package} "
            f"(SHA-256 {attachment['package_digest']}), epoch 1. "
            f"The frozen read-only input commit is {attachment['input_commit']}. "
            "The admission policy is Review/explicit-audit: exactly one fresh read-only reviewer "
            "under FirstMate/Herdr. Work, writers, repairs, nesting, additional components and "
            "native-child fallback are unavailable.\n"
            f"Read and apply the exact attached Review skill at {package / 'skills' / 'orch-review' / 'SKILL.md'}. "
            f"Read your tasktmp from {owner.home / 'state' / (task + '.meta')}. "
            + invocation_note +
            "Place the request JSON and transient files in that tasktmp, keeping your worktree clean. "
            "The request contains only request_id and assignment; the immutable attachment selects Review. "
            "Describe the audit target and relevant Review guidance in the assignment. "
            "Invoke the attached fork client with the absolute request path:\n\n"
            f"    {client} submit --request REQUEST_JSON_PATH\n"
            f"    {client} status\n"
            f"    {client} gather\n\n"
            "Replay the same request ID and exact body. After relaunch reconcile that saved request "
            "under your current generation; never create a replacement reviewer. A launching or uncertain "
            "request remains unresolved until FirstMate reconciles it. Read the complete retained report "
            "and result identity before gather acknowledges receipt. Keep the join pending while waiting; "
            "do not mark done or paused for a person. Once gathered, include the audit findings, exact "
            "reviewed commit, reviewer identity and remaining gaps in your normal scout report at "
            f"{owner.home / 'data' / task / 'report.md'}, then follow FirstMate's ordinary outer completion. "
            "Findings authorize no repair pass or additional review in this bounded audit.\n")


def dynamic_root_overlay(owner, task, attachment, client, invocation_note):
    package = Path(attachment["package_path"])
    delivery = root_delivery(attachment)
    opening = ("You remain a normal local-only ship root delivering committed output on "
               f"{delivery['branch']} through FirstMate's ordinary ready-branch contract. "
               "On first launch create that branch as the ordinary brief directs before invoking "
               "client status or submission. On relaunch preserve the existing branch. "
               if delivery else "You remain a normal root scout with ordinary FirstMate report delivery. ")
    completion = ("Keep the complete result committed and clean on " + delivery["branch"] +
                  ". Follow the brief's local-only definition of done: append done: ready in branch " +
                  delivery["branch"] + " to your recorded status file and stop. FirstMate's existing merge "
                  "authority and fm-merge-local owner land it. Do not merge, push or open a PR. "
                  "Keep diagnostic reports in your recorded tasktmp when requested.\n" if delivery else
                  "Deliver those custom requirements together with the resulting evidence, joined commit, review "
                  "identity, repair/check outcome and remaining gaps in your normal scout report at "
                  f"{owner.home / 'data' / task / 'report.md'}, then follow ordinary root completion.\n")
    return ("# FirstMate task-group dynamic root attachment\n\n"
            + opening + "The explicitly selected workflow is dynamic with workflow-review policy. "
            f"The immutable package is {package} (SHA-256 {attachment['package_digest']}). "
            f"Read and apply {package / 'skills' / 'orch-dynamic-workflow' / 'SKILL.md'}, "
            f"{package / 'skills' / 'orch-work' / 'SKILL.md'} and "
            f"{package / 'skills' / 'orch-review' / 'SKILL.md'}. "
            "For a requested custom workflow, on initial launch and every relaunch read the full selected "
            "retained custom skill before continuing. Reapply its deliverable and validation requirements "
            "to the retained results and remaining work; it composes these same primitives.\n"
            + invocation_note +
            f"Use your recorded tasktmp from {owner.home / 'state' / (task + '.meta')} for request files. "
            "Every request JSON has request_id, assignment, primitive (Work or Review), "
            "and writable (a JSON boolean). With negotiated assignment controls, optional model, effort, "
            "assignment_name and operation_defaults resolve independently through FirstMate. "
            "Selected compositions additionally use workflow_call. "
            "Work may write when scoped and useful; Review requires writable=false. "
            "Each new request freezes your current clean worktree HEAD. Commit your own changes before submitting. "
            f"The group permits at most {attachment['max_components']} component requests.\n\n"
            f"    {client} status\n"
            f"    {client} submit --request REQUEST_JSON_PATH\n"
            f"    {client} status --request-id REQUEST_ID\n"
            f"    {client} gather --request-id REQUEST_ID\n\n"
            "Status without an ID lists all retained requests. Ready independent Work requests may run together. "
            "Replay only the same request ID and exact body; an uncertain launch cannot authorize a replacement. "
            "FirstMate owns every child, workspace, endpoint, notice, recovery and cancellation. "
            "No native children or direct fleet commands are authorized. "
            "Descendant Work/Review requires the selected composition's explicit caller scope.\n"
            "For each request, run status --request-id REQUEST_ID and read the complete files at the exact "
            "top-level report_path and result_path returned by that response before gathering the request. "
            "The result's component_meta.tasktmp and component_meta.worktree record provenance; they are not "
            "the parent's retained report locations. Do not reconstruct component scratch paths or broaden "
            "permissions. If the retained paths are absent or unavailable, keep the request pending and "
            "reconcile through FirstMate's existing owner before continuing. For writing Work, "
            "inspect the retained input_commit and output_commit and join the complete input_commit..output_commit "
            "commit range in dependency order using ordinary Git cherry-pick in your own FirstMate "
            "worktree; include every maker commit, resolve conflicts there and record the join. "
            "Gather acknowledges receipt and does not join commits. Preserve accepted results and existing "
            "joined or dirty work after relaunch; inspect status and reread any selected retained custom skill "
            "before resuming its remaining deliverables and validation.\n"
            "After gathering all earlier Work results and joining and checking the exact clean candidate, "
            "request one fresh independent read-only Review for that dynamic call. Then gather it and perform "
            "one repair/check pass, using scoped repair Work if useful or repairing directly. Do not request "
            "another Review for the same call or repeat its review/repair cycle. Never wait for repeated clean verdicts. "
            "Once no-mistakes validation starts it alone owns review, fixes, tests, documentation, push, PR and CI; "
            "this selected workflow does not start or replace that pipeline. FirstMate self-development is refused.\n"
            "Keep unfinished joins pending while FirstMate supervises; do not mark done or paused for a person. "
            "Component completion returns only to you. Before ordinary root completion, reread any selected "
            "retained custom skill and verify its required report content, artifacts and checks are satisfied. "
            + completion)
