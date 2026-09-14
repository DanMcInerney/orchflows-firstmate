"""Bind selected root delivery to FirstMate's existing kind, mode and Git branch."""
from pathlib import Path

from fm_task_group_store import GroupError, clean_commit, clean_descendant, git, safe_path

LOCAL_DELIVERY = "ship-local-only"


def local_delivery(root):
    return {"kind": "ship", "mode": "local-only", "branch": "fm/" + root}


def root_delivery(attachment):
    value = attachment.get("root_delivery")
    if value is not None and (attachment.get("workflow") != "dynamic" or
                              value != local_delivery(attachment["root"])):
        raise GroupError("unsupported immutable root delivery identity")
    return value


def validate_root_metadata(value, attachment):
    delivery = root_delivery(attachment)
    kind, mode = ("ship", "local-only") if delivery else ("scout", "")
    if value.get("kind") != kind or value.get("mode", "") != mode:
        raise GroupError("root kind or mode differs from immutable delivery; no-mistakes owns validation once selected")
    expected = LOCAL_DELIVERY if delivery else None
    if value.get("task_group_delivery") != expected:
        raise GroupError("root metadata delivery differs from immutable attachment")


def validate_root_worktree(value, attachment, *, clean=False, branch=True):
    delivery = root_delivery(attachment)
    if not delivery:
        return
    worktree = safe_path(value.get("worktree", ""), directory=True)
    project = safe_path(attachment["project"], directory=True)
    top = safe_path(git(worktree, "rev-parse", "--show-toplevel"), directory=True)
    common = safe_path(git(worktree, "rev-parse", "--path-format=absolute", "--git-common-dir"), directory=True)
    expected_common = safe_path(git(project, "rev-parse", "--path-format=absolute", "--git-common-dir"), directory=True)
    if worktree == project or top != worktree or common != expected_common:
        raise GroupError("local-only root requires its own worktree of the attached repository")
    if branch and git(worktree, "symbolic-ref", "--quiet", "--short", "HEAD", accepted=(0, 1)) != delivery["branch"]:
        raise GroupError("root worktree branch differs from immutable delivery identity")
    if clean:
        clean_descendant(worktree, attachment["input_commit"])


def validate_root_launch_worktree(value, attachment):
    """Allow only the ordinary pristine detached start before fm-brief branches."""
    delivery = root_delivery(attachment)
    if not delivery:
        return
    validate_root_worktree(value, attachment, branch=False)
    worktree = value["worktree"]
    branch = git(worktree, "symbolic-ref", "--quiet", "--short", "HEAD", accepted=(0, 1))
    if branch == delivery["branch"]:
        return
    if branch or git(worktree, "rev-parse", "--verify", "--quiet",
                     "refs/heads/" + delivery["branch"], accepted=(0, 1)):
        raise GroupError("root launch requires its delivery branch or pristine detached input before branch creation")
    clean_commit(worktree, attachment["input_commit"])


def delivery_check(owner, task, *, landing=False, teardown=False, reassigned=False):
    from fm_task_group_launch import role
    task_role = role(owner, task)
    if not task_role:
        return
    if task_role != "root":
        raise GroupError("components return to parent; root delivery or component relaunch is unavailable")
    current = owner.meta(task)
    current, attachment = owner.root_meta(task, current.get("spawn_gen", ""), check_worktree=not teardown)
    if landing and not root_delivery(attachment):
        raise GroupError("attachment does not authorize local-only root delivery")
    if teardown:
        # The shell owner independently proves the retained delivery ref landed,
        # or validates its own exact-generation pre-cleanup completion marker.
        # Returned workspaces can be detached or missing. A reassigned Treehouse
        # slot is inspected only by its current owner, as ordinary teardown does.
        worktree = safe_path(current.get("worktree", ""), directory=True, exists=False)
        if worktree.exists() and not reassigned:
            validate_root_worktree(current, attachment, branch=False)
    else:
        validate_root_worktree(current, attachment, clean=landing)
