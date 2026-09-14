"""Review admission and retained evidence using real Git/controller state.

Spawn and inbox delivery are injected external owners, not Herdr/model evidence.
Each test has an isolated Linux filesystem home, project and worktree.
"""
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import test_task_group as fixtures
from fm_task_group_launch import launch_check, launch_meta, launch_overlay
from fm_task_group_store import GroupError, canonical, digest, read_json, write_json


class ReviewOwnerTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.ControllerTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.owner = self.fixture.owner
        self.attachment = self.owner.attach(
            "audit", self.fixture.package, self.fixture.project, "Review", "explicit-audit")
        self.root_meta = dict(self.fixture.root_meta, endpoint_task_id="audit")
        self.root_meta.update(self.fixture.fields(launch_meta(self.owner, "audit")))
        self.fixture.save_meta("audit", self.root_meta)

    def submit(self):
        return self.owner.submit("audit", self.root_meta["spawn_gen"], self.fixture.body)

    def completed(self):
        child = self.submit()["request"]["child"]
        return self.owner.complete(child, "s2.345.6", self.fixture.report(child))

    def cli(self, *args):
        return subprocess.run(
            [sys.executable, "-B", str(fixtures.BIN / "fm-task-group.py"),
             "--home", str(self.owner.home), *args],
            capture_output=True, text=True, timeout=30)

    def assert_first_gather_survives_replay(self, root, meta):
        child = self.owner.submit(root, meta["spawn_gen"], self.fixture.body)["request"]["child"]
        self.owner.complete(child, "s2.345.6", self.fixture.report(child))
        with patch("fm_task_group.time.time", return_value=100):
            first = self.owner.status(root, meta["spawn_gen"], gather=True)
        self.assertEqual(first["request"]["gathered_at"], 100)
        meta["spawn_gen"] = "s3.456.7"
        self.fixture.save_meta(root, meta)
        with patch("fm_task_group.time.time", return_value=200):
            repeated = self.owner.status(root, meta["spawn_gen"], gather=True)
        self.assertEqual(repeated["request"]["gathered_at"], 100)
        self.assertEqual(repeated["request"]["gathered_parent_gen"], "s3.456.7")
        self.assertEqual(repeated["request"]["child"], child)

    def test_review_repeated_gather_preserves_first_ack_and_updates_parent(self):
        self.assert_first_gather_survives_replay("audit", dict(self.root_meta))

    def test_work_repeated_gather_preserves_first_ack_and_updates_parent(self):
        self.assert_first_gather_survives_replay("root", dict(self.fixture.root_meta))

    def test_review_requires_explicit_pair_before_persistent_task_mutation(self):
        for primitive, policy in (("Review", "none"), ("Work", "explicit-audit"),
                                  ("Other", "none"), ("Review", None)):
            with self.subTest(primitive=primitive, policy=policy):
                with self.assertRaisesRegex(GroupError, "admission pairs"):
                    self.owner.attach("denied", self.fixture.package, self.fixture.project,
                                      primitive, policy)
                self.assertFalse(self.owner.task("denied").exists())
        self.assertEqual(self.fixture.calls, [])

    def test_review_refuses_other_platform_before_persistent_task_mutation(self):
        with patch("fm_task_group_primitives.sys.platform", "darwin"):
            with self.assertRaisesRegex(GroupError, "requires Linux"):
                self.owner.attach("denied", self.fixture.package, self.fixture.project,
                                  "Review", "explicit-audit")
        self.assertFalse(self.owner.task("denied").exists())

    def test_reattach_requires_same_primitive_policy_and_snapshot(self):
        first = self.owner.attach("fresh", self.fixture.package, self.fixture.project,
                                  "Review", "explicit-audit")
        self.assertEqual(first, self.owner.attach(
            "fresh", self.fixture.package, self.fixture.project, "Review", "explicit-audit"))
        before = (self.owner.group("fresh") / "attachment.json").read_bytes()
        with self.assertRaisesRegex(GroupError, "immutable"):
            self.owner.attach("fresh", self.fixture.package, self.fixture.project)
        with self.assertRaisesRegex(GroupError, "admission pairs"):
            self.owner.attach("fresh", self.fixture.package, self.fixture.project, "Review")
        self.assertEqual(before, (self.owner.group("fresh") / "attachment.json").read_bytes())
        self.assertNotIn("review_policy", self.fixture.attachment)

    def test_fresh_reviewer_uses_inherited_controls_frozen_commit_and_review_guidance(self):
        self.root_meta.update(harness="codex", model="gpt-5.5", effort="high")
        self.fixture.save_meta("audit", self.root_meta)
        value = self.submit()
        request = value["request"]
        child = request["child"]
        self.assertEqual(value["scope"], "local-readonly-review")
        self.assertEqual(request["state"], "launched")
        self.assertEqual(request["primitive"], "Review")
        self.assertEqual(request["review_policy"], "explicit-audit")
        self.assertEqual(request["input_commit"], self.attachment["input_commit"])
        self.assertEqual(request["package_digest"], self.attachment["package_digest"])
        meta = self.owner.meta(child)
        self.assertEqual(meta["task_group_primitive"], "Review")
        self.assertEqual((meta["harness"], meta["model"], meta["effort"]), ("codex", "gpt-5.5", "high"))
        self.assertNotEqual(Path(meta["worktree"]), self.fixture.project)
        brief = (self.owner.task(child) / "brief.md").read_text()
        for text in ("fresh Review component", "relevant Review guidance",
                     "do not make or delegate repairs", self.attachment["input_commit"]):
            self.assertIn(text, brief)
            self.assertIn(text, launch_overlay(self.owner, child))
        self.assertNotIn("Make guidance", brief)
        self.assertEqual(self.fixture.calls, [child])
        with self.assertRaisesRegex(GroupError, "relaunch"):
            launch_check(self.owner, child, "scout", "herdr", "codex", self.fixture.project)

    def test_review_root_overlay_regenerates_explicit_client_and_audit_delivery(self):
        overlay = launch_overlay(self.owner, "audit")
        self.assertIn("/skills/orch-review/SKILL.md", overlay)
        for verb in ("submit", "status", "gather"):
            self.assertIn("--primitive Review " + verb, overlay)
        self.assertIn("Read the complete retained report and result identity before gather", overlay)
        self.assertIn("normal scout report", overlay)
        self.assertIn("Findings authorize no repair pass", overlay)
        self.root_meta["spawn_gen"] = "s3.456.7"
        self.fixture.save_meta("audit", self.root_meta)
        launch_check(self.owner, "audit", "scout", "herdr", "claude", self.fixture.project)
        self.assertEqual(overlay, launch_overlay(self.owner, "audit"))
        work = launch_overlay(self.owner, "root")
        self.assertIn("Stage 1 permits exactly one read-only Work", work)
        self.assertNotIn("--primitive Review", work)

    def test_root_metadata_cannot_downgrade_or_omit_review(self):
        for primitive in (None, "Work"):
            value = dict(self.root_meta)
            if primitive is None:
                value.pop("task_group_primitive")
            else:
                value["task_group_primitive"] = primitive
            self.fixture.save_meta("audit", value)
            with self.subTest(primitive=primitive), self.assertRaisesRegex(GroupError, "metadata primitive"):
                self.submit()
            with self.assertRaisesRegex(GroupError, "metadata primitive"):
                launch_check(self.owner, "audit", "scout", "herdr", "claude", self.fixture.project)
        self.assertIsNone(self.owner.request("audit"))
        self.assertEqual(self.fixture.calls, [])

    def test_component_metadata_cannot_downgrade_or_omit_review(self):
        child = self.submit()["request"]["child"]
        original = self.owner.meta(child)
        for primitive in (None, "Work"):
            value = dict(original)
            if primitive is None:
                value.pop("task_group_primitive")
            else:
                value["task_group_primitive"] = primitive
            self.fixture.save_meta(child, value)
            with self.subTest(primitive=primitive), self.assertRaisesRegex(GroupError, "metadata primitive"):
                self.owner.complete(child, "s2.345.6", self.fixture.report(child))
            with self.assertRaisesRegex(GroupError, "metadata primitive"):
                self.owner.waiting(child)

    def test_saved_request_primitive_and_policy_are_immutable(self):
        request = self.submit()["request"]
        for key, changed in (("primitive", "Work"), ("review_policy", "none"),
                             ("primitive", None), ("review_policy", None)):
            corrupted = dict(request)
            if changed is None:
                corrupted.pop(key)
            else:
                corrupted[key] = changed
            write_json(self.owner.group("audit") / "request.json", corrupted)
            with self.subTest(key=key, changed=changed), self.assertRaisesRegex(GroupError, "primitive or review policy"):
                self.owner.status("audit", self.root_meta["spawn_gen"])
            with self.assertRaises(GroupError):
                self.owner.waiting("audit")
        self.assertEqual(len(self.fixture.calls), 1)

    def test_work_request_and_metadata_cannot_authorize_review(self):
        for key, value in (("primitive", "Review"), ("review_policy", "explicit-audit")):
            with self.subTest(key=key), self.assertRaisesRegex(GroupError, "only request_id and assignment"):
                self.owner.submit("root", self.fixture.root_meta["spawn_gen"],
                                  dict(self.fixture.body, **{key: value}))
        self.assertIsNone(self.owner.request("root"))
        original = self.fixture.root_meta
        self.fixture.save_meta("root", dict(original, task_group_primitive="Review"))
        with self.assertRaisesRegex(GroupError, "metadata primitive"):
            self.fixture.submit()
        self.fixture.save_meta("root", original)
        request = self.fixture.submit()["request"]
        self.assertNotIn("primitive", request)
        self.assertNotIn("review_policy", request)
        request.update(primitive="Review", review_policy="explicit-audit")
        write_json(self.owner.group("root") / "request.json", request)
        with self.assertRaisesRegex(GroupError, "primitive or review policy"):
            self.owner.status("root", original["spawn_gen"])

    def test_review_result_retains_identity_and_gather_controls_cleanup(self):
        value = self.completed()
        result = value["result"]
        child = result["child"]
        self.assertEqual(result["primitive"], "Review")
        self.assertEqual(result["review_policy"], "explicit-audit")
        self.assertEqual(result["input_commit"], self.attachment["input_commit"])
        self.assertEqual(result["package_digest"], self.attachment["package_digest"])
        self.assertTrue(result["readonly"])
        self.assertEqual(result["component_meta"]["task_group_primitive"], "Review")
        self.assertEqual(result["parent_at_completion"]["task_group_primitive"], "Review")
        self.assertEqual(len(self.fixture.notices), 1)
        self.assertFalse(self.owner.waiting(child)["cleanup_allowed"])
        self.assertTrue(self.owner.waiting("audit")["result_ready"])
        self.owner.status("audit", self.root_meta["spawn_gen"], gather=True)
        self.assertTrue(self.owner.waiting(child)["cleanup_allowed"])
        self.assertFalse((self.owner.home / "state/audit.status").exists())
        with self.assertRaisesRegex(GroupError, "only one"):
            self.owner.submit("audit", self.root_meta["spawn_gen"],
                              dict(self.fixture.body, request_id="second-audit"))

    def test_forged_result_identity_cannot_be_gathered_even_with_recomputed_digest(self):
        complete = self.completed()
        for key, value in (("primitive", "Work"), ("review_policy", "none")):
            result = dict(complete["result"], **{key: value})
            record = dict(complete["request"], result_digest=digest(canonical(result)))
            write_json(Path(complete["result_path"]), result)
            write_json(self.owner.group("audit") / "request.json", record)
            with self.subTest(key=key), self.assertRaisesRegex(GroupError, "primitive or review policy"):
                self.owner.status("audit", self.root_meta["spawn_gen"], gather=True)
            with self.assertRaises(GroupError):
                self.owner.waiting("audit")

    def test_stale_generations_refuse_and_new_root_gathers_same_reviewer(self):
        accepted = self.submit()
        child = accepted["request"]["child"]
        report = self.fixture.report(child)
        with self.assertRaisesRegex(GroupError, "stale"):
            self.owner.complete(child, "old-child", report)
        self.root_meta["spawn_gen"] = "s3.456.7"
        self.fixture.save_meta("audit", self.root_meta)
        with self.assertRaisesRegex(GroupError, "stale parent"):
            self.owner.submit("audit", "s1.123.4", self.fixture.body)
        self.assertEqual(self.submit()["request"]["child"], child)
        completed = self.owner.complete(child, "s2.345.6", report)
        gathered = self.owner.status("audit", "s3.456.7", gather=True)
        self.assertEqual(gathered["result"], completed["result"])
        self.assertEqual(gathered["request"]["accepted_parent_gen"], "s1.123.4")
        self.assertEqual(gathered["request"]["gathered_parent_gen"], "s3.456.7")
        self.assertEqual(self.fixture.calls, [child])

    def test_review_does_not_accept_dirty_or_changed_frozen_input(self):
        (self.fixture.project / "input.txt").write_text("uncommitted candidate")
        with self.assertRaisesRegex(GroupError, "dirty"):
            self.submit()
        self.fixture.git("add", "input.txt")
        self.fixture.git("commit", "-qm", "new candidate")
        with self.assertRaisesRegex(GroupError, "commit changed"):
            self.submit()
        self.assertEqual(self.fixture.calls, [])
        self.assertIsNone(self.owner.request("audit"))


    def test_review_saved_target_identity_must_match_attachment(self):
        request = self.submit()["request"]
        for key in ("input_commit", "package_digest"):
            write_json(self.owner.group("audit") / "request.json", dict(request, **{key: "different"}))
            with self.subTest(key=key), self.assertRaisesRegex(GroupError, "input or package identity"):
                self.owner.status("audit", self.root_meta["spawn_gen"])
        self.assertEqual(len(self.fixture.calls), 1)

    def test_review_repairs_cannot_be_published_as_a_clean_audit(self):
        child = self.submit()["request"]["child"]
        report = self.fixture.report(child)
        (Path(self.owner.meta(child)["worktree"]) / "input.txt").write_text("repair")
        with self.assertRaisesRegex(GroupError, "dirty"):
            self.owner.complete(child, "s2.345.6", report)
        self.assertEqual(self.owner.request("audit")["state"], "launched")
        self.assertFalse(self.owner.waiting(child)["cleanup_allowed"])

    def test_cli_capabilities_and_explicit_admission(self):
        protocol = self.cli("protocol")
        self.assertEqual(protocol.returncode, 0, protocol.stderr)
        value = json.loads(protocol.stdout)
        self.assertEqual(value["version"], 1)
        self.assertEqual(value["scope"], "local-readonly-work")
        self.assertEqual(value["primitives"], ["Work", "Review"])
        self.assertEqual(value["review_policies"], ["explicit-audit"])
        arguments = ("attach", "cli-audit", "--package", str(self.fixture.package),
                     "--project", str(self.fixture.project), "--primitive", "Review")
        denied = self.cli(*arguments)
        self.assertEqual(denied.returncode, 2, denied.stderr)
        self.assertIn("admission pairs", json.loads(denied.stderr)["error"])
        self.assertFalse(self.owner.task("cli-audit").exists())
        accepted = self.cli(*arguments, "--review-policy", "explicit-audit")
        self.assertEqual(accepted.returncode, 0, accepted.stderr)
        self.assertEqual(json.loads(accepted.stdout)["review_policy"], "explicit-audit")
        metadata = self.cli("launch-meta", "cli-audit")
        self.assertEqual(metadata.returncode, 0, metadata.stderr)
        self.assertEqual(self.fixture.fields(metadata.stdout)["task_group_primitive"], "Review")


if __name__ == "__main__":
    unittest.main()
