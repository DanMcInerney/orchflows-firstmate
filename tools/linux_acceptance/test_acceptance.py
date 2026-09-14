"""Driver checks: private auth, result acceptance and native read ordering."""
from argparse import Namespace
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import unittest

from .evidence import assess, read_order
from .runtime import Runtime, access_token, linux_dev


class AcceptanceChecks(unittest.TestCase):
    def args(self, **kwargs):
        return Namespace(access_token_expires_at=None, claude_access_token_file=None,
                         timeout=120, **kwargs)

    def test_environment_token_is_not_in_auth_receipt(self):
        token, expiry, receipt = access_token(self.args(), {"CLAUDE_CODE_OAUTH_TOKEN": "private-synthetic-token"})
        self.assertEqual(token, "private-synthetic-token")
        self.assertIsNone(expiry)
        self.assertNotIn(token, json.dumps(receipt))
        self.assertFalse(receipt["credential_file_copied"])

    def test_cache_is_read_access_token_only_and_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "credentials.json"
            original = json.dumps({"claudeAiOauth": {"accessToken": "access-test-value",
                                                   "refreshToken": "refresh-test-value",
                                                   "expiresAt": (time.time() + 1500) * 1000}})
            path.write_text(original)
            args = self.args()
            args.claude_access_token_file = path
            token, _, receipt = access_token(args, {})
            self.assertEqual(token, "access-test-value")
            self.assertEqual(path.read_text(), original)
            self.assertNotIn("refresh-test-value", json.dumps(receipt))
            self.assertEqual(list(Path(directory).iterdir()), [path])

    def test_symlink_cache_and_ambiguous_auth_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "source"
            path.write_text("{}")
            link = Path(directory) / "link"
            link.symlink_to(path)
            args = self.args()
            args.claude_access_token_file = link
            with self.assertRaises(ValueError):
                access_token(args, {})
            with self.assertRaises(ValueError):
                access_token(args, {"CLAUDE_CODE_OAUTH_TOKEN": "synthetic"})

    def test_insufficient_and_nonfinite_expiration_refused(self):
        args = self.args()
        for expiration in (time.time() + 5, float("inf"), float("nan")):
            args.access_token_expires_at = expiration
            with self.assertRaises(ValueError):
                access_token(args, {"CLAUDE_CODE_OAUTH_TOKEN": "synthetic"})

    def test_token_is_scrubbed_from_written_logs(self):
        with tempfile.TemporaryDirectory() as directory:
            runtime = Runtime.__new__(Runtime)
            runtime.secrets = ["synthetic-secret"]
            path = Path(directory) / "log"
            runtime.write(path, "command reported synthetic-secret")
            self.assertEqual(path.read_text(), "command reported [redacted]")

    def test_socket_paths_fit_linux_and_long_paths_fail_before_launch(self):
        with tempfile.TemporaryDirectory(prefix="oa-", dir="/tmp") as directory:
            runtime = Runtime.__new__(Runtime)
            runtime.env = {"XDG_CONFIG_HOME": str(Path(directory) / "c")}
            session = "fm-lab-review-123456-12345"
            runtime.validate_session_paths(session)
            parent = Path(runtime.env["XDG_CONFIG_HOME"]) / "herdr/sessions" / session
            parent.mkdir(parents=True)
            for name in ("herdr.sock", "herdr-client.sock"):
                with socket.socket(socket.AF_UNIX) as sock:
                    sock.bind(str(parent / name))
            runtime.env["XDG_CONFIG_HOME"] = str(Path(directory) / ("long" * 30))
            with self.assertRaisesRegex(ValueError, "shorter --work-root"):
                runtime.validate_session_paths(session)

    def failed_runtime(self, directory):
        runtime = Runtime.__new__(Runtime)
        runtime.namespace = Path(directory)
        (runtime.namespace / "home").mkdir()
        runtime.out = runtime.namespace / "evidence"
        runtime.out.mkdir()
        runtime.env = {"PATH": "/usr/bin:/bin"}
        runtime.receipt = {}
        runtime.secrets = ["synthetic-secret"]
        return runtime

    def test_failed_operation_retains_scrubbed_output_without_arguments(self):
        with tempfile.TemporaryDirectory() as directory:
            runtime = self.failed_runtime(directory)
            with self.assertRaisesRegex(RuntimeError, "operation-failure-1.log"):
                runtime.run([sys.executable, "-c",
                    "import sys; print('synthetic-secret failure'); sys.exit(3)"])
            self.assertEqual((runtime.out / "operation-failure-1.log").read_text(),
                             "[redacted] failure\n")
            self.assertNotIn("synthetic-secret", json.dumps(runtime.receipt))
            self.assertEqual(runtime.receipt["operation_failures"][0]["outcome"], 3)

    def test_timed_out_operation_retains_scrubbed_partial_output(self):
        with tempfile.TemporaryDirectory() as directory:
            runtime = self.failed_runtime(directory)
            with self.assertRaises(subprocess.TimeoutExpired):
                runtime.run([sys.executable, "-c",
                    "import time; print('synthetic-secret partial', flush=True); time.sleep(10)"], timeout=0.5)
            self.assertEqual((runtime.out / "operation-failure-1.log").read_text(),
                             "[redacted] partial\n")
            self.assertEqual(runtime.receipt["operation_failures"][0]["outcome"], "timeout")

    def test_snapshot_rejects_external_symlink(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "outside").write_text("fixture")
            source = root / "source"
            source.mkdir()
            (source / "escape").symlink_to(root / "outside")
            with self.assertRaises(ValueError):
                linux_dev.identity(source, allow_links=True)

    def valid_run(self):
        return {"root": "root", "spawn_exit": 0, "root_status": "done: fixture complete",
                "component_count": 1, "retained_integrity_matches": True, "source_findings_present": True,
                "input_status": "", "input_commit_unchanged": True, "worktree_status": {"root": "", "child": ""},
                "request": {"state": "complete", "gathered": True, "child": "child", "gathered_parent_gen": "new"},
                "metadata": {"root": {"spawn_gen": "new"}},
                "read_order": {"same_child_replay": True, "read_both_before_first_gather": True,
                               "read_both_before_owner_acknowledgement": True},
                "replacement": {"exit": 0, "child": "child", "before_generation": "old"},
                "watcher_ended_while_pending": True}

    def test_restart_does_not_hide_child_or_generation_mismatch(self):
        run = self.valid_run()
        self.assertTrue(assess(run, restart=True, minimum_waiting_span=0)["passed"])
        run["replacement"]["child"] = "another-child"
        self.assertFalse(assess(run, restart=True, minimum_waiting_span=0)["passed"])
        run["replacement"]["child"] = "child"
        run["request"]["gathered_parent_gen"] = "old"
        self.assertFalse(assess(run, restart=True, minimum_waiting_span=0)["passed"])

    def test_ordinary_watcher_attention_remains_failure(self):
        run = self.valid_run()
        self.assertFalse(assess(run, restart=False, minimum_waiting_span=0)["passed"])
        run["watcher_ended_while_pending"] = False
        self.assertFalse(assess(run, restart=False, minimum_waiting_span=240)["passed"])

    def test_waiting_uses_actual_owner_format_and_positive_child_activity(self):
        run = self.valid_run()
        run["watcher_ended_while_pending"] = False
        sample = {"root_current": "state: waiting · source: task-group · waiting for active component child",
                  "child_current": "state: working · source: pane · harness busy (claude-hook)",
                  "root_current_exit": 0, "child_current_exit": 0, "arm_exit": None,
                  "beacon_age_seconds": 2, "watcher_lock": "123"}
        run["watch_samples"] = [dict(sample, at=100), dict(sample, at=400)]
        proof = assess(run, restart=False, minimum_waiting_span=240)
        self.assertTrue(proof["passed"])
        self.assertEqual(proof["waiting_samples"], 2)
        self.assertEqual(proof["waiting_span_seconds"], 300)
        run["watch_samples"][1]["child_current"] = "state: unknown · source: none · no live activity"
        self.assertFalse(assess(run, restart=False, minimum_waiting_span=240)["passed"])

    def test_full_reads_across_replacement_sessions_before_gather(self):
        with tempfile.TemporaryDirectory() as directory:
            namespace = Path(directory)
            home = namespace / "claude-fm"
            retained = home / "data/root/task-group/results/child"
            retained.mkdir(parents=True)
            (retained / "report.md").write_text("Expected report\nsecond line\n")
            (retained / "result.json").write_text('{"child": "child"}\n')
            transcripts = namespace / "claude/projects/fixture"
            transcripts.mkdir(parents=True)
            cwd = str(namespace / "worktree")
            now = time.time()
            def record(when, blocks):
                return {"cwd": cwd, "timestamp": datetime.fromtimestamp(now + when, timezone.utc).isoformat(),
                        "message": {"content": blocks}}
            read_records = []
            for number, name in enumerate(("report.md", "result.json")):
                read_records.extend([
                    record(number * 2, [{"type": "tool_use", "id": name, "name": "Read",
                                         "input": {"file_path": str(retained / name)}}]),
                    record(number * 2 + 1, [{"type": "tool_result", "tool_use_id": name,
                                             "content": (retained / name).read_text()}])])
            for number in range(2):
                tool_id = "submit-" + str(number)
                read_records.extend([
                    record(-5 + number * 2, [{"type": "tool_use", "id": tool_id, "name": "Bash",
                        "input": {"command": "python3 -B /retained/scripts/firstmate.py --root root submit --request /tmp/request.json"}}]),
                    record(-4 + number * 2, [{"type": "tool_result", "tool_use_id": tool_id,
                        "content": json.dumps({"request": {"child": "child", "body": {"request_id": "inspect"}}})}])])
            gather = record(5, [{"type": "tool_use", "id": "gather", "name": "Bash",
                                "input": {"command": "python3 -B /retained/scripts/firstmate.py --root root gather"}}])
            (transcripts / "old.jsonl").write_text("\n".join(json.dumps(item) for item in read_records))
            (transcripts / "new.jsonl").write_text(json.dumps(gather))
            run = {"root": "root", "request": {"child": "child", "body": {"request_id": "inspect"}, "gathered_at": now + 6},
                   "metadata": {"root": {"worktree": cwd}}}
            proof = read_order(namespace, home, run)
            self.assertTrue(proof["same_child_replay"])
            self.assertTrue(proof["read_both_before_first_gather"])
            self.assertTrue(proof["read_both_before_owner_acknowledgement"])
            self.assertNotIn("Expected report", json.dumps(proof))
            # An earlier variable-based gather is outside the literal-command
            # recognizer. The owner's immutable first timestamp must still fail
            # read-before-acknowledgement after a later visible gather.
            early = record(-2, [{"type": "tool_use", "id": "hidden-gather", "name": "Bash",
                                "input": {"command": 'CLIENT=/retained/scripts/firstmate.py; python3 "$CLIENT" --root root gather'}}])
            (transcripts / "early.jsonl").write_text(json.dumps(early))
            run["request"]["gathered_at"] = now - 1
            early_proof = read_order(namespace, home, run)
            self.assertTrue(early_proof["read_both_before_first_gather"])
            self.assertFalse(early_proof["read_both_before_owner_acknowledgement"])
            run["request"]["gathered_at"] = now + 6
            gather["timestamp"] = datetime.fromtimestamp(now - 1, timezone.utc).isoformat()
            (transcripts / "new.jsonl").write_text(json.dumps(gather))
            self.assertFalse(read_order(namespace, home, run)["read_both_before_first_gather"])


if __name__ == "__main__":
    unittest.main()
