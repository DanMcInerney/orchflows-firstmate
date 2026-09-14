"""Controller boundary tests. Injected spawn/notice are NOT live fleet evidence.

Real Git fixtures exercise attachment and retained-result custody. The injected
external FirstMate owner publishes explicit metadata fixtures without starting
Herdr or a harness. Shell parent-lock integration is a separate test surface.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest

BIN = Path(__file__).resolve().parents[1] / "overlay" / "bin"
sys.path.insert(0, str(BIN))
from fm_task_group import TaskGroups
from fm_task_group_launch import launch_check, launch_meta, launch_overlay
from fm_task_group_store import GroupError, read_json, write_json


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="firstmate-group-test-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name).resolve()
        self.home = self.base / "home"
        (self.home / "data").mkdir(parents=True)
        (self.home / "state").mkdir()
        self.project = self.base / "project"
        self.project.mkdir()
        self.git("init", "-q")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "user.name", "Fixture")
        (self.project / "input.txt").write_text("Two facts live here.\n", encoding="utf-8")
        self.git("add", "input.txt")
        self.git("commit", "-qm", "fixture input")
        self.package = self.base / "package"
        self.package.mkdir()
        (self.package / "plugin.json").write_text(json.dumps({"name": "orchflows-firstmate", "version": "test"}))
        (self.package / "guidance.md").write_text("Read only; report evidence.\n")
        self.calls = []
        self.notices = []
        self.owner = TaskGroups(self.home, BIN.parent, self.fixture_spawn, self.fixture_notice)
        self.attachment = self.owner.attach("root", self.package, self.project)
        launch_check(self.owner, "root", "scout", "herdr", "claude", self.project)
        self.root_meta = {"endpoint_task_id": "root", "spawn_gen": "s1.123.4", "backend": "herdr",
                          "kind": "scout", "harness": "claude", "project": str(self.project),
                          "worktree": str(self.project), "model": "default", "effort": "default",
                          "herdr_session": "lab-fixture"}
        self.root_meta.update(self.fields(launch_meta(self.owner, "root")))
        self.save_meta("root", self.root_meta)
        self.body = {"request_id": "find-facts", "assignment": "Read input.txt and report its two facts."}

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.project), *args], check=True, capture_output=True).stdout.decode().strip()

    @staticmethod
    def fields(text):
        return dict(line.split("=", 1) for line in text.splitlines())

    def save_meta(self, task, value):
        (self.home / "state" / f"{task}.meta").write_text("".join(f"{key}={item}\n" for key, item in value.items()), encoding="utf-8")

    def fixture_notice(self, *args):
        self.notices.append(args)
        return SimpleNamespace(returncode=0)

    def fixture_spawn(self, root, generation, child, project, harness, model, effort):
        # A request and non-placeholder role brief must precede any owner dispatch.
        record = read_json(self.owner.group(root) / "request.json")
        self.assertEqual(record["state"], "launching")
        self.assertEqual(record["accepted_parent_gen"], generation)
        brief = (self.owner.task(child) / "brief.md").read_text()
        self.assertIn(self.body["assignment"], brief)
        self.assertIn("FirstMate task-group component completion contract", brief)
        self.calls.append(child)
        launch_check(self.owner, child, "scout", "herdr", harness, project)
        worktree = self.base / (child + "-worktree")
        self.git("worktree", "add", "--detach", str(worktree), self.attachment["input_commit"])
        launch_check(self.owner, child, "scout", "herdr", harness, project, worktree)
        tasktmp = self.base / (child + "-tmp")
        tasktmp.mkdir()
        value = {"endpoint_task_id": child, "spawn_gen": "s2.345.6", "backend": "herdr", "kind": "scout",
                 "harness": harness, "model": model, "effort": effort, "project": str(project),
                 "worktree": str(worktree), "tasktmp": str(tasktmp), "herdr_session": "lab-fixture",
                 "herdr_workspace_id": "fixture-workspace", "herdr_tab_id": "fixture-tab",
                 "herdr_pane_id": "fixture-pane", "window": "fixture-window"}
        value.update(self.fields(launch_meta(self.owner, child)))
        self.save_meta(child, value)
        return SimpleNamespace(returncode=0)

    def submit(self):
        return self.owner.submit("root", self.root_meta["spawn_gen"], self.body)

    def report(self, child):
        path = Path(self.owner.meta(child)["tasktmp"]) / "report.md"
        path.write_text("input.txt:1 contains the inspected fixture evidence.\n", encoding="utf-8")
        return path

    def completed(self):
        child = self.submit()["request"]["child"]
        return self.owner.complete(child, "s2.345.6", self.report(child))

    def test_replay_returns_same_child_and_changed_body_is_rejected(self):
        first = self.submit()
        self.assertEqual(self.submit()["request"]["child"], first["request"]["child"])
        changed = dict(self.body, assignment="Different assignment")
        with self.assertRaisesRegex(GroupError, "different body"):
            self.owner.submit("root", self.root_meta["spawn_gen"], changed)
        self.assertEqual(len(self.calls), 1)

    def test_one_assignment_per_attachment_even_after_gather(self):
        self.completed()
        self.owner.status("root", self.root_meta["spawn_gen"], gather=True)
        with self.assertRaisesRegex(GroupError, "only one"):
            self.owner.submit("root", self.root_meta["spawn_gen"], dict(self.body, request_id="second"))
        self.assertEqual(len(self.calls), 1)

    def test_stale_parent_rejected_but_relaunched_parent_reconciles(self):
        first = self.submit()
        self.root_meta["spawn_gen"] = "s3.456.7"
        self.save_meta("root", self.root_meta)
        with self.assertRaisesRegex(GroupError, "stale parent"):
            self.owner.status("root", "s1.123.4")
        replay = self.submit()
        self.assertEqual(replay["request"]["accepted_parent_gen"], "s1.123.4")
        self.assertEqual(first["request"]["child"], replay["request"]["child"])
        self.assertEqual(len(self.calls), 1)
        launch_check(self.owner, "root", "scout", "herdr", "claude", self.project)

    def test_unsupported_parent_backend_kind_harness_role(self):
        for key, wrong in (("backend", "tmux"), ("kind", "ship"), ("harness", "other"), ("task_group_role", "component")):
            with self.subTest(key=key):
                self.save_meta("root", dict(self.root_meta, **{key: wrong}))
                with self.assertRaises(GroupError):
                    self.submit()
        self.assertEqual(self.calls, [])

    def test_unknown_request_axes_rejected_before_acceptance(self):
        for extra in ({"primitive": "Review"}, {"readonly": False}, {"model": "other"}):
            with self.subTest(extra=extra), self.assertRaises(GroupError):
                self.owner.submit("root", self.root_meta["spawn_gen"], dict(self.body, **extra))
        self.assertIsNone(self.owner.request("root"))

    def test_input_changes_prevent_admission(self):
        (self.project / "input.txt").write_text("changed")
        with self.assertRaisesRegex(GroupError, "dirty"):
            self.submit()
        self.git("add", "input.txt")
        self.git("commit", "-qm", "changed input")
        with self.assertRaisesRegex(GroupError, "commit changed"):
            self.submit()
        self.assertEqual(self.calls, [])

    def test_origin_rejected_and_original_package_changes_do_not_mutate_snapshot(self):
        self.git("remote", "add", "origin", "https://example.invalid/project.git")
        with self.assertRaisesRegex(GroupError, "without origin"):
            self.submit()
        self.git("remote", "remove", "origin")
        (self.package / "guidance.md").write_text("new default package")
        self.assertEqual(self.submit()["attachment"]["package_digest"], self.attachment["package_digest"])

    def test_snapshot_tamper_is_rejected(self):
        path = Path(self.attachment["package_path"]) / "guidance.md"
        path.chmod(0o644)
        path.write_text("tampered")
        with self.assertRaisesRegex(GroupError, "snapshot changed"):
            self.submit()
        self.assertEqual(self.calls, [])

    def test_failed_spawn_is_retained_uncertain_without_second_dispatch(self):
        def failure(*args):
            self.calls.append(args[2])
            return SimpleNamespace(returncode=1)
        self.owner.spawn = failure
        first = self.submit()
        self.assertEqual(first["request"]["state"], "uncertain")
        self.assertEqual(self.submit()["request"]["child"], first["request"]["child"])
        self.assertEqual(len(self.calls), 1)
        self.assertTrue(self.owner.waiting("root")["pending"])
        self.assertFalse((self.home / "state" / (first["request"]["child"] + ".meta")).exists())

    def test_timeout_and_success_without_bound_meta_remain_uncertain(self):
        def timeout(*args):
            self.calls.append(args[2])
            raise subprocess.TimeoutExpired("FirstMate fixture boundary", 300)
        self.owner.spawn = timeout
        self.assertEqual(self.submit()["request"]["state"], "uncertain")
        self.submit()
        self.assertEqual(len(self.calls), 1)

    def test_success_exit_without_metadata_is_not_a_successful_launch(self):
        self.owner.spawn = lambda *args: SimpleNamespace(returncode=0)
        self.assertEqual(self.submit()["request"]["state"], "uncertain")

    def test_forged_component_binding_or_controls_is_rejected(self):
        original = self.owner.spawn
        def mismatch(*args):
            result = original(*args)
            child = args[2]
            value = self.owner.meta(child)
            value["task_group_parent"] = "some-other-root"
            self.save_meta(child, value)
            return result
        self.owner.spawn = mismatch
        self.assertEqual(self.submit()["request"]["state"], "uncertain")

    def test_completion_retains_report_exact_identity_and_requires_gather(self):
        value = self.completed()
        child = value["request"]["child"]
        self.report(child).unlink()
        self.assertTrue(Path(value["report_path"]).is_file())
        self.assertEqual(value["result"]["component_meta"]["spawn_gen"], "s2.345.6")
        self.assertEqual(value["result"]["package_digest"], self.attachment["package_digest"])
        self.assertIsNone(value["result"]["native_session_id"])
        self.assertTrue(self.owner.waiting("root")["pending"])
        self.assertFalse(self.owner.waiting(child)["cleanup_allowed"])
        gathered = self.owner.status("root", self.root_meta["spawn_gen"], gather=True)
        self.assertTrue(gathered["request"]["gathered"])
        self.assertTrue(self.owner.waiting(child)["cleanup_allowed"])
        self.assertFalse((self.home / "state" / "root.status").exists())
        self.assertEqual(len(self.notices), 1)

    def test_result_tamper_prevents_gather_and_cleanup(self):
        value = self.completed()
        Path(value["report_path"]).write_text("tampered retained report")
        with self.assertRaisesRegex(GroupError, "integrity"):
            self.owner.status("root", self.root_meta["spawn_gen"], gather=True)
        with self.assertRaisesRegex(GroupError, "integrity"):
            self.owner.waiting("root")

    def test_stale_child_report_and_dirty_child_are_refused(self):
        child = self.submit()["request"]["child"]
        report = self.report(child)
        with self.assertRaisesRegex(GroupError, "stale"):
            self.owner.complete(child, "wrong-generation", report)
        (Path(self.owner.meta(child)["worktree"]) / "input.txt").write_text("write forbidden")
        with self.assertRaisesRegex(GroupError, "dirty"):
            self.owner.complete(child, "s2.345.6", report)
        self.assertEqual(self.owner.request("root")["state"], "launched")

    def test_changed_endpoint_same_generation_cannot_complete(self):
        child = self.submit()["request"]["child"]
        report = self.report(child)
        value = self.owner.meta(child)
        value["herdr_pane_id"] = "replacement-pane"
        self.save_meta(child, value)
        with self.assertRaisesRegex(GroupError, "identity changed"):
            self.owner.complete(child, "s2.345.6", report)

    def test_symlink_report_is_rejected(self):
        child = self.submit()["request"]["child"]
        actual = self.base / "actual-report.md"
        actual.write_text("external report")
        link = Path(self.owner.meta(child)["tasktmp"]) / "linked.md"
        try:
            link.symlink_to(actual)
        except (OSError, NotImplementedError):
            self.skipTest("host does not allow this fixture to create a symlink")
        with self.assertRaisesRegex(GroupError, "symlink"):
            self.owner.complete(child, "s2.345.6", link)

    def test_new_parent_generation_gathers_old_assignment(self):
        complete = self.completed()
        self.root_meta["spawn_gen"] = "s3.456.7"
        self.save_meta("root", self.root_meta)
        value = self.owner.status("root", "s3.456.7", gather=True)
        self.assertEqual(value["request"]["accepted_parent_gen"], "s1.123.4")
        self.assertEqual(value["report_path"], complete["report_path"])
        self.assertEqual(value["request"]["gathered_parent_gen"], "s3.456.7")

    def test_reports_outside_tasktmp_empty_or_oversize_are_rejected(self):
        child = self.submit()["request"]["child"]
        outside = self.base / "outside.md"
        outside.write_text("evidence")
        with self.assertRaisesRegex(GroupError, "within recorded tasktmp"):
            self.owner.complete(child, "s2.345.6", outside)
        report = self.report(child)
        for data in (b"", b" \n", b"x" * (512 * 1024 + 1)):
            report.write_bytes(data)
            with self.assertRaises(GroupError):
                self.owner.complete(child, "s2.345.6", report)

    def test_component_cannot_submit_or_relaunch(self):
        child = self.submit()["request"]["child"]
        with self.assertRaises(GroupError):
            self.owner.submit(child, "s2.345.6", self.body)
        with self.assertRaisesRegex(GroupError, "relaunch"):
            launch_check(self.owner, child, "scout", "herdr", "claude", self.project)

    def test_hooks_noop_ordinary_but_missing_bound_attachment_fails(self):
        launch_check(self.owner, "ordinary", "ship", "tmux", "other", self.project)
        self.assertEqual(launch_meta(self.owner, "ordinary"), "")
        self.assertEqual(launch_overlay(self.owner, "ordinary"), "")
        self.assertFalse(self.owner.waiting("ordinary")["attached"])
        self.save_meta("missing", {"task_group_role": "root"})
        with self.assertRaisesRegex(GroupError, "no durable binding"):
            launch_check(self.owner, "missing", "scout", "herdr", "claude", self.project)
        with self.assertRaisesRegex(GroupError, "no durable binding"):
            self.owner.waiting("missing")

    def test_codex_controls_are_inherited(self):
        self.root_meta.update(harness="codex", model="gpt-5.5", effort="high")
        self.save_meta("root", self.root_meta)
        value = self.submit()
        self.assertEqual(value["request"]["state"], "launched")
        self.assertEqual(value["request"]["launch_meta"]["harness"], "codex")
        self.assertEqual(value["request"]["launch_meta"]["effort"], "high")

    def test_notification_failure_preserves_result_and_can_retry(self):
        self.owner.notify = lambda *args: SimpleNamespace(returncode=1)
        value = self.completed()
        self.assertTrue(value["request"]["notification_pending"])
        self.assertEqual(value["request"]["state"], "complete")
        self.owner.notify = self.fixture_notice
        child = value["request"]["child"]
        value = self.owner.complete(child, "s2.345.6", self.report(child))
        self.assertFalse(value["request"]["notification_pending"])

    def test_invalid_paths_identifiers_and_duplicate_json_are_rejected(self):
        with self.assertRaises(GroupError):
            self.owner.status("../escape", "s1")
        path = self.base / "duplicate.json"
        path.write_text('{"request_id":"one","request_id":"two","assignment":"read"}')
        with self.assertRaisesRegex(GroupError, "duplicate"):
            read_json(path)


if __name__ == "__main__":
    unittest.main()
