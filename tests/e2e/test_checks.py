"""Fast checks of the E2E oracle's failure detection; no model calls."""
import json
from pathlib import Path
import tempfile
import unittest

from evidence import Collector, completed, metadata, task_sessions
from oracle import ArtifactOracle, generated, money
from assertions import library_checks, reviewed_revisions


class ArtifactFailureDetection(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.oracle = ArtifactOracle(self.root, self.root / "checks")

    def fake_cli(self, stdout, status=0, stderr=""):
        (self.root / "moneylog.py").write_text(
            f"import sys\nsys.stdout.write({stdout!r})\nsys.stderr.write({stderr!r})\nraise SystemExit({status})\n")

    def test_wrong_result_cannot_pass_with_success_exit(self):
        self.fake_cli('{"a":"0.31"}\n')
        self.oracle.success("exact", "", {"a": "0.30"})
        self.assertFalse(self.oracle.result()["passed"])

    def test_duplicate_or_unsorted_keys_fail(self):
        for text in ('{"b":"1.00","a":"2.00"}\n',
                     '{"a":"2.00","a":"2.00","b":"1.00"}\n'):
            with self.subTest(text=text):
                self.oracle.checks.clear()
                self.fake_cli(text)
                self.oracle.success("ordered", "", {"a": "2.00", "b": "1.00"})
                self.assertFalse(self.oracle.result()["passed"])

    def test_partial_stdout_on_failure_is_rejected(self):
        self.fake_cli('{"a":"1.00"}\n', status=2, stderr="Invalid amount on line 3\n")
        self.oracle.failure("atomic", "", line=3)
        self.assertFalse(self.oracle.result()["passed"])

    def test_wrong_line_is_rejected(self):
        self.fake_cli("", status=2, stderr="Invalid amount on line 2\n")
        self.oracle.failure("physical line", "", line=4)
        self.assertFalse(self.oracle.result()["passed"])

    def test_correct_observation_passes(self):
        self.fake_cli('{"a":"0.30"}\n')
        self.oracle.success("exact", "", {"a": "0.30"})
        self.assertTrue(self.oracle.result()["passed"])

    def test_valid_json_of_wrong_type_is_a_failure_not_a_crash(self):
        for value in ("1\n", "null\n", '"wrong"\n', '[1,2]\n'):
            with self.subTest(value=value):
                self.oracle.checks.clear()
                self.fake_cli(value)
                self.oracle.success("object required", "", {"a": "0.30"})
                self.assertFalse(self.oracle.result()["passed"])

    def test_total_duplicate_and_unsorted_nested_keys_fail(self):
        self.fake_cli('{"accounts":{"b":"1.00","a":"2.00"},"total":"3.00"}\n')
        self.oracle.success("total", "", {"accounts": {"a": "2.00", "b": "1.00"}, "total": "3.00"}, ["--total", "-"])
        self.assertFalse(self.oracle.result()["passed"])

    def test_library_checker_rejects_pins_and_nonobject_manifests(self):
        library = self.root / "libraries/cashflow"
        library.mkdir(parents=True)
        (library / "plugin.json").write_text('{"name":"cashflow","version":"1","model":"pinned"}')
        checks = library_checks(self.root)
        self.assertFalse(next(c["passed"] for c in checks if c["name"] == "plugin.json no model or effort fields"))
        (library / "plugin.json").write_text("[]")
        checks = library_checks(self.root)
        self.assertFalse(next(c["passed"] for c in checks if c["name"] == "manifest plugin.json"))

    def test_generated_fixture_repeatable_and_integer_exact(self):
        self.assertEqual(generated(7), generated(7))
        self.assertNotEqual(generated(7), generated(8))
        self.assertEqual(money(-1), "-0.01")
        self.assertEqual(money(10**40 + 1), str(10**38) + ".01")


class CompletionEvidence(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.lab = type("Lab", (), {"root": root, "config": {"primary_session": "test"}})()
        directory = root / "evidence/transcripts/claude"
        directory.mkdir(parents=True)
        self.path = directory / "test.jsonl"

    def write(self, role, kind, text):
        self.path.write_text(json.dumps({"type": role, "message": {
            "content": [{"type": kind, "text": text}]}}) + "\n")

    def test_echoed_request_and_tool_output_do_not_complete(self):
        for role, kind in (("user", "text"), ("assistant", "tool_use"), ("user", "tool_result")):
            with self.subTest(role=role, kind=kind):
                self.write(role, kind, "E2E_CASE_DONE dynamic")
                self.assertFalse(completed(self.lab, "dynamic"))

    def test_only_standalone_assistant_marker_completes(self):
        self.write("assistant", "text", "Do not print E2E_CASE_DONE dynamic yet")
        self.assertFalse(completed(self.lab, "dynamic"))
        self.write("assistant", "text", "Delivered.\nE2E_CASE_DONE dynamic\n")
        self.assertTrue(completed(self.lab, "dynamic"))
        self.assertFalse(completed(self.lab, "saved"))

    def test_absent_model_and_effort_remain_unknown(self):
        fields = metadata("harness=claude\nkind=ship\n")
        self.assertNotIn("model", fields)
        self.assertNotIn("effort", fields)

    def test_review_revision_accepts_abbreviations_without_matching_base(self):
        self.assertEqual(reviewed_revisions(
            '**Reviewed commit:** `66e7785`, base `e6f94f7`.'), {"66e7785"})
        sha = "a" * 40
        self.assertEqual(reviewed_revisions(f'**Commit reviewed:** `{sha}`'), {sha})
        self.assertEqual(reviewed_revisions(f'Base commit: `{sha}`'), set())

    def test_completion_from_previous_attempt_is_rejected(self):
        self.write("assistant", "text", "E2E_CASE_DONE dynamic")
        record = json.loads(self.path.read_text())
        record["timestamp"] = "2026-09-17T10:00:00Z"
        self.path.write_text(json.dumps(record) + "\n")
        (self.lab.root / "events.jsonl").write_text(json.dumps({
            "time": 1789660800, "kind": "case-start", "case": "dynamic"}) + "\n")
        self.assertFalse(completed(self.lab, "dynamic"))

    def test_transcript_scope_uses_identity_not_a_path_mentioned_in_chat(self):
        collector = Collector(self.lab)
        unrelated = json.dumps({"cwd": "/unrelated", "message": {"content": str(self.lab.root)}})
        self.assertFalse(collector.belongs_to_lab(unrelated))
        own = json.dumps({"cwd": str(self.lab.root / "user-home/worktree")})
        self.assertTrue(collector.belongs_to_lab(own))

    def test_reused_worktree_does_not_mix_worker_profiles(self):
        plan = {"worktree": "/pool/1", "spawn_gen": "s100.1.1"}
        work = {"worktree": "/pool/1", "spawn_gen": "s200.1.1"}
        routing = {"tasks": [{"task_id": "plan", "metadata": plan}, {"task_id": "work", "metadata": work}],
                   "claude_sessions": {
                       "a": {"cwd": "/pool/1", "first_time": "1970-01-01T00:01:41Z", "native_efforts": ["high"]},
                       "b": {"cwd": "/pool/1", "first_time": "1970-01-01T00:03:21Z", "native_efforts": ["low"]}}}
        self.assertEqual(task_sessions(routing, "plan", plan), [routing["claude_sessions"]["a"]])
        self.assertEqual(task_sessions(routing, "work", work), [routing["claude_sessions"]["b"]])


if __name__ == "__main__":
    unittest.main()
