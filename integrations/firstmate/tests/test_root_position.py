"""Fresh root positioning after local-only delivery, using actual Git and lock owners."""
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

import test_task_group as fixtures
from fm_task_group_delivery import local_delivery
from fm_task_group_launch import launch_position
from fm_task_group_store import GroupError, clean_commit, git


class RootPositionTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.ControllerTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.owner = self.fixture.owner
        self.project = self.fixture.project
        self.base = self.fixture.base
        self.candidate = Path(os.environ["FM_STAGE1_FIRSTMATE_ROOT"])
        self.fixture.git("branch", "-M", "main")
        self.initial = clean_commit(self.project)
        self.remote = self.base / "origin.git"
        subprocess.run(["git", "clone", "--bare", "-q", str(self.project), str(self.remote)], check=True)
        self.fixture.git("remote", "add", "origin", str(self.remote))
        self.fixture.git("fetch", "-q", "origin")
        self.fixture.git("symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main")
        (self.project / "delivered.txt").write_text("Locally landed output without a push.\n")
        self.fixture.git("add", "delivered.txt")
        self.fixture.git("commit", "-qm", "local-only delivery")
        self.delivered = clean_commit(self.project)
        self.fixture.package.joinpath("scripts/firstmate-client.json").write_text(json.dumps(
            {"schema": 1, "launch_context_schema": 1, "workflows": ["dynamic"],
             "root_deliveries": ["ship-local-only"]}))
        self.attachment = self.owner.attach("fresh", self.fixture.package, self.project,
                                            "Work", "workflow-review", workflow="dynamic",
                                            delivery=local_delivery("fresh"))
        self.pool = self.base / "pool"
        self.slot = self.pool / "slot" / "project"
        self.slot.parent.mkdir(parents=True)
        (self.pool / "treehouse-state.json").write_text("{}")
        self.fixture.git("worktree", "add", "--detach", str(self.slot), self.initial)
        self.owner.code_root = self.candidate

    def run_position(self, scenario="owned"):
        shell = r"""
set -eu
. "$CODE/bin/fm-backend.sh"
. "$CODE/bin/fm-wake-lib.sh"
spawnlock="$FM_HOME/state/.spawn-fresh.lock"
projectlock=$(fm_treehouse_project_lock_path "$PROJECT")
held=()
cleanup() { for lock in "${held[@]}"; do fm_lock_release "$lock" || true; done; }
trap cleanup EXIT
if [ "$SCENARIO" != missing-project ]; then
  fm_lock_try_acquire "$projectlock"
  held+=("$projectlock")
fi
if [ "$SCENARIO" != missing-spawn ]; then
  fm_lock_try_acquire "$spawnlock"
  held+=("$spawnlock")
fi
claim=fresh
[ "$SCENARIO" != wrong-claim ] || claim=other-task
fm_treehouse_slot_owner_claim "$SLOT" "$claim" "$FM_HOME"
"$PYTHON" -B "$CODE/bin/fm-task-group.py" --home "$FM_HOME" launch-position fresh --worktree "$SLOT"
"$PYTHON" -B "$CODE/bin/fm-task-group.py" --home "$FM_HOME" launch-check fresh \
  --kind ship --mode local-only --backend herdr --harness claude --project "$PROJECT" --worktree "$SLOT"
"""
        env = {key: value for key, value in os.environ.items()
               if not key.startswith(("FM_", "HERDR_", "ORCHFLOWS_"))}
        env.update(CODE=str(self.candidate), FM_HOME=str(self.owner.home), PROJECT=str(self.project),
                   SLOT=str(self.slot), PYTHON=sys.executable, SCENARIO=scenario)
        return subprocess.run(["bash", "-c", shell], env=env, capture_output=True, text=True, timeout=30)

    def test_fresh_local_root_starts_from_attached_local_tip_ahead_of_origin(self):
        # This is the state produced by ordinary spawn's origin refresh. Its
        # launch-position callback must restore the immutable selected input.
        self.assertEqual(clean_commit(self.slot), self.initial)
        self.assertEqual(self.attachment["input_commit"], self.delivered)
        result = self.run_position()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(clean_commit(self.slot), self.delivered)
        self.assertEqual((self.slot / "delivered.txt").read_text(),
                         "Locally landed output without a push.\n")
        self.assertEqual(clean_commit(self.project), self.delivered)
        self.assertEqual(self.fixture.git("rev-parse", "origin/main"), self.initial)
        remote = subprocess.run(["git", "--git-dir", str(self.remote), "rev-parse", "main"],
                                check=True, capture_output=True, text=True).stdout.strip()
        self.assertEqual(remote, self.initial)
        self.assertFalse((self.owner.home / "state/fresh.meta").exists())
        self.assertEqual(git(self.slot, "symbolic-ref", "--quiet", "--short", "HEAD", accepted=(0, 1)), "")

    def test_fresh_root_requires_existing_spawn_project_and_slot_custody(self):
        for scenario in ("missing-spawn", "missing-project", "wrong-claim"):
            with self.subTest(scenario=scenario):
                result = self.run_position(scenario)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("current spawn custody and its own Treehouse slot", result.stderr)
                self.assertEqual(clean_commit(self.slot), self.initial)
                self.assertEqual(clean_commit(self.project), self.delivered)

    def test_root_position_refuses_dirty_foreign_primary_and_named_branch_inputs(self):
        (self.slot / "unfinished.txt").write_text("preserve this work")
        with self.assertRaisesRegex(GroupError, "dirty"):
            launch_position(self.owner, "fresh", self.slot)
        self.assertEqual((self.slot / "unfinished.txt").read_text(), "preserve this work")
        self.assertEqual(git(self.slot, "rev-parse", "HEAD"), self.initial)
        (self.slot / "unfinished.txt").unlink()
        with self.assertRaisesRegex(GroupError, "own worktree"):
            launch_position(self.owner, "fresh", self.project)
        foreign = self.base / "foreign"
        subprocess.run(["git", "clone", "-q", str(self.project), str(foreign)], check=True)
        with self.assertRaisesRegex(GroupError, "attached repository"):
            launch_position(self.owner, "fresh", foreign)
        self.assertEqual(clean_commit(foreign), self.delivered)
        git(self.slot, "switch", "-c", "retained-branch")
        with self.assertRaisesRegex(GroupError, "detached"):
            launch_position(self.owner, "fresh", self.slot)
        self.assertEqual(self.fixture.git("rev-parse", "retained-branch"), self.initial)
        self.assertEqual(clean_commit(self.project), self.delivered)

    def test_published_root_preserves_its_joined_branch_and_dirty_repair(self):
        git(self.slot, "switch", "-c", "fm/fresh", self.delivered)
        (self.slot / "joined.txt").write_text("retained joined result")
        git(self.slot, "add", "joined.txt")
        git(self.slot, "commit", "-qm", "joined work")
        joined = clean_commit(self.slot)
        meta = dict(self.fixture.root_meta, endpoint_task_id="fresh", kind="ship", mode="local-only",
                    worktree=str(self.slot), task_group_delivery="ship-local-only",
                    task_group_primitive="Work", task_group_workflow="dynamic")
        self.fixture.save_meta("fresh", meta)
        (self.slot / "repair.txt").write_text("retained unfinished repair")
        launch_position(self.owner, "fresh", self.slot)
        self.assertEqual(git(self.slot, "rev-parse", "HEAD"), joined)
        self.assertEqual(git(self.slot, "symbolic-ref", "--short", "HEAD"), "fm/fresh")
        self.assertEqual((self.slot / "repair.txt").read_text(), "retained unfinished repair")


if __name__ == "__main__":
    unittest.main()
