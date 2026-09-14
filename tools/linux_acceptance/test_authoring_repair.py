"""Repair delivery must retain actual evidence for the changed library."""
from contextlib import contextmanager
import hashlib
import json
import unittest
from unittest.mock import patch

from .authoring import AuthoringTrial
from .authoring_repair import AuthoringRepairTrial, REPAIR_FILES, ORIGINAL_FILES
from .authoring_fixture import EXPECTED, LIBRARY
from . import test_authoring as authoring_tests


class RepairEvidenceTests(unittest.TestCase):
    @contextmanager
    def candidate(self):
        with authoring_tests.AuthoringEvidenceTests().candidate() as (trial, worktree, git, retained):
            trial.__class__ = AuthoringRepairTrial
            reviewed = git("rev-parse", "HEAD")
            (worktree / LIBRARY / "guidance/release.md").write_text("Clarified stable ordering.\n")
            git("add", ".")
            git("commit", "-qm", "post-Review clarification")
            repaired = git("rev-parse", "HEAD")
            requests = []
            for key, primitive, writable, phase in (
                ("author-maker-v1", "Work", True, "work"),
                ("leaf-trial-v1", "Work", False, "work"),
                ("final-review-v1", "Review", False, "review"),
                ("repair-trial-v1", "Work", False, "repair")):
                value = retained.setdefault(key, {})
                value.update(primitive=primitive, writable=writable,
                             child=value.get("child", key + "-child"))
                requests.append({"body": {"request_id": key}, "primitive": primitive,
                    "writable": writable, "phase": phase, "child": value["child"], "gathered": True,
                    "accepted_at": len(requests) * 10 + 1, "gathered_at": len(requests) * 10 + 5})
            retained["final-review-v1"]["input_commit"] = reviewed
            repair = retained["repair-trial-v1"]
            repair["input_commit"] = repaired
            repair["report_digest"] = hashlib.sha256(json.dumps(EXPECTED, indent=2).encode()).hexdigest()
            group = trial.owner_home / "data" / trial.root / "task-group/results"
            for key, prefix, payload in (
                ("final-review-v1", "final-review", "No blocking findings.\n"),
                ("repair-trial-v1", "repair-trial", json.dumps(EXPECTED, indent=2))):
                value = retained[key]
                directory = group / value["child"]
                directory.mkdir(parents=True)
                (directory / "report.md").write_text(payload)
                (directory / "result.json").write_text(json.dumps(value))
                target = prefix + ("-report.md" if key == "final-review-v1" else "-output.json")
                (worktree / target).write_bytes((directory / "report.md").read_bytes())
                (worktree / (prefix + "-result.json")).write_bytes((directory / "result.json").read_bytes())
            record = dict(preparation="bounded clarification", intervention="none", findings="correct output",
                limits="same-project", author_output_commit=retained["author-maker-v1"]["output_commit"],
                trial_input_commit=repaired, trial_child=repair["child"], request_id="repair-trial-v1",
                result_digest=hashlib.sha256(json.dumps(repair, sort_keys=True,
                    separators=(",", ":"), ensure_ascii=False).encode()).hexdigest(),
                report_digest=repair["report_digest"], reviewed_commit=reviewed,
                review_child=retained["final-review-v1"]["child"])
            (worktree / "repair-trial-record.json").write_text(json.dumps(record))
            git("add", ".")
            git("commit", "-qm", "retain repair and Review evidence")
            result = {"retained_results": retained, "requests": requests}
            yield trial, worktree, git, result

    def test_repair_candidate_passes_separate_contract_and_strict_tree_still_fails(self):
        with self.candidate() as (trial, tree, git, result):
            checks = trial.final_library_checks(tree, result)
            self.assertTrue(all(checks.values()), checks)
            self.assertFalse(result["unchanged_library_assessment"]["passed"])
            self.assertEqual(AuthoringTrial.expected_requests,
                             {"author-maker-v1", "leaf-trial-v1", "final-review-v1"})
            self.assertEqual(len(trial.evidence_hashes(tree)), len(REPAIR_FILES | set(ORIGINAL_FILES)))

    def test_tasktmp_only_and_self_consistent_forged_repair_result_fail(self):
        with self.candidate() as (trial, tree, git, result):
            output = tree / "repair-trial-output.json"
            original = output.read_bytes()
            output.unlink()
            checks = trial.check_repair_candidate(tree, result)
            self.assertFalse(checks["repair_exact_trial_output_committed"])
            output.write_bytes(original)
            path = tree / "repair-trial-result.json"
            fake = json.loads(path.read_text())
            fake["fabricated"] = True
            path.write_text(json.dumps(fake))
            record_path = tree / "repair-trial-record.json"
            record = json.loads(record_path.read_text())
            record["result_digest"] = hashlib.sha256(json.dumps(fake, sort_keys=True,
                separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
            record_path.write_text(json.dumps(record))
            checks = trial.check_repair_candidate(tree, result)
            self.assertFalse(checks["repair_exact_retained_trial_result_committed"])
            self.assertFalse(checks["repair_committed_trial_identities"])

    def test_changes_after_repair_trial_and_replaced_original_evidence_fail(self):
        with self.candidate() as (trial, tree, git, result):
            (tree / LIBRARY / "guidance/release.md").write_text("Untrialed change.\n")
            (tree / "trial-record.json").write_text("{}")
            git("add", ".")
            git("commit", "-qm", "late untrialed change and overwritten evidence")
            checks = trial.check_repair_candidate(tree, result)
            for key in ("changed_library_has_exact_repair_trial", "only_repair_evidence_added_after_trial",
                        "original_reviewed_trial_evidence_preserved"):
                self.assertFalse(checks[key], key)

    def test_pre_review_repair_second_review_extra_work_and_foreign_child_fail(self):
        with self.candidate() as (trial, tree, git, result):
            repair = result["requests"][-1]
            for field, value in (("phase", "work"), ("primitive", "Review"), ("writable", True),
                                 ("child", "foreign-child")):
                old = repair[field]
                repair[field] = value
                self.assertFalse(trial.check_repair_candidate(tree, result)["exact_author_review_repair_sequence"])
                repair[field] = old
            repair["accepted_at"] = 2
            self.assertFalse(trial.check_repair_candidate(tree, result)["repair_trial_after_review_gather"])
            result["requests"].append(dict(repair, body={"request_id": "extra-work"}))
            self.assertFalse(trial.check_repair_candidate(tree, result)["exact_author_review_repair_sequence"])

    def test_substituted_review_evidence_and_wrong_review_binding_fail(self):
        with self.candidate() as (trial, tree, git, result):
            (tree / "final-review-report.md").write_text("Manufactured findings")
            path = tree / "repair-trial-record.json"
            record = json.loads(path.read_text())
            record["reviewed_commit"] = result["retained_results"]["repair-trial-v1"]["input_commit"]
            path.write_text(json.dumps(record))
            checks = trial.check_repair_candidate(tree, result)
            self.assertFalse(checks["exact_review_evidence_committed"])
            self.assertFalse(checks["repair_committed_trial_identities"])


    def test_final_check_must_follow_repair_gather_and_succeed(self):
        with self.candidate() as (trial, tree, git, result):
            result.update(metadata={trial.root: {"worktree": str(tree)}},
                          client_path=str(tree / "core/scripts/firstmate.py"))
            for at, success, expected in ((30, True, False), (36, False, False), (36, True, True)):
                result["acceptance"] = {"checks": {}, "passed": True}
                result["final_check_order"] = {"events": [
                    {"invoked_at": at, "completed_at": at + 1, "success": success}]}
                with patch.object(AuthoringTrial, "collect_dynamic"):
                    trial.collect_dynamic(result, tree)
                self.assertIs(result["acceptance"]["checks"]["root_final_check_after_repair_gather"], expected)


    def test_external_symlinks_cannot_substitute_for_committed_evidence(self):
        with self.candidate() as (trial, tree, git, result):
            for name in sorted(REPAIR_FILES | set(ORIGINAL_FILES)):
                path = tree / name
                original = path.read_bytes()
                target = trial.namespace / ("external-" + name)
                target.write_bytes(original)
                path.unlink()
                path.symlink_to(target)
                git("add", name)
                git("commit", "-qm", "linked " + name)
                self.assertFalse(trial.committed_evidence_files(tree, {name}), name)
                self.assertFalse(trial.check_repair_candidate(tree, result)[
                    "all_trial_evidence_regular_committed_blobs"], name)
                self.assertNotIn(name, trial.evidence_hashes(tree))
                path.unlink()
                path.write_bytes(original)
                git("add", name)
                git("commit", "-qm", "restore " + name)
            self.assertTrue(all(trial.check_repair_candidate(tree, result).values()))

    def test_uncommitted_evidence_bytes_and_reviewed_symlink_are_rejected(self):
        with self.candidate() as (trial, tree, git, result):
            name = "repair-trial-record.json"
            (tree / name).write_text((tree / name).read_text() + "\n")
            self.assertFalse(trial.committed_evidence_files(tree, {name}))
            name = "trial-output.json"
            path = tree / name
            target = trial.namespace / "outside-original-output"
            target.write_bytes(path.read_bytes())
            path.unlink()
            path.symlink_to(target)
            git("add", name)
            git("commit", "-qm", "linked original output")
            checked = trial.check_reviewed_candidate(tree, git("rev-parse", "HEAD"), result["retained_results"])
            self.assertFalse(checked["checks"]["reviewed_trial_evidence_regular_blobs"])


    def test_same_cwd_prefix_requires_explicit_separate_reassessment(self):
        from datetime import datetime, timezone
        from .evidence import final_check_order
        with self.candidate() as (trial, tree, git, result):
            traces = trial.namespace / "claude/projects"
            traces.mkdir(parents=True)
            receipt = trial.namespace / "final-check.txt"
            run = {"root": trial.root, "metadata": {trial.root: {"worktree": str(tree)}},
                   "requests": [{"primitive": "Review", "gathered_at": 10}]}
            final = "python3 -B -m unittest discover -v > " + str(receipt) + " 2>&1"
            def observe(command, at=20, error=False):
                records = [
                    {"cwd": str(tree), "timestamp": datetime.fromtimestamp(at, timezone.utc).isoformat(),
                     "message": {"content": [{"type": "tool_use", "name": "Bash", "id": "test",
                                              "input": {"command": command}}]}},
                    {"cwd": str(tree), "timestamp": datetime.fromtimestamp(at + 1, timezone.utc).isoformat(),
                     "message": {"content": [{"type": "tool_result", "tool_use_id": "test", "is_error": error}]}}]
                (traces / "session.jsonl").write_text("\n".join(json.dumps(v) for v in records))
                return final_check_order(trial.namespace, trial.owner_home, run, receipt,
                                         allow_same_cwd_prefix=True)
            command = "cd " + str(tree) + "\n" + final
            self.assertTrue(observe(command)["passed"])
            self.assertFalse(final_check_order(trial.namespace, trial.owner_home, run, receipt)["passed"])
            for wrong in ("cd /wrong\n" + final, "cd $PWD\n" + final,
                          command + "; true", command + "\necho done"):
                self.assertFalse(observe(wrong)["passed"], wrong)
            self.assertFalse(observe(command, at=5)["passed"])
            self.assertFalse(observe(command, error=True)["passed"])
