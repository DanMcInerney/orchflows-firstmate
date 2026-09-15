"""Targeted dynamic launch/selection checks with real disposable Linux Git worktrees."""
import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import unittest

import test_enablement as enable_fixtures
from fm_orchflows import auto_attach, enable, launch_context, library_overlay
from fm_task_group_launch import launch_check, launch_meta, launch_overlay, launch_position
from fm_task_group_store import GroupError, clean_commit, git
from fm_task_group_policy import claude_permissions, file_rule


class DynamicLaunchTests(unittest.TestCase):
    def setUp(self):
        self.fixture = enable_fixtures.EnablementTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.owner = self.fixture.owner
        self.package = self.fixture.package
        self.project = self.fixture.project
        self.base = self.fixture.fixture.base
        self.fixture.package.joinpath("scripts/firstmate-client.json").write_text(json.dumps(
            {"schema": 1, "launch_context_schema": 1, "workflows": ["dynamic"]}))
        skill = self.package / "skills/orch-dynamic-workflow/SKILL.md"
        skill.parent.mkdir()
        skill.write_text("Compose Work, join/check, one Review, one repair/check.\n")
        self.owner.spawn = self.spawn
        self.children = []

    def attach(self, task="dynamic-root", workflow="dynamic"):
        return auto_attach(self.owner, task, "scout", "herdr", "claude",
                           self.project, workflow=workflow)

    def publish_root(self):
        self.attach()
        self.worktree = self.base / "root-worktree"
        git(self.project, "worktree", "add", "--detach", str(self.worktree), "HEAD")
        meta = dict(self.fixture.fixture.root_meta, endpoint_task_id="dynamic-root",
                    worktree=str(self.worktree))
        meta.update(self.fixture.fixture.fields(launch_meta(self.owner, "dynamic-root")))
        self.fixture.fixture.save_meta("dynamic-root", meta)

    def spawn(self, root, generation, child, project, harness, model, effort):
        binding, record, attachment = self.owner.component_context(child)
        launch_check(self.owner, child, "scout", "herdr", harness, project)
        worktree = self.base / (child + "-worktree")
        git(self.project, "worktree", "add", "--detach", str(worktree), "HEAD")
        # The injected spawn boundary has no actual lifecycle owner; real lock
        # and slot custody is checked separately against the prepared shell bridge.
        with patch("fm_task_group_launch.verify_position"):
            launch_position(self.owner, child, worktree)
        launch_check(self.owner, child, "scout", "herdr", harness, project, worktree)
        self.assertEqual(clean_commit(worktree), record["input_commit"])
        tasktmp = self.base / (child + "-tmp")
        tasktmp.mkdir()
        meta = dict(self.fixture.fixture.root_meta, endpoint_task_id=child,
                    spawn_gen="s2.345.6", worktree=str(worktree), tasktmp=str(tasktmp),
                    herdr_workspace_id="fixture-workspace", herdr_tab_id="fixture-tab",
                    herdr_pane_id="fixture-pane", window="fixture-window")
        meta.update(self.fixture.fixture.fields(launch_meta(self.owner, child)))
        self.fixture.fixture.save_meta(child, meta)
        self.children.append(child)
        return SimpleNamespace(returncode=0)

    def test_project_default_explicit_selection_optout_and_relaunch_precedence(self):
        entry = enable(self.owner, self.package, self.project, workflow="dynamic")
        self.assertEqual((entry["primitive"], entry["review_policy"], entry["workflow"]),
                         ("Work", "workflow-review", "dynamic"))
        self.assertEqual(self.attach(workflow="default"), "root")
        original = self.owner.attachment("dynamic-root")
        self.assertEqual(original["readonly"], False)
        self.assertIsNone(self.attach("ordinary", workflow="none"))
        self.assertFalse(self.owner.group("ordinary").exists())
        enable(self.owner, self.package, self.project)
        self.assertEqual(self.attach(workflow="none"), "root")
        self.assertEqual(self.owner.attachment("dynamic-root"), original)
        self.assertEqual(self.attach("selected", workflow="dynamic"), "root")
        self.assertEqual(self.owner.attachment("selected")["workflow"], "dynamic")
        self.attach("default-work", workflow="default")
        self.assertNotIn("workflow", self.owner.attachment("default-work"))

    def test_dynamic_selection_requires_enabled_capability_and_supported_profile(self):
        with self.assertRaisesRegex(GroupError, "enabled project"):
            self.attach()
        self.package.joinpath("scripts/firstmate-client.json").write_text(json.dumps(
            {"schema": 1, "launch_context_schema": 1}))
        enable(self.owner, self.package, self.project)
        with self.assertRaisesRegex(GroupError, "dynamic client capability"):
            self.attach()
        with self.assertRaisesRegex(GroupError, "dynamic client capability"):
            enable(self.owner, self.package, self.project, workflow="dynamic")
        with self.assertRaisesRegex(GroupError, "Work/workflow-review"):
            enable(self.owner, self.package, self.project, "Review", "explicit-audit",
                   workflow="dynamic")
        with self.assertRaisesRegex(GroupError, "scout"):
            auto_attach(self.owner, "ship", "ship", "herdr", "claude", self.project, "dynamic")
        self.assertFalse(self.owner.group("dynamic-root").exists())

    def test_dynamic_launch_retains_committed_and_dirty_parent_work(self):
        enable(self.owner, self.package, self.project, workflow="dynamic")
        self.publish_root()
        (self.worktree / "joined.txt").write_text("Joined useful work\n")
        git(self.worktree, "add", ".")
        git(self.worktree, "commit", "-qm", "join")
        joined = clean_commit(self.worktree)
        (self.worktree / "repair.txt").write_text("In-progress repair\n")
        launch_check(self.owner, "dynamic-root", "scout", "herdr", "claude",
                     self.project, self.worktree)
        launch_position(self.owner, "dynamic-root", self.worktree)
        self.assertEqual(git(self.worktree, "rev-parse", "HEAD"), joined)
        self.assertEqual((self.worktree / "repair.txt").read_text(), "In-progress repair\n")
        context = json.loads(Path(launch_context(self.owner, "dynamic-root", "s1.123.4")).read_text())
        self.assertEqual(context["primitive"], "Work")

    def test_fresh_components_start_at_current_root_candidate_and_preserve_root(self):
        enable(self.owner, self.package, self.project, workflow="dynamic")
        self.publish_root()
        (self.worktree / "joined.txt").write_text("Candidate after joining prior work\n")
        git(self.worktree, "add", ".")
        git(self.worktree, "commit", "-qm", "candidate")
        joined = clean_commit(self.worktree)
        body = {"request_id": "make-next", "assignment": "Extend joined.txt",
                "primitive": "Work", "writable": True}
        view = self.owner.submit("dynamic-root", "s1.123.4", body)
        child = view["request"]["child"]
        self.assertEqual(self.owner.meta(child)["task_group_writable"], "true")
        self.assertIn("Commit the complete result", (self.owner.task(child) / "brief.md").read_text())
        self.assertEqual(clean_commit(self.worktree), joined)
        self.assertNotEqual(clean_commit(self.project), joined)
        with self.assertRaisesRegex(GroupError, "fresh launching"):
            launch_position(self.owner, child, Path(self.owner.meta(child)["worktree"]))

    def test_readonly_review_uses_request_commit_and_component_completion(self):
        enable(self.owner, self.package, self.project, workflow="dynamic")
        self.publish_root()
        (self.worktree / "candidate.txt").write_text("Review this exact candidate\n")
        git(self.worktree, "add", ".")
        git(self.worktree, "commit", "-qm", "candidate")
        joined = clean_commit(self.worktree)
        view = self.owner.submit("dynamic-root", "s1.123.4",
                                 {"request_id": "audit", "assignment": "Audit candidate.txt",
                                  "primitive": "Review", "writable": False})
        child = view["request"]["child"]
        meta = self.owner.meta(child)
        self.assertEqual((meta["task_group_primitive"], meta["task_group_writable"]),
                         ("Review", "false"))
        overlay = launch_overlay(self.owner, child)
        self.assertIn(joined, overlay)
        self.assertIn("do not make or delegate repairs", overlay)
        self.assertIn("Do not write ordinary scout done status", overlay)
        self.assertNotIn("scoped Work implementation", overlay)

    def test_position_requires_real_spawn_locks_and_exact_pool_slot_claim(self):
        candidate = Path(os.environ["FM_STAGE1_FIRSTMATE_ROOT"])
        pool = self.base / "pool"
        slot = pool / "slot" / "project"
        slot.parent.mkdir(parents=True)
        (pool / "treehouse-state.json").write_text("{}")
        git(self.project, "worktree", "add", "--detach", str(slot), "HEAD")
        caller = self.base / "verify-position.py"
        caller.write_text(
            "import os,sys\nfrom pathlib import Path\n"
            "sys.path.insert(0, str(Path(os.environ['CODE']) / 'bin'))\n"
            "from fm_task_group import TaskGroups\n"
            "from fm_task_group_launch import verify_position\n"
            "owner=TaskGroups(Path(os.environ['FM_HOME']), Path(os.environ['CODE']))\n"
            "verify_position(owner, dict(parent='root', accepted_parent_gen='s1.123.4', "
            "child=os.environ['CHILD']), Path(os.environ['PROJECT']), Path(os.environ['SLOT']))\n")
        shell = r"""
set -eu
. "$CODE/bin/fm-backend.sh"
. "$CODE/bin/fm-wake-lib.sh"
control="$FM_HOME/state/.control-root.lock"
metalock=$(fm_meta_lock_path "$FM_HOME/state/root.meta")
spawnlock="$FM_HOME/state/.spawn-$CHILD.lock"
projectlock=$(fm_treehouse_project_lock_path "$PROJECT")
held=()
cleanup() { for lock in "${held[@]}"; do fm_lock_release "$lock" || true; done; }
trap cleanup EXIT
for lock in "$control" "$metalock" "$projectlock"; do
  fm_lock_try_acquire "$lock"
  held+=("$lock")
done
if [ "$SCENARIO" != missing-spawn ]; then
  fm_lock_try_acquire "$spawnlock"
  held+=("$spawnlock")
fi
claim="$CHILD"
[ "$SCENARIO" != wrong-claim ] || claim=other-task
fm_treehouse_slot_owner_claim "$SLOT" "$claim" "$FM_HOME"
fm_current_pid FM_TASK_GROUP_LOCK_OWNER
export FM_TASK_GROUP_LOCK_OWNER FM_TASK_GROUP_LOCK_ROOT=root FM_TASK_GROUP_LOCK_HOME="$FM_HOME"
"$PYTHON" -B "$CALLER"
"""
        for scenario, succeeds in (("owned", True), ("missing-spawn", False),
                                   ("wrong-claim", False)):
            with self.subTest(scenario=scenario):
                env = dict(os.environ, CODE=str(candidate), FM_HOME=str(self.owner.home),
                           PROJECT=str(self.project), SLOT=str(slot), CALLER=str(caller),
                           PYTHON=sys.executable, CHILD="tg-" + "b" * 20, SCENARIO=scenario)
                result = subprocess.run(["bash", "-c", shell], env=env,
                                        capture_output=True, text=True, timeout=30)
                self.assertEqual(result.returncode == 0, succeeds, result.stderr)
                self.assertEqual(clean_commit(slot), clean_commit(self.project))
                if not succeeds:
                    self.assertIn("current spawn custody and its own Treehouse slot", result.stderr)

    def test_leaf_trial_reads_frozen_authored_library_and_retained_dependencies(self):
        dependency = self.fixture.library()
        enable(self.owner, self.package, self.project, workflow="dynamic",
               libraries=(dependency,))
        self.publish_root()
        attachment = self.owner.attachment("dynamic-root")
        authored = {
            "library/plugin.json": '{"name":"authored","version":"1.0","skills":"./skills/"}',
            "library/.claude-plugin/plugin.json": '{"name":"authored","version":"1.0"}',
            "library/.codex-plugin/plugin.json": '{"name":"authored","version":"1.0"}',
            "library/README.md": "Apply the leaf to a declared input; zero delegated agents.",
            "library/references/library-context.md": "Use retained custom-a and writing guidance.",
            "library/guidance/summary.md": "## Make\nRetain every input fact.",
            "library/skills/summarize/SKILL.md": "Read the declared input and return its summary.",
            "fixture.txt": "Three crates remain.",
        }
        for relative, content in authored.items():
            path = self.worktree / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        git(self.worktree, "add", ".")
        git(self.worktree, "commit", "-qm", "join authored library")
        candidate = clean_commit(self.worktree)
        view = self.owner.submit("dynamic-root", "s1.123.4", {
            "request_id": "leaf-trial", "primitive": "Work", "writable": False,
            "assignment": "Apply library/skills/summarize/SKILL.md to fixture.txt in your "
                          "own worktree using retained dependencies. Return the output and findings.",
        })
        child = view["request"]["child"]
        meta = self.owner.meta(child)
        worktree = Path(meta["worktree"])
        self.assertEqual(view["request"]["input_commit"], candidate)
        for relative, content in authored.items():
            self.assertEqual((worktree / relative).read_text(), content)
        self.assertFalse((Path(attachment["package_path"]) / "library").exists())
        retained_dependency = (Path(attachment["package_path"]) /
                               "firstmate-libraries/custom-a/skills/inspect/SKILL.md")
        expected_dependency = retained_dependency.read_bytes()
        (dependency / "skills/inspect/SKILL.md").write_text("Changed future dependency")
        (self.worktree / "fixture.txt").write_text("Changed author input")
        self.assertEqual((worktree / "fixture.txt").read_text(), authored["fixture.txt"])
        self.assertEqual(retained_dependency.read_bytes(), expected_dependency)
        permissions = claude_permissions(self.owner, child, meta["spawn_gen"])["allow"]
        self.assertIn(file_rule(self.owner.runtime, "Read", attachment["package_path"], tree=True),
                      permissions)
        self.assertNotIn(file_rule(self.owner.runtime, "Read", self.worktree, tree=True), permissions)
        self.assertNotIn(file_rule(self.owner.runtime, "Edit", attachment["package_path"], tree=True),
                         permissions)
        report = Path(meta["tasktmp"]) / "trial.md"
        report.write_text("Three crates remain.\nTrial uses the frozen declared input.")
        self.owner.complete(child, meta["spawn_gen"], report)
        retained = self.owner.status("dynamic-root", "s1.123.4", request_id="leaf-trial")
        self.assertEqual(Path(retained["report_path"]).read_bytes(), report.read_bytes())
        self.assertEqual(retained["result"]["input_commit"], candidate)
        self.assertEqual(clean_commit(worktree), candidate)
        self.assertEqual(self.owner.attachment("dynamic-root"), attachment)

    def test_relaunch_reapplies_retained_custom_deliverables_before_completion(self):
        library = self.fixture.library()
        source_skill = library / "skills/inspect/SKILL.md"
        requirement = "Deliver a rationale in the root report and verify the joined result.\n"
        source_skill.write_text(requirement)
        enable(self.owner, self.package, self.project, workflow="dynamic", libraries=(library,))
        self.publish_root()
        attachment = self.owner.attachment("dynamic-root")
        retained_skill = (Path(attachment["package_path"]) /
                          "firstmate-libraries/custom-a/skills/inspect/SKILL.md")
        first_context = launch_context(self.owner, "dynamic-root", "s1.123.4")
        first_overlay = launch_overlay(self.owner, "dynamic-root")
        (self.worktree / "joined.txt").write_text("Already joined work\n")
        git(self.worktree, "add", ".")
        git(self.worktree, "commit", "-qm", "retained join")
        joined_commit = clean_commit(self.worktree)
        source_skill.write_text("Future source requirements do not belong to this retained task.\n")
        meta = self.owner.meta("dynamic-root")
        meta["spawn_gen"] = "s3.456.7"
        self.fixture.fixture.save_meta("dynamic-root", meta)
        replacement_context = launch_context(self.owner, "dynamic-root", "s3.456.7")
        replacement_overlay = launch_overlay(self.owner, "dynamic-root")
        self.assertNotEqual(first_context, replacement_context)
        self.assertEqual(clean_commit(self.worktree), joined_commit)
        self.assertEqual(retained_skill.read_text(), requirement)
        self.assertEqual(self.owner.attachment("dynamic-root"), attachment)
        for overlay in (first_overlay, replacement_overlay):
            self.assertIn(str(retained_skill), overlay)
            self.assertIn("on initial launch and every relaunch read the full selected "
                          "retained custom skill before continuing", overlay)
            self.assertIn("Reapply its deliverable and validation requirements "
                          "to the retained results and remaining work", overlay)
            self.assertIn("Before ordinary root completion, reread any selected retained custom skill "
                          "and verify its required report content, artifacts and checks are satisfied", overlay)
            self.assertIn("inspect status and reread any selected retained custom skill", overlay)
        catalog = library_overlay(attachment)
        self.assertIn("On initial launch and every relaunch", catalog)
        self.assertIn("Before ordinary root completion, reread that skill", catalog)

    def test_dynamic_catalog_and_root_guidance_use_retained_composition_contract(self):
        enable(self.owner, self.package, self.project, workflow="dynamic",
               libraries=(self.fixture.library(),))
        self.publish_root()
        attachment = self.owner.attachment("dynamic-root")
        overlay = launch_overlay(self.owner, "dynamic-root")
        for expected in ("orch-dynamic-workflow/SKILL.md", "status --request-id REQUEST_ID",
                         "gather --request-id REQUEST_ID", "output_commit",
                         "cherry-pick", "request one fresh independent read-only Review",
                         "normal scout report", "workflow-review", "primitive", "writable",
                         "exact top-level report_path and result_path returned by that response",
                         "component_meta.tasktmp and component_meta.worktree record provenance",
                         "Do not reconstruct component scratch paths or broaden permissions",
                         "If the retained paths are absent or unavailable, keep the request pending",
                         "reconcile through FirstMate's existing owner before continuing"):
            self.assertIn(expected, overlay)
        self.assertNotIn("Additional components, writers, Dynamic", library_overlay(attachment))
        self.assertIn("Custom and meta skills load in the current caller", library_overlay(attachment))
        self.assertIn(attachment["package_path"], overlay)


if __name__ == "__main__":
    unittest.main()
