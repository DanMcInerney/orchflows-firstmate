"""Selected local-only root delivery at actual FirstMate entrypoints; no live fleet."""
import json
import os
from pathlib import Path
import subprocess
import unittest

import test_task_group as fixtures
import test_dynamic_owner as dynamic
import test_enablement as enabled
from fm_orchflows import auto_attach, enable, launch_context
from fm_task_group_delivery import delivery_check, local_delivery
from fm_task_group_launch import launch_check, launch_meta, launch_overlay
from fm_task_group_store import GroupError, git


class LocalDeliveryTests(unittest.TestCase):
    spawn = dynamic.DynamicOwnerTests.spawn
    submit = dynamic.DynamicOwnerTests.submit
    gather = dynamic.DynamicOwnerTests.gather
    complete = dynamic.DynamicOwnerTests.complete
    commit = dynamic.DynamicOwnerTests.commit
    git_at = dynamic.DynamicOwnerTests.git_at

    def setUp(self):
        self.fixture = fixtures.ControllerTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.owner = self.fixture.owner
        self.candidate = Path(os.environ["FM_STAGE1_FIRSTMATE_ROOT"])
        self.fixture.git("branch", "-M", "main")
        self.fixture.package.joinpath("scripts/firstmate-client.json").write_text(json.dumps(
            dict(schema=1, launch_context_schema=1, workflows=["dynamic"],
                 root_deliveries=["ship-local-only"])))
        self.attachment = self.owner.attach("flow", self.fixture.package, self.fixture.project,
                                            "Work", "workflow-review", workflow="dynamic",
                                            delivery=local_delivery("flow"))
        self.root_worktree = self.fixture.base / "root-worktree"
        self.fixture.git("worktree", "add", "-b", "fm/flow", str(self.root_worktree), "HEAD")
        self.root_meta = dict(self.fixture.root_meta, endpoint_task_id="flow", kind="ship",
                              mode="local-only", yolo="on", worktree=str(self.root_worktree))
        self.root_meta.update(self.fixture.fields(launch_meta(self.owner, "flow")))
        self.fixture.save_meta("flow", self.root_meta)
        self.owner.spawn = self.spawn
        self.records = []
        for folder in ("config",):
            (self.owner.home / folder).mkdir(exist_ok=True)
        self.env = {key: value for key, value in os.environ.items()
                    if not key.startswith(("FM_", "HERDR_", "ORCHFLOWS_"))}
        self.env.update(FM_HOME=str(self.owner.home), FM_ROOT_OVERRIDE=str(self.candidate),
                        FM_SPAWN_NO_GUARD="1")

    def merge(self):
        return subprocess.run(["bash", str(self.candidate / "bin/fm-merge-local.sh"), "flow"],
                              env=self.env, capture_output=True, text=True, timeout=30)

    def test_ordinary_spawn_callbacks_admit_only_pristine_detached_start_before_worker_branch(self):
        self.owner.attach("fresh", self.fixture.package, self.fixture.project,
                          "Work", "workflow-review", workflow="dynamic", delivery=local_delivery("fresh"))
        worktree = self.fixture.base / "fresh-worktree"
        self.fixture.git("worktree", "add", "--detach", str(worktree), "HEAD")
        controller = self.candidate / "bin/fm-task-group.py"

        def call(*args):
            return subprocess.run(["python3", "-B", str(controller), "--home", str(self.owner.home), *args],
                                  env=self.env, capture_output=True, text=True, timeout=30)

        launch = ["launch-check", "fresh", "--kind", "ship", "--backend", "herdr", "--harness", "claude",
                  "--project", str(self.fixture.project), "--worktree", str(worktree), "--mode", "local-only"]
        admitted = call(*launch)
        self.assertEqual(admitted.returncode, 0, admitted.stderr)
        self.git_at(worktree, "switch", "-c", "wrong-fresh-branch")
        self.assertNotEqual(call(*launch).returncode, 0)
        self.git_at(worktree, "switch", "--detach")
        (worktree / "dirty.txt").write_text("not pristine")
        self.assertNotEqual(call(*launch).returncode, 0)
        (worktree / "dirty.txt").unlink()
        advanced = self.commit(worktree, "advanced.txt")
        self.assertNotEqual(call(*launch).returncode, 0)
        self.git_at(worktree, "reset", "--hard", self.attachment["input_commit"])
        self.git_at(worktree, "branch", "fm/fresh", advanced)
        self.assertNotEqual(call(*launch).returncode, 0)
        self.git_at(worktree, "branch", "-D", "fm/fresh")
        # These are the actual entrypoints fm-spawn invokes after publishing
        # metadata and before launching the worker with fm-brief's branch step.
        tasktmp = self.fixture.base / "fresh-tasktmp"
        tasktmp.mkdir()
        metadata = {**self.root_meta, "endpoint_task_id": "fresh", "worktree": str(worktree),
                    "tasktmp": str(tasktmp)}
        published = call("launch-meta", "fresh")
        self.assertEqual(published.returncode, 0, published.stderr)
        metadata.update(self.fixture.fields(published.stdout))
        self.fixture.save_meta("fresh", metadata)
        for verb in ("launch-claude-permissions", "launch-context"):
            result = call(verb, "fresh", "--generation", metadata["spawn_gen"])
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotEqual(call("status", "fresh", "--generation", metadata["spawn_gen"]).returncode, 0)
        # Execute the unmodified ordinary ship brief's first worker action.
        self.git_at(worktree, "checkout", "-b", "fm/fresh")
        self.assertEqual(call("status", "fresh", "--generation", metadata["spawn_gen"]).returncode, 0)
        self.assertEqual(call(*launch).returncode, 0)
        self.git_at(worktree, "switch", "--detach")
        self.assertNotEqual(call(*launch).returncode, 0, "relaunch must retain the existing delivery branch")

    def test_ship_components_stay_scout_and_relaunch_retains_delivery_and_generation(self):
        pending = self.submit()
        child = pending["request"]["child"]
        child_meta = self.owner.meta(child)
        self.assertEqual((child_meta["kind"], child_meta["result_disposition"]), ("scout", "parent"))
        self.assertNotIn("task_group_delivery", child_meta)
        self.assertEqual(pending["scope"], "local-dynamic-ship-local-only")
        context = json.loads(Path(launch_context(self.owner, "flow", "s1.123.4")).read_text())
        self.assertEqual(context["root_delivery"], local_delivery("flow"))
        joined = self.commit(self.root_worktree, "root.txt")
        (self.root_worktree / "repair.txt").write_text("unfinished repair")
        launch_check(self.owner, "flow", "ship", "herdr", "claude", self.fixture.project,
                     self.root_worktree, mode="local-only")
        self.root_meta["spawn_gen"] = "replacement"
        self.fixture.save_meta("flow", self.root_meta)
        replacement = json.loads(Path(launch_context(self.owner, "flow", "replacement")).read_text())
        self.assertEqual(replacement["root_delivery"], context["root_delivery"])
        self.assertEqual(self.submit()["request"], pending["request"])
        self.assertEqual(self.git_at(self.root_worktree, "rev-parse", "HEAD"), joined)
        self.assertTrue((self.root_worktree / "repair.txt").exists())
        with self.assertRaisesRegex(GroupError, "stale"):
            self.owner.status("flow", "s1.123.4")
        overlay = launch_overlay(self.owner, "flow")
        self.assertIn("done: ready in branch fm/flow", overlay)
        self.assertNotIn("normal scout report", overlay)
        self.assertIn("Do not merge, push or open a PR", overlay)

    def test_changed_delivery_metadata_cannot_dispatch_replay_gather_or_relaunch(self):
        first = self.submit()
        self.complete(first, "maker.txt")
        original = dict(self.root_meta)
        for key, value in (("kind", "scout"), ("mode", "direct-PR"), ("mode", "no-mistakes"),
                           ("task_group_delivery", "scout-report")):
            with self.subTest(key=key, value=value):
                self.fixture.save_meta("flow", {**original, key: value})
                for action in (lambda: self.submit(), lambda: self.submit("new-work"),
                               lambda: self.gather("maker-a"),
                               lambda: delivery_check(self.owner, "flow")):
                    with self.assertRaises(GroupError):
                        action()
        self.assertEqual(len(self.records), 1)
        self.fixture.save_meta("flow", original)
        self.assertFalse(self.owner.request("flow", "maker-a")["gathered"])

    def test_ref_replay_requires_own_expected_branch_and_repository(self):
        self.submit()
        for args in (("switch", "--detach", "HEAD"), ("switch", "-c", "other-delivery")):
            self.git_at(self.root_worktree, *args)
            with self.assertRaisesRegex(GroupError, "branch differs"):
                self.submit()
            with self.assertRaises(GroupError):
                launch_check(self.owner, "flow", "ship", "herdr", "claude", self.fixture.project,
                             self.root_worktree, mode="local-only")
        self.git_at(self.root_worktree, "switch", "fm/flow")
        foreign = self.fixture.base / "foreign"
        subprocess.run(["git", "clone", "-q", str(self.fixture.project), str(foreign)], check=True)
        self.git_at(foreign, "switch", "-c", "fm/flow")
        self.fixture.save_meta("flow", {**self.root_meta, "worktree": str(foreign)})
        with self.assertRaisesRegex(GroupError, "own worktree"):
            self.submit()
        self.assertEqual(len(self.records), 1)

    def test_actual_local_merge_guards_every_result_review_and_clean_ready_branch(self):
        initial = self.fixture.git("rev-parse", "main")
        empty = self.merge()
        self.assertNotEqual(empty.returncode, 0, empty.stdout)
        self.assertIn("unfinished workflow Review", empty.stderr)
        maker = self.complete(self.submit(), "maker.txt")
        self.assertNotEqual(self.merge().returncode, 0)
        self.gather("maker-a")
        self.git_at(self.root_worktree, "cherry-pick", maker["result"]["output_commit"])
        self.assertNotEqual(self.merge().returncode, 0)
        audit = self.submit("audit", "Review", False)
        self.complete(audit)
        self.assertNotEqual(self.merge().returncode, 0)
        self.gather("audit")
        repair = self.submit("repair")
        self.assertNotEqual(self.merge().returncode, 0)
        result = self.complete(repair, "repair.txt")
        self.gather("repair")
        self.git_at(self.root_worktree, "cherry-pick", result["result"]["output_commit"])
        (self.root_worktree / "dirty.txt").write_text("unfinished")
        self.assertNotEqual(self.merge().returncode, 0)
        (self.root_worktree / "dirty.txt").unlink()
        self.assertEqual(self.fixture.git("rev-parse", "main"), initial)
        landed = self.merge()
        self.assertEqual(landed.returncode, 0, landed.stderr)
        self.assertEqual(self.fixture.git("rev-parse", "main"),
                         self.git_at(self.root_worktree, "rev-parse", "HEAD"))
        self.assertTrue((self.fixture.project / "maker.txt").is_file())
        self.assertTrue((self.fixture.project / "repair.txt").is_file())
        self.assertEqual(self.fixture.git("rev-parse", maker["result"]["output_ref"]),
                         maker["result"]["output_commit"])

    def teardown_guard(self):
        shell = '. "$FM_ROOT_OVERRIDE/bin/fm-backend.sh"\n' + \
                '. "$FM_ROOT_OVERRIDE/bin/fm-task-group-state.sh"\n' + \
                'fm_task_group_guard "$FM_HOME" flow "$FM_HOME/state" teardown\n'
        return subprocess.run(["bash", "-c", shell], env=self.env,
                              capture_output=True, text=True, timeout=30)

    def ready_output(self):
        result = self.complete(self.submit(), "maker.txt")
        self.gather("maker-a")
        self.git_at(self.root_worktree, "cherry-pick", result["result"]["output_commit"])
        self.complete(self.submit("audit", "Review", False))
        self.gather("audit")
        return result

    def test_actual_teardown_guard_refuses_unlanded_promised_branch_after_switch(self):
        self.ready_output()
        self.assertTrue(self.owner.waiting("flow")["cleanup_allowed"])
        original = self.git_at(self.root_worktree, "rev-parse", "fm/flow")
        self.git_at(self.root_worktree, "switch", "-c", "unrelated-landed", "main")
        result = self.teardown_guard()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("immutable task-group delivery fm/flow is not landed", result.stderr)
        self.assertEqual(self.fixture.git("rev-parse", "fm/flow"), original)
        self.assertNotEqual(self.fixture.git("rev-parse", "main"), original)
        # The actual entrypoint invokes that guard before any endpoint mutation.
        actual = subprocess.run(["bash", str(self.candidate / "bin/fm-teardown.sh"), "flow"],
                                env=self.env, capture_output=True, text=True, timeout=30)
        self.assertNotEqual(actual.returncode, 0)
        self.assertIn("immutable task-group delivery fm/flow is not landed", actual.stderr)
        self.assertTrue((self.owner.home / "state/flow.meta").exists())

    def test_actual_teardown_guard_rejects_clean_foreign_worktree_after_landing(self):
        self.ready_output()
        self.assertEqual(self.merge().returncode, 0)
        foreign = self.fixture.base / "foreign-clean"
        subprocess.run(["git", "clone", "-q", str(self.fixture.project), str(foreign)], check=True)
        self.git_at(foreign, "switch", "-c", "fm/flow")
        self.fixture.save_meta("flow", {**self.root_meta, "worktree": str(foreign)})
        result = self.teardown_guard()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("own worktree of the attached repository", result.stderr)

    def test_detach_and_return_retry_keeps_landed_ref_without_backlog_marker(self):
        self.ready_output()
        self.assertEqual(self.merge().returncode, 0)
        source = (self.candidate / "bin/fm-teardown.sh").read_text()
        # Exercise the actual ordinary detach/branch/return block. Only the
        # external Treehouse return is replaced with a failed/successful return.
        block = source.split('elif [ -d "$WT" ] && [ "$KIND" != secondmate ]; then\n', 1)[1]
        block = block.split('\nfi\n\nHERDR_PRESENTATION_JOURNAL=', 1)[0]
        prefix = r'''set -eu
. "$FM_ROOT_OVERRIDE/bin/fm-backend.sh"
. "$FM_ROOT_OVERRIDE/bin/fm-wake-lib.sh"
ID=flow KIND=ship FORCE= TEARDOWN_TASK_GROUP_LOCAL_DELIVERY=1
WT="$TEST_WORKTREE" PROJ="$TEST_PROJECT"
teardown_treehouse_return() {
  [ "$TEST_RETURN" = success ] || return 1
  git -C "$WT" reset --hard main >/dev/null
}
'''
        for outcome in ("failure", "success"):
            result = subprocess.run(["bash", "-c", prefix + block],
                                    env={**self.env, "TEST_WORKTREE": str(self.root_worktree),
                                         "TEST_PROJECT": str(self.fixture.project), "TEST_RETURN": outcome},
                                    capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode == 0, outcome == "success", result.stderr)
            self.assertEqual(self.git_at(self.root_worktree, "rev-parse", "--abbrev-ref", "HEAD"), "HEAD")
            self.assertEqual(self.fixture.git("rev-parse", "fm/flow"), self.fixture.git("rev-parse", "main"))
            self.assertFalse((self.owner.home / "state/flow.backlog-close").exists())
            retry = self.teardown_guard()
            self.assertEqual(retry.returncode, 0, retry.stderr)

    def test_deleted_ref_retry_requires_exact_existing_local_completion_marker(self):
        self.ready_output()
        self.assertEqual(self.merge().returncode, 0)
        self.git_at(self.root_worktree, "checkout", "--detach")
        self.fixture.git("branch", "-d", "fm/flow")
        self.assertNotEqual(self.teardown_guard().returncode, 0)
        shell = r'''
. "$FM_ROOT_OVERRIDE/bin/fm-backlog-transition-lib.sh"
fm_backlog_close_marker_write "$FM_HOME/state" flow "$FM_HOME/data" s1.123.4 --note 'local main'
'''
        marker = subprocess.run(["bash", "-c", shell], env=self.env,
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(marker.returncode, 0, marker.stderr)
        retry = self.teardown_guard()
        self.assertEqual(retry.returncode, 0, retry.stderr)
        self.fixture.save_meta("flow", {**self.root_meta, "spawn_gen": "later-generation"})
        stale = self.teardown_guard()
        self.assertNotEqual(stale.returncode, 0)
        self.assertIn("exact-generation local completion marker", stale.stderr)
        self.fixture.save_meta("flow", self.root_meta)
        # An actual pool claim owned by someone else keeps that slot untouched
        # while the old task's validated completion record permits cleanup.
        pool = self.fixture.base / "pool"
        slot = pool / "slot" / "project"
        slot.parent.mkdir(parents=True)
        (pool / "treehouse-state.json").write_text("{}")
        self.fixture.git("worktree", "move", str(self.root_worktree), str(slot))
        self.fixture.save_meta("flow", {**self.root_meta, "worktree": str(slot)})
        claim_shell = r'''
. "$FM_ROOT_OVERRIDE/bin/fm-wake-lib.sh"
fm_treehouse_slot_owner_claim "$TEST_SLOT" successor "$FM_HOME"
'''
        claim = subprocess.run(["bash", "-c", claim_shell], env={**self.env, "TEST_SLOT": str(slot)},
                               capture_output=True, text=True, timeout=30)
        self.assertEqual(claim.returncode, 0, claim.stderr)
        (slot / "successor.txt").write_text("current owner's unfinished work")
        retry = self.teardown_guard()
        self.assertEqual(retry.returncode, 0, retry.stderr)
        self.assertEqual((slot / "successor.txt").read_text(), "current owner's unfinished work")
        self.assertIn("task=successor", (slot.parent / ".fm-slot-owner").read_text())

    def test_immutable_attachment_cannot_be_rebound_to_another_delivery(self):
        for delivery in (None, {**local_delivery("flow"), "branch": "other"},
                         {**local_delivery("flow"), "mode": "no-mistakes"}):
            with self.assertRaises(GroupError):
                self.owner.attach("flow", self.fixture.package, self.fixture.project,
                                  "Work", "workflow-review", workflow="dynamic", delivery=delivery)
        self.assertEqual(self.owner.attachment("flow"), self.attachment)

    def test_actual_spawn_rejects_unsupported_dynamic_modes_before_task_or_endpoint_mutation(self):
        for flags in (("--mode", "direct-PR", "--yolo", "on"),
                      ("--mode", "no-mistakes", "--yolo", "on"), ("--secondmate",)):
            result = subprocess.run(["bash", str(self.candidate / "bin/fm-spawn.sh"), "unsupported",
                                     str(self.fixture.project), "--orchflows-workflow", "dynamic", *flags],
                                    env=self.env, capture_output=True, text=True, timeout=30)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("dynamic workflow requires a scout or explicit ship --mode local-only", result.stderr)
            self.assertFalse(self.owner.task("unsupported").exists())
            self.assertFalse((self.owner.home / "state/unsupported.meta").exists())
            self.assertEqual(self.fixture.git("rev-parse", "main"), self.attachment["input_commit"])


class LocalDeliverySelectionTests(unittest.TestCase):
    def setUp(self):
        self.fixture = enabled.EnablementTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

    def test_retained_dev6_package_stays_scout_only_and_defaults_do_not_change_ship(self):
        fixture = self.fixture
        marker = fixture.package / "scripts/firstmate-client.json"
        marker.write_text(json.dumps(dict(schema=1, launch_context_schema=1, workflows=["dynamic"])))
        skill = fixture.package / "skills/orch-dynamic-workflow/SKILL.md"
        skill.parent.mkdir()
        skill.write_text("Compose scoped Work and one Review.\n")
        enable(fixture.owner, fixture.package, fixture.project, workflow="dynamic")
        for workflow in ("default", "none"):
            self.assertIsNone(auto_attach(fixture.owner, "ordinary", "ship", "herdr", "claude",
                                         fixture.project, workflow=workflow, mode="local-only"))
        with self.assertRaisesRegex(GroupError, "ship-local-only client capability"):
            auto_attach(fixture.owner, "new-ship", "ship", "herdr", "claude", fixture.project,
                        workflow="dynamic", mode="local-only")
        self.assertFalse(fixture.owner.group("new-ship").exists())
        marker.write_text(json.dumps(dict(schema=1, launch_context_schema=1, workflows=["dynamic"],
                                          root_deliveries=["ship-local-only"])))
        enable(fixture.owner, fixture.package, fixture.project, workflow="dynamic")
        self.assertEqual(auto_attach(fixture.owner, "new-ship", "ship", "herdr", "claude", fixture.project,
                                     workflow="dynamic", mode="local-only"), "root")
        self.assertEqual(fixture.owner.attachment("new-ship")["root_delivery"], local_delivery("new-ship"))
        self.assertFalse(fixture.owner.group("ordinary").exists())


if __name__ == "__main__":
    unittest.main()
