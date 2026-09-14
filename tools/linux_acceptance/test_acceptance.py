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

    def test_enabled_trial_requires_context_and_retained_custom_read(self):
        run = self.valid_run()
        run.update(enabled_project=True, custom_marker_present=True)
        self.assertFalse(assess(run, restart=True, minimum_waiting_span=0)["passed"])
        run["read_order"]["context_only_calls"] = True
        self.assertFalse(assess(run, restart=True, minimum_waiting_span=0)["passed"])
        run["read_order"]["custom_skill_read_before_submit"] = True
        self.assertTrue(assess(run, restart=True, minimum_waiting_span=0)["passed"])
        run["custom_marker_present"] = False
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
            # Short commands must match this task's exact retained client.
            run["client_path"] = "/retained/scripts/firstmate.py"
            for record_value in [*read_records, gather]:
                for block in record_value["message"]["content"]:
                    if block.get("name") == "Bash":
                        block["input"]["command"] = block["input"]["command"].replace("--root root ", "")
            custom = namespace / "custom-SKILL.md"
            custom.write_text("Use the admitted primitive and include a retained marker.\n")
            run["custom_skill_path"] = str(custom)
            read_records.extend([
                record(-10, [{"type": "tool_use", "id": "custom", "name": "Read",
                              "input": {"file_path": str(custom)}}]),
                record(-9, [{"type": "tool_result", "tool_use_id": "custom", "content": custom.read_text()}])])
            (transcripts / "old.jsonl").write_text("\n".join(json.dumps(item) for item in read_records))
            (transcripts / "new.jsonl").write_text(json.dumps(gather))
            proof = read_order(namespace, home, run)
            self.assertTrue(proof["context_only_calls"])
            self.assertTrue(proof["custom_skill_read_before_submit"])
            self.assertTrue(proof["same_child_replay"])
            run["client_path"] = "/wrong/scripts/firstmate.py"
            self.assertFalse(read_order(namespace, home, run)["context_only_calls"])
            run["client_path"] = "/retained/scripts/firstmate.py"
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


class DynamicReadChecks(unittest.TestCase):
    def test_other_component_gathers_do_not_acknowledge_this_result(self):
        with tempfile.TemporaryDirectory() as directory:
            namespace = Path(directory)
            home = namespace / "fm"
            retained = home / "data/root/task-group/results/child"
            retained.mkdir(parents=True)
            for name in ("report.md", "result.json"):
                (retained / name).write_text("complete retained " + name)
            traces = namespace / "claude/projects/example"
            traces.mkdir(parents=True)
            cwd = str(namespace / "wt")
            now = time.time()
            events = []
            def event(at, block):
                events.append({"cwd": cwd, "timestamp": datetime.fromtimestamp(now + at, timezone.utc).isoformat(),
                               "message": {"content": [block]}})
            def bash(at, ident, command, response=None):
                event(at, {"type": "tool_use", "id": ident, "name": "Bash", "input": {"command": command}})
                if response:
                    event(at + .1, {"type": "tool_result", "tool_use_id": ident, "content": json.dumps(response)})
            client = "python3 -B /retained/scripts/firstmate.py "
            bash(-4, "other-gather", client + "gather --request-id other")
            for index, request_id in enumerate(("other", "inspect", "inspect")):
                bash(-3 + index, "submit" + str(index), client + "submit --request /tmp/request.json",
                     {"request": {"child": "child" if request_id == "inspect" else "other-child",
                                  "body": {"request_id": request_id}}})
            for index, name in enumerate(("report.md", "result.json")):
                event(index * 2, {"type": "tool_use", "id": name, "name": "Read", "input": {"file_path": str(retained / name)}})
                event(index * 2 + 1, {"type": "tool_result", "tool_use_id": name, "content": (retained / name).read_text()})
            bash(5, "our-gather", client + "gather --request-id inspect")
            trace = traces / "session.jsonl"
            trace.write_text("\n".join(json.dumps(item) for item in events))
            run = {"root": "root", "workflow": "dynamic", "client_path": "/retained/scripts/firstmate.py",
                   "metadata": {"root": {"worktree": cwd}},
                   "request": {"child": "child", "body": {"request_id": "inspect"}, "gathered_at": now + 6}}
            proof = read_order(namespace, home, run)
            self.assertEqual(proof["recognized_gather_count"], 1)
            self.assertTrue(proof["same_child_replay"])
            self.assertTrue(proof["read_both_before_first_gather"])
            # An output-only formatter still executes the same literal client.
            for event_value in events:
                for block in event_value["message"]["content"]:
                    if block.get("id") == "our-gather":
                        block["input"]["command"] += " | python3 -c \"import json,sys; print(json.load(sys.stdin)['request']['gathered'])\""
            trace.write_text("\n".join(json.dumps(item) for item in events))
            piped = read_order(namespace, home, run)
            self.assertEqual(piped["recognized_gather_count"], 1)
            self.assertTrue(piped["read_both_before_first_gather"])
            self.assertTrue(piped["context_only_calls"])
            self.assertTrue(any(e.get("output_pipeline") for e in piped["events"]))
            run["request"]["gathered_at"] = now - 2
            self.assertFalse(read_order(namespace, home, run)["read_both_before_owner_acknowledgement"])


class DynamicCandidateChecks(unittest.TestCase):
    def test_reviewed_snapshot_must_contain_both_retained_maker_implementations(self):
        from .dynamic import DynamicTrial
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            project = base / "project"
            project.mkdir()
            (base / "home").mkdir()
            trial = DynamicTrial.__new__(DynamicTrial)
            trial.namespace, trial.out = base, base / "evidence"
            trial.out.mkdir()
            trial.env = {"PATH": "/usr/bin:/bin", "HOME": str(base), "GIT_CONFIG_NOSYSTEM": "1",
                         "GIT_CONFIG_GLOBAL": "/dev/null", "PYTHONDONTWRITEBYTECODE": "1"}
            trial.secrets, trial.receipt = [], {}
            def git(*args):
                return subprocess.run(["git", "-C", str(project), *args], check=True, env=trial.env,
                                      capture_output=True, text=True).stdout.strip()
            def commit(message):
                git("add", ".")
                git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", message)
                return git("rev-parse", "HEAD")
            git("init", "-b", "main")
            (project / "stock.py").write_text("def total_units(counts): return sum(counts)\n")
            (project / "labels.py").write_text("def normalize_code(value): return value.strip().upper()\n")
            trial.receipt["input_commit"] = commit("input")
            for name in ("test_stock.py", "test_labels.py"):
                (project / name).write_text("# placeholder only\n")
            wrong_review = commit("test names but no joined implementation")
            (project / "stock.py").write_text("def total_units(counts): return sum(counts)\ndef has_stock(counts): return total_units(counts)>0\n")
            (project / "test_stock.py").write_text("import unittest\nfrom stock import has_stock\nclass Stock(unittest.TestCase):\n def test_positive(self): self.assertTrue(has_stock([1]))\n")
            stock_output = commit("stock maker")
            (project / "labels.py").write_text("def normalize_code(value): return value.strip().upper()\ndef label_key(value): return normalize_code(value).replace('-', '_')\n")
            (project / "test_labels.py").write_text("import unittest\nfrom labels import label_key\nclass Labels(unittest.TestCase):\n def test_key(self): self.assertEqual(label_key(' ab-7 '),'AB_7')\n")
            joined = commit("label maker")
            retained = {"stock-maker-v1": {"output_commit": stock_output}, "label-maker-v1": {"output_commit": joined}}
            wrong = trial.check_reviewed_candidate(project, wrong_review, retained)
            self.assertFalse(wrong["passed"])
            self.assertFalse(wrong["checks"]["reviewed_behavior"])
            self.assertFalse(wrong["checks"]["stock.py_matches_maker"])
            right = trial.check_reviewed_candidate(project, joined, retained)
            self.assertTrue(right["passed"], right)
            self.assertEqual(len(right["files_sha256"]), 4)

    def test_final_test_execution_must_follow_review_acknowledgement(self):
        from .evidence import final_check_order
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            traces = base / "claude/projects/example"
            traces.mkdir(parents=True)
            now = time.time()
            cwd = str(base / "worktree")
            receipt = base / "dynamic-final-check.txt"
            receipt.write_text("Ran 2 tests in 0.001s\n\nOK\n")
            run = {"root": "root", "metadata": {"root": {"worktree": cwd}},
                   "requests": [{"primitive": "Review", "gathered_at": now}]}
            def write(at, error=False):
                records = []
                for offset, block in ((0, {"type": "tool_use", "id": "final", "name": "Bash",
                     "input": {"command": "python3 -B -m unittest discover -v > " + str(receipt) + " 2>&1"}}),
                     (1, {"type": "tool_result", "tool_use_id": "final", "is_error": error, "content": ""})):
                    records.append({"cwd": cwd, "timestamp": datetime.fromtimestamp(at + offset, timezone.utc).isoformat(),
                                    "message": {"content": [block]}})
                (traces / "session.jsonl").write_text("\n".join(json.dumps(r) for r in records))
            write(now - 10)
            self.assertFalse(final_check_order(base, base / "fm", run, receipt)["passed"])
            write(now + 2, error=True)
            self.assertFalse(final_check_order(base, base / "fm", run, receipt)["passed"])
            write(now + 2)
            self.assertTrue(final_check_order(base, base / "fm", run, receipt)["passed"])


class LiteralClientChecks(unittest.TestCase):
    def test_output_pipeline_does_not_allow_shell_lists_or_substitutions(self):
        from .evidence import literal_client_command
        invocation = "python3 -B /retained/scripts/firstmate.py gather --request-id inspect"
        self.assertEqual(literal_client_command(invocation), (invocation.split(), False))
        self.assertEqual(literal_client_command(invocation + " | python3 -c 'import json,sys; print(json.load(sys.stdin))'"),
                         (invocation.split(), True))
        for suffix in ("; echo done", " && echo done", " || echo done", " &", " |", " < /tmp/input", " | echo $(date)"):
            self.assertEqual(literal_client_command(invocation + suffix), ([], False))


class DynamicRelaunchChecks(unittest.TestCase):
    def test_later_review_cannot_stand_in_for_inflight_maker_recovery(self):
        from .dynamic import maker_relaunch_window
        stock = {"primitive": "Work", "state": "complete", "gathered": True}
        label = {"primitive": "Work", "state": "complete", "gathered": True}
        review = {"primitive": "Review", "state": "launched", "gathered": False}
        completed, pending = maker_relaunch_window([stock, label, review])
        self.assertTrue(completed)
        self.assertFalse(pending, "Review activity cannot certify in-flight maker recovery")
        label.update(state="launched", gathered=False)
        completed, pending = maker_relaunch_window([stock, label])
        self.assertEqual(completed, [stock])
        self.assertEqual(pending, [label])
