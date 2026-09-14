"""One explicit post-Review repair trial, using the original authoring owners."""
import hashlib
import json
from pathlib import Path

from .authoring import AuthoringTrial, TRIAL_FILES, full_reads
from .authoring_fixture import LIBRARY, SKILL, repair_spec
from .local_delivery import _extend


REPAIR_FILES = {"repair-trial-output.json", "repair-trial-result.json", "repair-trial-record.json",
                "final-review-report.md", "final-review-result.json"}
ORIGINAL_FILES = TRIAL_FILES


class AuthoringRepairTrial(AuthoringTrial):
    expected_requests = AuthoringTrial.expected_requests | {"repair-trial-v1"}
    request_count_check = "three_work_one_review"
    title = "Author, review, repair and retrial a leaf library with delivered evidence"

    def prepare_root(self, project, session):
        result = super().prepare_root(project, session)
        self.receipt.update(authoring="non-delegating-leaf-repair",
                            scope="private Linux Claude same-project leaf repair acceptance")
        return result

    def composition_spec(self):
        return repair_spec(self.args.component_delay, self.delivery_instructions())

    def final_library_checks(self, worktree, result):
        # Preserve the unchanged-library assertion as a separate observation.
        # Only this explicitly selected case accepts the required changed tree.
        strict = super().final_library_checks(worktree, result)
        result["unchanged_library_assessment"] = {"checks": strict, "passed": all(strict.values())}
        return self.check_repair_candidate(worktree, result)

    def check_repair_candidate(self, worktree, result):
        retained = result["retained_results"]
        review = retained.get("final-review-v1", {})
        repair = retained.get("repair-trial-v1", {})
        reviewed, repaired = review.get("input_commit"), repair.get("input_commit")
        final = self.git_text(worktree, "rev-parse", "HEAD")
        requests = {r.get("body", {}).get("request_id"): r for r in result.get("requests", [])}
        repair_request = requests.get("repair-trial-v1", {})
        review_request = requests.get("final-review-v1", {})
        checks = {"repair_" + name: value for name, value in self.check_trial_provenance(
            worktree, retained, request_id="repair-trial-v1", prefix="repair-trial",
            extra_identities={"reviewed_commit": reviewed, "review_child": review.get("child")}).items()}
        try:
            record = json.loads((worktree / "repair-trial-record.json").read_text())
            checks["repair_trial_limits_recorded"] = (
                all(record.get(key) for key in ("preparation", "intervention", "findings", "limits"))
                and "same-project" in record["limits"])
        except (OSError, ValueError, TypeError):
            checks["repair_trial_limits_recorded"] = False
        checks["all_trial_evidence_regular_committed_blobs"] = self.committed_evidence_files(
            worktree, REPAIR_FILES | set(ORIGINAL_FILES))
        roles = {"author-maker-v1": ("Work", True, "work"),
                 "leaf-trial-v1": ("Work", False, "work"),
                 "final-review-v1": ("Review", False, "review"),
                 "repair-trial-v1": ("Work", False, "repair")}
        checks["exact_author_review_repair_sequence"] = (
            len(result.get("requests", [])) == len(roles) and set(requests) == set(roles)
            and set(retained) == set(roles)
            and len({r.get("child") for r in requests.values()}) == len(roles)
            and all(r.get("child") for r in requests.values())
            and all(requests[key].get("primitive") == primitive
                    and requests[key].get("writable") is writable
                    and requests[key].get("phase") == phase
                    and retained[key].get("primitive") == primitive
                    and retained[key].get("writable") is writable
                    and retained[key].get("child") == requests[key].get("child")
                    and requests[key].get("gathered") is True
                    for key, (primitive, writable, phase) in roles.items()))
        times = [review_request.get("gathered_at"), repair_request.get("accepted_at"),
                 repair_request.get("gathered_at")]
        checks["repair_trial_after_review_gather"] = (
            all(isinstance(t, (int, float)) and not isinstance(t, bool) for t in times)
            and 0 < times[0] < times[1] < times[2])
        trees = {label: self.git_text(worktree, "rev-parse", commit + ":" + LIBRARY) if commit else None
                 for label, commit in (("reviewed", reviewed), ("repair_trial", repaired), ("final", final))}
        checks["changed_library_has_exact_repair_trial"] = (
            all(trees.values()) and trees["reviewed"] != trees["repair_trial"] == trees["final"])
        def ancestor(before, after):
            return bool(before and after) and self.run(
                ["git", "-C", worktree, "merge-base", "--is-ancestor", before, after],
                check=False).returncode == 0
        checks["review_repair_delivery_ancestry"] = (
            reviewed != repaired != final and ancestor(reviewed, repaired) and ancestor(repaired, final))
        delta = self.git_text(worktree, "diff", "--name-status", repaired, final) if repaired and final else None
        checks["only_repair_evidence_added_after_trial"] = (
            delta is not None and set(delta.splitlines()) == {"A\t" + name for name in REPAIR_FILES})
        before_trial = self.git_text(worktree, "diff", "--name-only", reviewed, repaired) if reviewed and repaired else None
        checks["repair_changes_only_library"] = (
            bool(before_trial) and all(name.startswith(LIBRARY + "/") for name in before_trial.splitlines()))
        checks["original_reviewed_trial_evidence_preserved"] = bool(reviewed) and all(
            self.git_text(worktree, "rev-parse", reviewed + ":" + name)
            == self.git_text(worktree, "rev-parse", "HEAD:" + name)
            and self.git_text(worktree, "rev-parse", "HEAD:" + name)
            for name in ORIGINAL_FILES)
        review_dir = (self.owner_home / "data" / self.root / "task-group/results"
                      / review.get("child", "missing"))
        try:
            checks["exact_review_evidence_committed"] = (
                (worktree / "final-review-report.md").read_bytes() == (review_dir / "report.md").read_bytes()
                and (worktree / "final-review-result.json").read_bytes() == (review_dir / "result.json").read_bytes()
                and json.loads((review_dir / "result.json").read_text()) == review)
        except (OSError, ValueError):
            checks["exact_review_evidence_committed"] = False
        result["repair_library_trees"] = trees
        return checks

    def collect_dynamic(self, result, project):
        super().collect_dynamic(result, project)
        repair = result["retained_results"].get("repair-trial-v1", {})
        request = next((r for r in result["requests"]
                        if r.get("body", {}).get("request_id") == "repair-trial-v1"), {})
        meta = result["metadata"].get(repair.get("child"), {})
        child_tree = Path(meta.get("worktree", "/nonexistent"))
        package = Path(result["client_path"]).parents[1]
        relative = (LIBRARY + "/" + SKILL, LIBRARY + "/references/library-context.md",
                    LIBRARY + "/guidance/release.md", "release-input.json")
        expected = {}
        for name in relative:
            reply = self.run(["git", "-C", project, "show", repair["input_commit"] + ":" + name],
                             check=False) if repair.get("input_commit") else None
            expected[str(child_tree / name)] = reply.stdout if reply and reply.returncode == 0 else ""
        writing = package / "guidance/writing.md"
        expected[str(writing)] = writing.read_text() if writing.is_file() else ""
        reads = full_reads(self.namespace, child_tree, list(expected),
                           after=request.get("accepted_at", 0), before=request.get("gathered_at", 0),
                           expected_contents=expected, shell_targets={str(writing)})
        result["repair_trial_native_reads"] = reads
        ack = request.get("gathered_at")
        events = result.get("final_check_order", {}).get("events", [])
        worktree = Path(result["metadata"].get(self.root, {}).get("worktree", "/nonexistent"))
        result["committed_authoring_evidence_sha256"] = self.evidence_hashes(worktree)
        _extend(result, {
            "fresh_repair_trial_read_declared_context": reads["passed"],
            "root_final_check_after_repair_gather": isinstance(ack, (int, float)) and any(
                e.get("success") and e.get("completed_at", 0) >= e.get("invoked_at", 0) > ack
                for e in events),
        })

    @staticmethod
    def evidence_hashes(worktree):
        return {name: hashlib.sha256((worktree / name).read_bytes()).hexdigest()
                for name in sorted(REPAIR_FILES | set(ORIGINAL_FILES)) if (worktree / name).is_file() and not (worktree / name).is_symlink()}

    def cleanup(self):
        super().cleanup()
        # Compare to pre-landing validated bytes; teardown may remove owner records.
        for result in self.receipt.get("runs", []):
            before = result.get("committed_authoring_evidence_sha256", {})
            after = self.evidence_hashes(self.namespace / "project")
            passed = (bool(before) and set(before) == REPAIR_FILES | set(ORIGINAL_FILES) and after == before
                      and self.committed_evidence_files(self.namespace / "project", set(before)))
            result["repair_evidence_after_cleanup"] = {"passed": passed, "files_sha256": after}
            self.receipt["cleanup_passed"] &= passed
