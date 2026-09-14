"""Authoring evidence must prove actual declared reads and the exact trialed tree."""
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from .authoring import AuthoringTrial, full_reads, shell_read_target
from .authoring_fixture import INPUT, EXPECTED, LIBRARY, REQUIRED, TESTS


class AuthoringEvidenceTests(unittest.TestCase):
    def test_full_read_refuses_partial_failed_other_worker_and_late_reads(self):
        with tempfile.TemporaryDirectory(dir="/tmp") as name:
            base = Path(name)
            transcript = base / "claude/projects/trial.jsonl"
            transcript.parent.mkdir(parents=True)
            target = base / "leaf.md"
            target.write_text("complete first line\ncomplete last line\n")
            cwd = base / "worker"
            def records(*, payload, failed=False, limit=None, worker=None, at="2026-09-14T20:00:00Z"):
                return [
                    {"cwd": str(worker or cwd), "timestamp": at, "message": {"content": [
                        {"type": "tool_use", "id": "read", "name": "Read",
                         "input": {"file_path": str(target), "limit": limit}}]}},
                    {"cwd": str(worker or cwd), "timestamp": "2026-09-14T20:00:01Z", "message": {"content": [
                        {"type": "tool_result", "tool_use_id": "read", "is_error": failed, "content": payload}]}}]
            for kwargs in ({"payload": "complete first line"}, {"payload": target.read_text(), "failed": True},
                           {"payload": target.read_text(), "limit": 1},
                           {"payload": target.read_text(), "worker": base / "other"}):
                transcript.write_text("\n".join(json.dumps(v) for v in records(**kwargs)))
                self.assertFalse(full_reads(base, cwd, [target])["passed"], kwargs)
            transcript.write_text("\n".join(json.dumps(v) for v in records(payload=target.read_text())))
            self.assertTrue(full_reads(base, cwd, [target])["passed"])
            target.unlink()
            expected = {str(target): "complete first line\ncomplete last line\n"}
            self.assertTrue(full_reads(base, cwd, [target], expected_contents=expected)["passed"])
            self.assertFalse(full_reads(base, cwd, [target], expected_contents={str(target): "wrong"})["passed"])
            target.write_text("changed after Review")
            self.assertTrue(full_reads(base, cwd, [target], expected_contents=expected)["passed"])
            self.assertFalse(full_reads(base, cwd, [target])["passed"])
            self.assertFalse(full_reads(base, cwd, [target], after=1789416002)["passed"])
            self.assertFalse(full_reads(base, cwd, [target], before=1789416000)["passed"])

    @contextmanager
    def candidate(self):
        with tempfile.TemporaryDirectory(dir="/tmp") as name:
            base = Path(name)
            trial = AuthoringTrial.__new__(AuthoringTrial)
            trial.namespace, trial.out, trial.secrets = base, base / "evidence", []
            trial.out.mkdir()
            (base / "home").mkdir()
            worktree = base / "project"
            worktree.mkdir()
            trial.env = {"PATH": "/usr/bin:/bin", "HOME": str(base / "home"),
                         "PYTHONDONTWRITEBYTECODE": "1", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null"}
            def git(*args):
                return trial.run(["git", "-C", worktree, *args]).stdout.strip()
            git("init", "-b", "main")
            git("config", "user.name", "Fixture")
            git("config", "user.email", "fixture@example.invalid")
            (worktree / "release-input.json").write_text(json.dumps(INPUT))
            (worktree / "test_delivery.py").write_text(TESTS)
            git("add", ".")
            git("commit", "-qm", "input")
            trial.receipt = {"input_commit": git("rev-parse", "HEAD")}
            library = worktree / LIBRARY
            for relative in REQUIRED:
                file = library / relative
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_text("declared content\n")
                if relative.endswith("plugin.json"):
                    file.write_text(json.dumps({"name": "release-triage", "version": "0.1.0"}))
            (library / "skills/triage-release/SKILL.md").write_text("---\nname: triage-release\n---\nApply guidance.\n")
            git("add", ".")
            git("commit", "-qm", "authored")
            authored = git("rev-parse", "HEAD")
            (worktree / "trial-output.json").write_text(json.dumps(EXPECTED))
            retained = {"author-maker-v1": {"output_commit": authored},
                        "leaf-trial-v1": {"input_commit": authored, "child": "trial-child",
                            "report_digest": hashlib.sha256((worktree / "trial-output.json").read_bytes()).hexdigest()}}
            trial.owner_home, trial.root = base / "owner", "root"
            evidence = trial.owner_home / "data/root/task-group/results/trial-child"
            evidence.mkdir(parents=True)
            retained_result = retained["leaf-trial-v1"]
            (evidence / "report.md").write_bytes((worktree / "trial-output.json").read_bytes())
            (evidence / "result.json").write_text(json.dumps(retained_result))
            (worktree / "trial-result.json").write_bytes((evidence / "result.json").read_bytes())
            record = {key: "evidence" for key in ("findings", "preparation", "intervention")}
            record.update(author_output_commit=authored, trial_input_commit=authored, trial_child="trial-child",
                request_id="leaf-trial-v1", limits="same-project",
                result_digest=hashlib.sha256(json.dumps(retained_result, sort_keys=True,
                    separators=(",", ":"), ensure_ascii=False).encode()).hexdigest(),
                report_digest=retained_result["report_digest"])
            (worktree / "trial-record.json").write_text(json.dumps(record))
            git("add", ".")
            git("commit", "-qm", "trial evidence")
            yield trial, worktree, git, retained

    def test_review_must_contain_trialed_library_and_real_trial_output(self):
        with self.candidate() as (trial, worktree, git, retained):
            result = trial.check_reviewed_candidate(worktree, git("rev-parse", "HEAD"), retained)
            self.assertTrue(result["passed"], result)
            (worktree / LIBRARY / "guidance/release.md").write_text("untested replacement\n")
            git("add", ".")
            git("commit", "-qm", "changed after trial")
            result = trial.check_reviewed_candidate(worktree, git("rev-parse", "HEAD"), retained)
            self.assertFalse(result["checks"]["same_authored_trialed_reviewed_library"])

    def test_report_digest_cannot_replace_canonical_result_digest(self):
        with self.candidate() as (trial, worktree, git, retained):
            path = worktree / "trial-record.json"
            record = json.loads(path.read_text())
            record["result_digest"] = record["report_digest"]
            path.write_text(json.dumps(record))
            git("add", ".")
            git("commit", "-qm", "conflated digests")
            result = trial.check_reviewed_candidate(worktree, git("rev-parse", "HEAD"), retained)
            self.assertFalse(result["checks"]["reviewed_tests"])
            self.assertFalse(result["passed"])

    def test_fabricated_output_and_replaced_validation_cannot_pass(self):
        with self.candidate() as (trial, worktree, git, retained):
            (worktree / "trial-output.json").write_text("{}")
            # A replacement test that always passes is not behavioral evidence.
            (worktree / "test_delivery.py").write_text(
                "import unittest\nclass Fake(unittest.TestCase):\n def test_fake(self): pass\n")
            git("add", ".")
            git("commit", "-qm", "forged validation")
            result = trial.check_reviewed_candidate(worktree, git("rev-parse", "HEAD"), retained)
            self.assertFalse(result["checks"]["reviewed_behavior"])
            self.assertFalse(result["passed"])


    def test_reviewed_fabrication_cannot_be_hidden_by_final_provenance_repair(self):
        with self.candidate() as (trial, worktree, git, retained):
            path = worktree / "trial-record.json"
            original = path.read_bytes()
            record = json.loads(original)
            record.update(author_output_commit="evidence", trial_input_commit="evidence")
            path.write_text(json.dumps(record))
            git("add", ".")
            git("commit", "-qm", "misattributed evidence sent to Review")
            reviewed = git("rev-parse", "HEAD")
            path.write_bytes(original)
            git("add", ".")
            git("commit", "-qm", "repair only after Review")
            self.assertTrue(all(trial.check_trial_provenance(worktree, retained).values()))
            checked = trial.check_reviewed_candidate(worktree, reviewed, retained)
            self.assertFalse(checked["checks"]["reviewed_committed_trial_identities"])
            self.assertFalse(checked["passed"])

    def test_reviewed_bytes_must_match_owner_not_only_self_consistent_digests(self):
        with self.candidate() as (trial, worktree, git, retained):
            (worktree / "trial-output.json").write_text(json.dumps(EXPECTED, indent=2))
            result = dict(retained["leaf-trial-v1"], fabricated=True,
                report_digest=hashlib.sha256((worktree / "trial-output.json").read_bytes()).hexdigest())
            (worktree / "trial-result.json").write_text(json.dumps(result))
            path = worktree / "trial-record.json"
            record = json.loads(path.read_text())
            record["result_digest"] = hashlib.sha256(json.dumps(result, sort_keys=True,
                separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
            record["report_digest"] = result["report_digest"]
            path.write_text(json.dumps(record))
            git("add", ".")
            git("commit", "-qm", "self-consistent substituted report and result")
            checked = trial.check_reviewed_candidate(worktree, git("rev-parse", "HEAD"), retained)
            self.assertTrue(checked["checks"]["reviewed_tests"])
            self.assertFalse(checked["checks"]["reviewed_exact_trial_output_committed"])
            self.assertFalse(checked["checks"]["reviewed_exact_retained_trial_result_committed"])
            self.assertFalse(checked["passed"])

    def test_retained_core_shell_read_requires_exact_path_and_full_success(self):
        with tempfile.TemporaryDirectory(dir="/tmp") as name:
            base = Path(name)
            core = base / "owner/task-group/package/guidance/writing.md"
            core.parent.mkdir(parents=True)
            core.write_text("First complete line.\nLast complete line.\n")
            staging = base / "package-source/guidance/writing.md"
            staging.parent.mkdir(parents=True)
            staging.write_bytes(core.read_bytes())
            cwd = base / "worker"
            transcript = base / "claude/projects/trial.jsonl"
            transcript.parent.mkdir(parents=True)
            def check(target=core, output=None, failed=False, interrupted=False, suffix=""):
                output = core.read_text() if output is None else output
                command = 'ls -la ' + str(target.parent) + '\necho "---"\ncat ' + str(target) + suffix
                records = [
                    {"cwd": str(cwd), "timestamp": "2026-09-14T20:00:00Z", "message": {"content": [
                        {"type": "tool_use", "id": "read-core", "name": "Bash", "input": {"command": command}}]}},
                    {"cwd": str(cwd), "timestamp": "2026-09-14T20:00:01Z",
                     "toolUseResult": {"stdout": output, "interrupted": interrupted},
                     "message": {"content": [{"type": "tool_result", "tool_use_id": "read-core",
                         "is_error": failed, "content": output}]}}]
                transcript.write_text("\n".join(json.dumps(v) for v in records))
                return full_reads(base, cwd, [core], shell_targets={str(core)})
            self.assertTrue(check(suffix=" 2>/dev/null")["passed"])
            for kwargs in ({"target": staging}, {"output": "First complete line."}, {"failed": True},
                           {"interrupted": True}, {"suffix": " | head -1"}, {"suffix": " > hidden.txt"}):
                self.assertFalse(check(**kwargs)["passed"], kwargs)
            self.assertIsNone(shell_read_target("python3 replace.py\ncat " + str(core)))
            self.assertIsNone(shell_read_target("cat " + str(core) + "; true"))
