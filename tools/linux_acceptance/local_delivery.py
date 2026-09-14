"""Local-only acceptance at FirstMate's existing branch, landing and cleanup owners."""
import hashlib
import json
from pathlib import Path

from .runtime import metadata

BEHAVIOR = (
    "from stock import has_stock; from labels import label_key; "
    "assert not has_stock([]); assert not has_stock([0,0]); assert has_stock([0,3]); "
    "assert label_key(' ab-7 ')=='AB_7'; assert label_key('')==''"
)


def _git(trial, project, *args):
    return trial.run(["git", "-C", project, *args], check=False)


def _extend(result, checks):
    result["acceptance"]["checks"].update(checks)
    result["acceptance"]["passed"] = all(result["acceptance"]["checks"].values())


def collect_ready(trial, result, project):
    """Require an actual clean ready branch before attempting the fixture landing."""
    parent = metadata(trial.owner_home / "state" / (trial.root + ".meta"))
    worktree = Path(parent.get("worktree", "/nonexistent"))
    expected_branch = "fm/" + trial.root
    attachment_path = trial.owner_home / "data" / trial.root / "task-group/attachment.json"
    attachment = json.loads(attachment_path.read_text()) if attachment_path.is_file() else {}
    status = trial.owner_home / "state" / (trial.root + ".status")
    lines = status.read_text().splitlines() if status.is_file() else []
    current = _git(trial, worktree, "symbolic-ref", "--quiet", "--short", "HEAD")
    head = _git(trial, worktree, "rev-parse", "--verify", "HEAD")
    branch = _git(trial, project, "rev-parse", "--verify", "refs/heads/" + expected_branch)
    clean = _git(trial, worktree, "status", "--porcelain")
    ancestry = _git(trial, project, "merge-base", "--is-ancestor", "main", expected_branch)
    checks = {
        "ordinary_ship_local_only_metadata": (
            parent.get("kind") == "ship" and parent.get("mode") == "local-only"
            and parent.get("task_group_role") == "root" and parent.get("yolo") == "on"),
        "immutable_local_delivery_attachment": attachment.get("root_delivery") == {
            "kind": "ship", "mode": "local-only", "branch": expected_branch}
            and parent.get("task_group_delivery") == "ship-local-only",
        "exact_ready_branch_signal": bool(lines) and lines[-1] == "done: ready in branch " + expected_branch,
        "committed_on_expected_branch": current.returncode == 0 and current.stdout.strip() == expected_branch
            and head.returncode == 0 and branch.returncode == 0
            and head.stdout.strip() == branch.stdout.strip() == result.get("final_commit"),
        "ready_branch_clean_fast_forward": clean.returncode == 0 and clean.stdout == "" and ancestry.returncode == 0,
        "components_return_to_parent": len(result.get("retained_results", {})) == 3 and all(
            value.get("component_meta", {}).get("kind") == "scout"
            and value.get("component_meta", {}).get("result_disposition") == "parent"
            for value in result.get("retained_results", {}).values()),
    }
    if getattr(trial.args, "restart", False):
        replacement = result.get("replacement", {})
        checks["local_delivery_survived_relaunch"] = replacement.get("delivery_before") == {
            "kind": "ship", "mode": "local-only", "task_group_delivery": "ship-local-only"} and (
            attachment_path.is_file() and replacement.get("attachment_before") ==
            hashlib.sha256(attachment_path.read_bytes()).hexdigest())
    result["local_delivery"] = {
        "branch": expected_branch, "ready_commit": head.stdout.strip() if head.returncode == 0 else None,
        "root_status": lines[-1] if lines else "", "landed": False,
    }
    _extend(result, checks)


def land(trial, result, project):
    """The private fixture uses yolo=on; no user project merge is performed."""
    if not result["acceptance"]["passed"]:
        return
    final = result["final_commit"]
    before = _git(trial, project, "rev-parse", "--verify", "refs/heads/main")
    merge = trial.owner("fm-merge-local.sh", trial.root, env=trial.worker_env, timeout=90, check=False)
    trial.write(trial.out / "local-landing.log", merge.stdout + merge.stderr)
    after = _git(trial, project, "rev-parse", "--verify", "refs/heads/main")
    dirty = _git(trial, project, "status", "--porcelain")
    landed = (merge.returncode == 0 and before.returncode == 0 and after.returncode == 0
              and before.stdout.strip() == trial.receipt["input_commit"]
              and after.stdout.strip() == final and dirty.returncode == 0 and dirty.stdout == "")
    result["local_delivery"].update(
        merge_exit=merge.returncode, default_before=before.stdout.strip(), default_after=after.stdout.strip(),
        landed=landed)
    _extend(result, {"ordinary_local_landing": landed})


def check_landed_after_cleanup(trial):
    """Verify delivered code after the ordinary task cleanup has removed scratch work."""
    project = trial.namespace / "project"
    for result in trial.receipt.get("runs", []):
        final = result.get("final_commit")
        head = _git(trial, project, "rev-parse", "--verify", "refs/heads/main")
        clean = _git(trial, project, "status", "--porcelain")
        env = {key: value for key, value in trial.env.items() if key != "CLAUDE_CODE_OAUTH_TOKEN"}
        behavior = trial.run(["python3", "-B", "-c", BEHAVIOR], env=env, cwd=project, check=False)
        tests = trial.run(["python3", "-B", "-m", "unittest", "discover", "-v"],
                          env=env, cwd=project, check=False)
        trial.write(trial.out / "landed-tests-after-cleanup.log", tests.stdout + tests.stderr)
        checks = {
            "landed_exact_final_commit": bool(result.get("local_delivery", {}).get("landed"))
                and bool(final) and head.returncode == 0 and head.stdout.strip() == final,
            "landed_checkout_clean": clean.returncode == 0 and clean.stdout == "",
            "landed_behavior_and_tests": behavior.returncode == 0 and tests.returncode == 0
                and "Ran 0 tests" not in tests.stderr,
            "root_metadata_removed": not (trial.owner_home / "state" / (trial.root + ".meta")).exists(),
        }
        result["delivery_after_cleanup"] = {"passed": all(checks.values()), "checks": checks}
        trial.receipt["cleanup_passed"] &= all(checks.values())
