"""A scratch writer result must not pass ordinary local-only delivery acceptance."""
from argparse import Namespace
from contextlib import contextmanager
import json
from pathlib import Path
import tempfile
import unittest

from .dynamic import DynamicTrial
from .local_delivery import collect_ready, land, check_landed_after_cleanup


class LocalDeliveryChecks(unittest.TestCase):
    @contextmanager
    def fixture(self):
        with tempfile.TemporaryDirectory(prefix="local-delivery-", dir="/tmp") as directory:
            base = Path(directory)
            trial = DynamicTrial.__new__(DynamicTrial)
            trial.namespace, trial.out, trial.owner_home = base, base / "evidence", base / "fm"
            trial.root, trial.args = "root", Namespace(local_only=True)
            trial.secrets = []
            trial.env = {"PATH": "/usr/bin:/bin", "HOME": str(base), "PYTHONDONTWRITEBYTECODE": "1",
                         "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null"}
            for name in ("home", "evidence", "fm/state", "fm/data/root/task-group", "project"):
                (base / name).mkdir(parents=True, exist_ok=True)
            project, worktree = base / "project", base / "worktree"
            def git(*args, cwd=project):
                return trial.run(["git", "-C", cwd, *args]).stdout.strip()
            git("init", "-b", "main")
            git("config", "user.name", "Fixture")
            git("config", "user.email", "fixture@example.invalid")
            (project / "initial").write_text("input")
            git("add", ".")
            git("commit", "-qm", "input")
            initial = git("rev-parse", "HEAD")
            git("worktree", "add", "-b", "fm/root", worktree)
            (worktree / "stock.py").write_text("def has_stock(counts): return sum(counts)>0\n")
            (worktree / "labels.py").write_text("def label_key(value): return value.strip().upper().replace('-', '_')\n")
            (worktree / "test_stock.py").write_text(
                "import unittest\nfrom stock import has_stock\nclass Stock(unittest.TestCase):\n"
                " def test_stock(self): self.assertTrue(has_stock([1]))\n")
            git("add", ".", cwd=worktree)
            git("commit", "-qm", "maker output", cwd=worktree)
            final = git("rev-parse", "HEAD", cwd=worktree)
            meta = (trial.owner_home / "state/root.meta")
            meta.write_text("kind=ship\nmode=local-only\nyolo=on\ntask_group_role=root\n"
                            "task_group_delivery=ship-local-only\nworktree=" + str(worktree) + "\n")
            status = trial.owner_home / "state/root.status"
            status.write_text("done: ready in branch fm/root\n")
            attachment = trial.owner_home / "data/root/task-group/attachment.json"
            attachment.write_text(json.dumps({"root_delivery": {
                "kind": "ship", "mode": "local-only", "branch": "fm/root"}}))
            result = {"final_commit": final, "acceptance": {"passed": True, "checks": {"composition": True}},
                      "retained_results": {str(i): {"component_meta": {"kind": "scout", "result_disposition": "parent"}}
                                           for i in range(3)}}
            trial.receipt = {"input_commit": initial, "runs": [result], "cleanup_passed": True}
            yield trial, result, project, worktree, git

    def test_exact_branch_delivery_passes_and_scout_done_cannot_substitute(self):
        with self.fixture() as (trial, result, project, worktree, git):
            collect_ready(trial, result, project)
            self.assertTrue(result["acceptance"]["passed"], result)
            (trial.owner_home / "state/root.status").write_text("done: report completed\n")
            collect_ready(trial, result, project)
            self.assertFalse(result["acceptance"]["checks"]["exact_ready_branch_signal"])

    def test_wrong_branch_dirty_tree_and_mode_mutation_refuse(self):
        with self.fixture() as (trial, result, project, worktree, git):
            git("switch", "-c", "scratch", cwd=worktree)
            (worktree / "uncommitted").write_text("unfinished")
            meta = trial.owner_home / "state/root.meta"
            meta.write_text(meta.read_text().replace("mode=local-only", "mode=no-mistakes"))
            collect_ready(trial, result, project)
            self.assertFalse(result["acceptance"]["passed"])
            for key in ("ordinary_ship_local_only_metadata", "committed_on_expected_branch",
                        "ready_branch_clean_fast_forward"):
                self.assertFalse(result["acceptance"]["checks"][key], key)

    def test_failed_composition_never_invokes_local_merge(self):
        with self.fixture() as (trial, result, project, worktree, git):
            result["acceptance"]["checks"]["composition"] = False
            collect_ready(trial, result, project)
            calls = []
            trial.owner = lambda *args, **kwargs: calls.append(args)
            land(trial, result, project)
            self.assertEqual(calls, [])
            self.assertEqual(git("rev-parse", "main"), trial.receipt["input_commit"])

    def test_writer_scratch_does_not_certify_landed_code_after_cleanup(self):
        with self.fixture() as (trial, result, project, worktree, git):
            collect_ready(trial, result, project)
            # Even a forged landing claim cannot hide main still containing only the input.
            result["local_delivery"]["landed"] = True
            (trial.owner_home / "state/root.meta").unlink()
            check_landed_after_cleanup(trial)
            self.assertFalse(trial.receipt["cleanup_passed"])
            checks = result["delivery_after_cleanup"]["checks"]
            self.assertFalse(checks["landed_exact_final_commit"])
            self.assertFalse(checks["landed_behavior_and_tests"])
            # Fixture-only fast-forward demonstrates the exact state the observer requires.
            git("merge", "--ff-only", "fm/root")
            trial.receipt["cleanup_passed"] = True
            check_landed_after_cleanup(trial)
            self.assertTrue(result["delivery_after_cleanup"]["passed"])
            self.assertTrue(trial.receipt["cleanup_passed"])
