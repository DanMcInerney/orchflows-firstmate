"""Review admission through the public client with a disposable controller.

These are transport and identity checks. They launch no FirstMate or worker.
"""

import argparse
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import test_firstmate_client as legacy


class FirstMateReviewClientTests(unittest.TestCase):
    setUp = legacy.FirstMateClientTests.setUp
    calls = legacy.FirstMateClientTests.calls

    def review(self):
        self.settings["protocol"].update(primitives=["Work", "Review"],
                                         review_policies=["explicit-audit"])
        self.settings["view"]["scope"] = "local-readonly-review"
        self.settings["view"]["attachment"].update(primitive="Review",
                                                    review_policy="explicit-audit")

    def cli(self, operation="status", *, primitive="Review", timeout="3"):
        legacy.write_json(self.home / "fixture.json", self.settings)
        command = [sys.executable, "-B", str(self.script), "--firstmate-root", str(self.code),
                   "--home", str(self.home), "--root", "root-1", "--generation", "gen-1",
                   "--timeout", timeout]
        if primitive is not None:
            command += ["--primitive", primitive]
        command.append(operation)
        if operation == "submit":
            command += ["--request", str(self.request)]
        result = subprocess.run(command, env=self.environment, capture_output=True, text=True,
                                encoding="utf-8", timeout=15)
        self.assertEqual(result.stderr, "", result.stderr)
        return result.returncode, json.loads(result.stdout)

    def rejected_before_mutation(self, operation="submit"):
        before = len(self.calls())
        code, result = self.cli(operation)
        self.assertEqual(code, 2)
        self.assertEqual(result["status"], "rejected")
        self.assertFalse(result["retry_automatically"])
        self.assertFalse(any(call["operation"] in {"submit", "gather"}
                             for call in self.calls()[before:]))
        return result

    def test_review_status_confirms_explicit_audit_and_exact_snapshot(self):
        self.review()
        code, result = self.cli()
        self.assertEqual((code, result), (0, self.settings["view"]))
        self.assertEqual([call["operation"] for call in self.calls()], ["protocol", "status"])

    def test_review_submit_and_gather_keep_owner_protocol_and_request_unchanged(self):
        self.review()
        code, result = self.cli("submit")
        self.assertEqual(code, 0)
        self.assertEqual(result["request"]["body"],
                         json.loads(self.request.read_text(encoding="utf-8")))
        self.assertEqual(self.calls()[-1]["args"],
                         ["--home", str(self.home), "submit", "root-1",
                          "--generation", "gen-1", "--request", str(self.request)])
        self.settings["view"].update(request={"state": "complete", "gathered": True},
                                     result={"primitive": "Review", "review_policy": "explicit-audit"})
        self.assertEqual(self.cli("gather"), (0, self.settings["view"]))
        self.assertEqual(self.calls()[-1]["args"],
                         ["--home", str(self.home), "gather", "root-1", "--generation", "gen-1"])

    def test_old_work_protocol_and_namespace_callers_remain_supported(self):
        self.assertEqual(self.cli(primitive=None), (0, self.settings["view"]))
        self.assertEqual(self.cli(primitive="Work"), (0, self.settings["view"]))
        spec = importlib.util.spec_from_file_location("review_test_client", self.script)
        client = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(client)
        args = argparse.Namespace(firstmate_root=self.code, home=self.home, root="root-1",
                                  generation="gen-1", timeout=3, operation="status")
        with patch.object(client, "call_controller",
                          side_effect=[self.settings["protocol"], self.settings["view"]]):
            self.assertEqual(client.run(args), self.settings["view"])

    def test_review_requires_explicit_capabilities_before_any_status(self):
        self.review()
        valid = copy.deepcopy(self.settings["protocol"])
        cases = [dict(legacy.PROTOCOL)]
        for key in ("primitives", "review_policies"):
            for value in (None, "Review explicit-audit", {}, [True], [["Review"]],
                          ["Work"], ["Review", "Review"]):
                cases.append({**valid, key: value})
        for protocol in cases:
            with self.subTest(protocol=protocol):
                self.settings["protocol"] = protocol
                before = len(self.calls())
                self.rejected_before_mutation()
                self.assertEqual([call["operation"] for call in self.calls()[before:]], ["protocol"])

    def test_review_handshake_retains_global_work_scope_and_strict_types(self):
        self.review()
        valid = copy.deepcopy(self.settings["protocol"])
        for key, value in (("scope", "local-readonly-review"), ("version", True),
                           ("version", 2), ("experimental", 1), ("protocol", "other")):
            with self.subTest(key=key, value=value):
                self.settings["protocol"] = {**valid, key: value}
                self.rejected_before_mutation()

    def test_review_rejects_missing_or_forged_audit_authorization(self):
        self.review()
        original = copy.deepcopy(self.settings["view"]["attachment"])
        candidates = [{key: value for key, value in original.items() if key != "review_policy"}]
        for key, value in (("review_policy", None), ("review_policy", "none"),
                           ("review_policy", True), ("review_policy", "dynamic"),
                           ("primitive", "Work"), ("readonly", False), ("readonly", 1),
                           ("max_components", 2), ("max_components", True), ("schema", True)):
            candidates.append({**original, key: value})
        for attachment in candidates:
            with self.subTest(attachment=attachment):
                self.settings["view"]["attachment"] = attachment
                self.rejected_before_mutation()
                self.rejected_before_mutation("gather")

    def test_work_cannot_consume_a_review_attachment_or_audit_policy(self):
        self.review()
        code, result = self.cli("submit", primitive="Work")
        self.assertEqual((code, result["status"]), (2, "rejected"))
        self.settings["view"]["scope"] = "local-readonly-work"
        self.settings["view"]["attachment"]["primitive"] = "Work"
        for policy in ("explicit-audit", None, True):
            with self.subTest(policy=policy):
                self.settings["view"]["attachment"]["review_policy"] = policy
                self.assertEqual(self.cli("submit", primitive="Work")[0], 2)
        self.assertFalse(any(call["operation"] == "submit" for call in self.calls()))
        self.settings["view"]["attachment"]["review_policy"] = "none"
        self.assertEqual(self.cli("submit", primitive="Work")[0], 0)

    def test_review_validates_root_generation_epoch_and_scope_before_mutation(self):
        self.review()
        original = copy.deepcopy(self.settings["view"])
        for key, value in (("scope", "local-readonly-work"), ("root", "other"),
                           ("generation", "old"), ("attached", 1), ("epoch", True),
                           ("attachment", None)):
            with self.subTest(key=key, value=value):
                self.settings["view"] = {**original, key: value}
                self.rejected_before_mutation()
        self.settings["view"] = original
        for key, value in (("root", "other"), ("epoch", True), ("epoch", 2)):
            with self.subTest(attachment_key=key, value=value):
                self.settings["view"] = copy.deepcopy(original)
                self.settings["view"]["attachment"][key] = value
                self.rejected_before_mutation()

    def test_review_requires_exact_valid_package_path_and_digest(self):
        self.review()
        original = copy.deepcopy(self.settings["view"]["attachment"])
        for key, value in (("package_path", None), ("package_path", "."),
                           ("package_path", str(self.area / "other")),
                           ("package_path", "/invalid\0snapshot"),
                           ("package_digest", None), ("package_digest", "f" * 63),
                           ("package_digest", "A" * 64)):
            with self.subTest(key=key, value=value):
                self.settings["view"]["attachment"] = {**original, key: value}
                self.rejected_before_mutation()

    def test_review_request_cannot_smuggle_policy_or_primitive(self):
        self.review()
        for extra in ({"primitive": "Review"}, {"review_policy": "explicit-audit"},
                      {"harness": "codex"}):
            with self.subTest(extra=extra):
                legacy.write_json(self.request, {"request_id": "audit", "assignment": "Inspect.", **extra})
                result = self.rejected_before_mutation()
                self.assertIn("Invalid Review request", result["error"])
        self.assertEqual(self.calls(), [])

    def test_malformed_review_preflight_responses_cannot_authorize_mutation(self):
        self.review()
        for operation in ("protocol", "status"):
            for raw in ("[]", "null", "truncated", '{"version":1,"version":1}'):
                with self.subTest(operation=operation, raw=raw):
                    self.settings["modes"] = {operation: {"raw": raw}}
                    self.rejected_before_mutation()

    def test_malformed_review_mutation_replies_remain_uncertain_without_retry(self):
        self.review()
        for operation in ("submit", "gather"):
            with self.subTest(operation=operation):
                self.settings["modes"] = {operation: {"raw": "truncated"}}
                before = len(self.calls())
                code, result = self.cli(operation)
                self.assertEqual((code, result["status"], result["operation"]),
                                 (2, "uncertain", operation))
                self.assertFalse(result["retry_automatically"])
                self.assertEqual([call["operation"] for call in self.calls()[before:]],
                                 ["protocol", "status", operation])

    def test_review_view_changes_after_mutation_are_uncertain(self):
        self.review()
        bad = copy.deepcopy(self.settings["view"])
        bad["attachment"].pop("review_policy")
        for operation in ("submit", "gather"):
            with self.subTest(operation=operation):
                self.settings["modes"] = {operation: {"payload": bad}}
                code, result = self.cli(operation)
                self.assertEqual((code, result["status"]), (2, "uncertain"))

    def test_review_observation_timeouts_do_not_claim_a_possible_launch(self):
        self.review()
        for operation in ("protocol", "status"):
            with self.subTest(operation=operation):
                self.settings["modes"] = {operation: {"sleep": 2}}
                before = len(self.calls())
                code, result = self.cli("submit", timeout="0.3")
                self.assertEqual((code, result["status"], result["operation"]),
                                 (2, "rejected", operation))
                self.assertFalse(result["retry_automatically"])
                self.assertNotIn("may still have launched", result["error"])
                self.assertFalse(any(call["operation"] == "submit"
                                     for call in self.calls()[before:]))

    def test_review_gather_timeout_preserves_uncertainty(self):
        self.review()
        self.settings["modes"] = {"gather": {"sleep": 2}}
        code, result = self.cli("gather", timeout="0.3")
        self.assertEqual((code, result["status"], result["operation"]),
                         (2, "uncertain", "gather"))
        self.assertEqual([call["operation"] for call in self.calls()].count("gather"), 1)


if __name__ == "__main__":
    unittest.main()
