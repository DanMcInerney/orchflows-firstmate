"""Assignment precedence, accepted replay and the real FirstMate flag owner."""
import json
import os
from pathlib import Path
import subprocess
import unittest
from types import SimpleNamespace

import test_task_group as fixtures
from fm_task_group_controls import (resolve_axes, validate_preferences, check_launch,
                                    validate_profile)
from fm_task_group_store import GroupError, write_json


class AssignmentControlsTests(unittest.TestCase):
    def test_each_axis_resolves_independently_across_all_precedence_levels(self):
        preferences = {"assignments": {"maker": {"model": "saved-model", "effort": "low"}},
                       "operations": {"Work": {"model": "saved-operation", "effort": "medium"}}}
        body = {"request_id": "request-1", "assignment_name": "maker", "model": "caller-model",
                "operation_defaults": {"effort": "high"}}
        axes, sources = resolve_axes(body, preferences, "Work")
        self.assertEqual(axes, {"model": "caller-model", "effort": "high"})
        self.assertEqual(sources, {"model": "caller-named", "effort": "caller-operation"})
        del body["model"]
        axes, sources = resolve_axes(body, preferences, "Work")
        self.assertEqual(axes["model"], "saved-model")
        self.assertEqual(sources["model"], "saved-named")
        del body["assignment_name"]
        self.assertEqual(resolve_axes(body, preferences, "Work")[0]["model"], "saved-operation")
        axes, sources = resolve_axes(body, preferences, "Review")
        self.assertEqual(axes, {"model": "default", "effort": "high"})
        self.assertEqual(sources["model"], "firstmate-default")
        body["model"] = "default"
        self.assertEqual(resolve_axes(body, preferences, "Work")[0]["model"], "default")

    def test_preferences_never_accept_harness_or_invalid_axes(self):
        for value in ({"harness": "codex"}, {"assignments": []},
                      {"operations": {"Build": {"model": "gpt-example"}}},
                      {"assignments": {"maker": {"effort": True}}},
                      {"assignments": {"../escape": {"model": "a"}}}):
            with self.subTest(value=value), self.assertRaises(GroupError):
                validate_preferences(value)


class AssignmentOwnerTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.ControllerTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.owner = self.fixture.owner
        self.owner.code_root = Path(os.environ["FM_STAGE1_FIRSTMATE_ROOT"])
        capability = self.fixture.package / "scripts/firstmate-client.json"
        capability.write_text(json.dumps({"schema": 1, "launch_context_schema": 1,
                                          "assignment_controls": ["model-effort-v1"]}))
        self.owner.attach("controlled", self.fixture.package, self.fixture.project)
        self.parent = dict(self.fixture.root_meta, endpoint_task_id="controlled",
                           model="author-session-model", effort="high")
        self.fixture.save_meta("controlled", self.parent)

    def submit(self, **extra):
        return self.owner.submit("controlled", self.parent["spawn_gen"], dict(self.fixture.body, **extra))

    def test_modern_default_does_not_copy_author_profile_and_replay_keeps_selection(self):
        first = self.submit()
        record = first["request"]
        self.assertEqual((record["model"], record["effort"]), ("default", "default"))
        self.assertEqual(record["profile"]["sources"], {"model": "firstmate-default", "effort": "firstmate-default"})
        self.parent.update(model="later-author", effort="medium", spawn_gen="replacement")
        self.fixture.save_meta("controlled", self.parent)
        second = self.submit()
        self.assertEqual(second["request"]["profile"], record["profile"])
        self.assertEqual(second["request"]["profile_hash"], record["profile_hash"])
        self.assertEqual(len(self.fixture.calls), 1)

    def test_explicit_profile_reaches_existing_spawn_and_changed_replay_refuses(self):
        record = self.submit(model="claude-sonnet-5", operation_defaults={"effort": "medium"})["request"]
        self.assertEqual(record["state"], "launched", record)
        self.assertEqual((record["model"], record["effort"]), ("claude-sonnet-5", "medium"))
        actual = self.owner.meta(record["child"])
        self.assertEqual((actual["model"], actual["effort"]), ("claude-sonnet-5", "medium"))
        with self.assertRaisesRegex(GroupError, "different body"):
            self.submit(model="claude-sonnet-5", operation_defaults={"effort": "high"})
        changed = dict(record, model="wrong")
        write_json(self.owner.request_path("controlled"), changed)
        with self.assertRaisesRegex(GroupError, "profile identity"):
            self.owner.request("controlled")

    def test_modern_profile_cannot_be_removed_to_impersonate_legacy(self):
        record = self.submit(effort="high")["request"]
        record.pop("profile")
        record.pop("profile_hash")
        write_json(self.owner.request_path("controlled"), record)
        with self.assertRaisesRegex(GroupError, "profile is missing"):
            self.owner.request("controlled")

    def test_explicit_codex_max_refuses_before_acceptance_or_child_scaffolding(self):
        self.parent["harness"] = "codex"
        self.fixture.save_meta("controlled", self.parent)
        with self.assertRaisesRegex(GroupError, "explicit workflow effort would be omitted"):
            self.submit(model="gpt-fixture", effort="max")
        self.assertFalse(self.owner.request_path("controlled").exists())
        self.assertEqual(self.fixture.calls, [])

    def test_old_attachment_keeps_legacy_profile_without_new_capability(self):
        parent = dict(self.fixture.root_meta, model="legacy-model", effort="high")
        self.fixture.save_meta("root", parent)
        record = self.owner.submit("root", parent["spawn_gen"], self.fixture.body)["request"]
        self.assertEqual((record["model"], record["effort"]), ("legacy-model", "high"))
        self.assertNotIn("profile", record)

    def test_existing_flag_owner_emits_both_harness_controls_and_refuses_omission(self):
        script_dir = self.owner.code_root / "bin"
        script = '. "$SCRIPT_DIR/fm-harness-profile-lib.sh"; fm_validate_workflow_profile "$1" "$2" "$3" && model_flag_for_harness "$1" "$2" && effort_flag_for_harness "$1" "$3" "$2"'
        for harness, model, effort, expected in (
                ("claude", "claude-sonnet-5", "high", "--effort 'high'"),
                ("codex", "gpt-fixture", "high", 'model_reasoning_effort="high"')):
            result = subprocess.run(["bash", "-c", script, "flags", harness, model, effort],
                                    env=dict(os.environ, SCRIPT_DIR=str(script_dir)),
                                    capture_output=True, text=True, check=True)
            self.assertIn("--model '" + model + "'", result.stdout)
            self.assertIn(expected, result.stdout)
        result = subprocess.run([str(script_dir / "fm-harness.sh"), "workflow-profile",
                                 "codex", "gpt-fixture", "max"],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("would be omitted", result.stderr)
        # This is the same profile owner sourced by actual spawn, and the
        # accepted-record gate precedes its model/effort flag application.
        spawn = (script_dir / "fm-spawn.sh").read_text()
        self.assertIn('. "$SCRIPT_DIR/fm-harness-profile-lib.sh"', spawn)
        self.assertNotIn("effort_flag_for_harness() {", spawn)
        self.assertLess(spawn.index('fm_task_group_controls.py'), spawn.index('MODELFLAG=$(model_flag_for_harness'))

    def test_flag_extraction_preserves_every_existing_harness_mapping(self):
        from test_spawn_bridge import SOURCE
        pinned = (SOURCE / "bin/fm-spawn.sh").read_text()
        quote = "shell_quote() {" + pinned.split("shell_quote() {", 1)[1].split("\n}\n", 1)[0] + "\n}\n"
        start = pinned.index("model_flag_for_harness() {")
        mappings = pinned[start:pinned.index('\ncase "$LAUNCH" in', start)]
        exercise = '''for harness in claude codex opencode pi pi-signed grok kimi cursor gemini muse rovo omp agy; do
  for effort in default low medium high xhigh max; do
    model_flag_for_harness "$harness" fixture
    effort_flag_for_harness "$harness" "$effort" fixture
    printf '\\n'
  done
done
'''
        environment = dict(os.environ, SCRIPT_DIR=str(self.owner.code_root / "bin"))
        expected = subprocess.run(["bash", "-c", quote + mappings + exercise],
                                  env=environment, capture_output=True, text=True, check=True)
        actual = subprocess.run(["bash", "-c", '. "$SCRIPT_DIR/fm-harness-profile-lib.sh";\n' + exercise],
                                env=environment, capture_output=True, text=True, check=True)
        self.assertEqual(actual.stdout, expected.stdout)
        self.assertEqual(actual.stderr, expected.stderr)


if __name__ == "__main__":
    unittest.main()
