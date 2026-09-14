"""Bounded dynamic client contracts with a disposable controller, not a fleet."""

import copy
import json
import subprocess
import sys
import unittest

import test_firstmate_client as legacy
import test_firstmate_context as context_tests


class FirstMateDynamicClientTests(unittest.TestCase):
    setUp = context_tests.FirstMateContextClientTests.setUp
    calls = legacy.FirstMateClientTests.calls

    def dynamic(self):
        self.settings["protocol"].update(primitives=["Work", "Review"],
                                         workflows=["dynamic"],
                                         review_policies=["explicit-audit", "workflow-review"])
        self.settings["view"]["scope"] = "local-dynamic"
        self.settings["view"]["attachment"].update(
            workflow="dynamic", readonly=False, max_components=32,
            review_policy="workflow-review")
        self.settings["view"]["requests"] = []

    def cli(self, operation="status", *, request_id=None):
        legacy.write_json(self.home / "fixture.json", self.settings)
        environment = dict(self.environment, ORCHFLOWS_FIRSTMATE_CONTEXT=str(self.context))
        command = [sys.executable, "-B", str(self.script), "--timeout", "3", operation]
        if operation == "submit":
            command += ["--request", str(self.request)]
        if request_id is not None:
            command += ["--request-id", request_id]
        result = subprocess.run(command, env=environment, capture_output=True, text=True,
                                encoding="utf-8", timeout=15)
        self.assertEqual(result.stderr, "")
        return result.returncode, json.loads(result.stdout)

    def request_body(self, *, primitive="Work", writable=True):
        body = {"request_id": "maker-1", "assignment": "Produce the assigned result.",
                "primitive": primitive, "writable": writable}
        legacy.write_json(self.request, body)
        return body

    def local_delivery(self):
        self.dynamic()
        delivery = dict(kind="ship", mode="local-only", branch="fm/root-1")
        self.settings["protocol"]["root_deliveries"] = ["ship-local-only"]
        self.settings["view"]["scope"] = "local-dynamic-ship-local-only"
        self.settings["view"]["attachment"]["root_delivery"] = delivery
        self.context_data["root_delivery"] = delivery
        legacy.write_json(self.context, self.context_data)
        return delivery

    def test_local_only_context_negotiates_delivery_before_dynamic_submit(self):
        self.local_delivery()
        body = self.request_body()
        code, result = self.cli("submit")
        self.assertEqual(code, 0, result)
        self.assertEqual(result["request"]["body"], body)
        self.assertEqual(result["attachment"]["root_delivery"]["branch"], "fm/root-1")

    def test_local_only_requires_controller_delivery_capability_before_mutation(self):
        self.local_delivery()
        self.request_body()
        for value in (None, [], "ship-local-only", [True], ["ship-local-only", "ship-local-only"]):
            with self.subTest(value=value):
                self.settings["protocol"]["root_deliveries"] = value
                self.assertEqual(self.cli("submit")[0], 2)
        self.assertFalse(any(call["operation"] == "submit" for call in self.calls()))

    def test_context_cannot_rebind_branch_mode_or_scout_delivery(self):
        delivery = self.local_delivery()
        self.request_body()
        for key, value in (("branch", "fm/other"), ("kind", "scout"), ("mode", "no-mistakes")):
            with self.subTest(key=key):
                self.settings["view"]["attachment"]["root_delivery"] = {**delivery, key: value}
                self.assertEqual(self.cli("submit")[0], 2)
        self.settings["view"]["attachment"]["root_delivery"] = delivery
        self.context_data.pop("root_delivery")
        legacy.write_json(self.context, self.context_data)
        self.assertEqual(self.cli("submit")[0], 2)
        self.assertFalse(any(call["operation"] == "submit" for call in self.calls()))

    def test_local_delivery_changed_after_submit_is_uncertain(self):
        self.local_delivery()
        self.request_body()
        changed = copy.deepcopy(self.settings["view"])
        changed["attachment"]["root_delivery"]["branch"] = "fm/other"
        self.settings["modes"] = {"submit": {"payload": changed}}
        code, result = self.cli("submit")
        self.assertEqual((code, result["status"]), (2, "uncertain"))
        self.assertFalse(result["retry_automatically"])
        self.assertEqual([call["operation"] for call in self.calls()].count("submit"), 1)

    def test_dynamic_context_work_selects_returned_profile_and_aggregate(self):
        self.dynamic()
        item = copy.deepcopy(self.settings["view"])
        item.pop("requests")
        item.update(request={"body": {"request_id": "maker-1"}, "state": "complete"},
                    result={"input_commit": "1" * 40, "output_commit": "2" * 40})
        self.settings["view"]["requests"] = [item]
        self.assertEqual(self.cli(), (0, self.settings["view"]))
        self.assertEqual([call["operation"] for call in self.calls()], ["protocol", "status"])
        self.assertEqual(json.loads(self.context.read_text())["primitive"], "Work")

    def test_dynamic_work_and_review_forward_exact_request_choices(self):
        self.dynamic()
        for primitive, writable in (("Work", True), ("Work", False), ("Review", False)):
            with self.subTest(primitive=primitive, writable=writable):
                body = self.request_body(primitive=primitive, writable=writable)
                code, result = self.cli("submit")
                self.assertEqual(code, 0, result)
                self.assertEqual(result["request"]["body"], body)
                self.assertEqual(self.calls()[-1]["args"],
                                 ["--home", str(self.home), "submit", "root-1",
                                  "--generation", "gen-1", "--request", str(self.request)])

    def test_selected_status_and_gather_forward_only_the_named_request(self):
        self.dynamic()
        body = self.request_body()
        self.settings["view"].update(request={"body": body, "state": "complete", "gathered": True},
                                     result={"input_commit": "1" * 40, "output_commit": "2" * 40})
        self.settings["view"].pop("requests")
        for operation in ("status", "gather"):
            with self.subTest(operation=operation):
                self.assertEqual(self.cli(operation, request_id="maker-1"),
                                 (0, self.settings["view"]))
                self.assertEqual(self.calls()[-1]["args"],
                                 ["--home", str(self.home), operation, "root-1",
                                  "--generation", "gen-1", "--request-id", "maker-1"])

    def test_dynamic_gather_requires_id_before_any_acknowledgement(self):
        self.dynamic()
        code, result = self.cli("gather")
        self.assertEqual((code, result["status"]), (2, "rejected"))
        self.assertIn("--request-id", result["error"])
        self.assertEqual([call["operation"] for call in self.calls()], ["protocol", "status"])

    def test_dynamic_requires_all_declared_capabilities_before_mutation(self):
        self.dynamic()
        self.request_body()
        valid = copy.deepcopy(self.settings["protocol"])
        for key, value in (("workflows", None), ("workflows", "dynamic"),
                           ("workflows", ["dynamic", "dynamic"]), ("workflows", [True]),
                           ("primitives", ["Work"]), ("review_policies", ["explicit-audit"])):
            with self.subTest(key=key, value=value):
                self.settings["protocol"] = {**valid, key: value}
                code, result = self.cli("submit")
                self.assertEqual((code, result["status"]), (2, "rejected"))
        self.assertFalse(any(call["operation"] == "submit" for call in self.calls()))

    def test_dynamic_rejects_expanded_or_ambiguous_profiles(self):
        self.dynamic()
        self.request_body()
        valid = copy.deepcopy(self.settings["view"]["attachment"])
        for key, value in (("workflow", "Build"), ("workflow", None), ("primitive", "Review"),
                           ("readonly", True), ("readonly", 0), ("max_components", 33),
                           ("max_components", True), ("review_policy", "explicit-audit")):
            with self.subTest(key=key, value=value):
                self.settings["view"]["attachment"] = {**valid, key: value}
                code, result = self.cli("submit")
                self.assertEqual((code, result["status"]), (2, "rejected"))
        self.assertFalse(any(call["operation"] == "submit" for call in self.calls()))

    def test_request_shape_cannot_upgrade_a_legacy_attachment(self):
        self.request_body()
        code, result = self.cli("submit")
        self.assertEqual((code, result["status"]), (2, "rejected"))
        self.assertIn("single-primitive", result["error"])
        self.assertFalse(any(call["operation"] == "submit" for call in self.calls()))

    def test_dynamic_requires_explicit_choices_and_readonly_review(self):
        self.dynamic()
        self.assertEqual(self.cli("submit")[0], 2)
        body = self.request_body()
        before = self.calls()
        for field, value in (("primitive", "Build"), ("primitive", None),
                             ("writable", 1), ("writable", "false")):
            with self.subTest(field=field, value=value):
                legacy.write_json(self.request, {**body, field: value})
                self.assertEqual(self.cli("submit")[0], 2)
        self.request_body(primitive="Review", writable=True)
        self.assertEqual(self.cli("submit")[0], 2)
        self.assertEqual(self.calls(), before)

    def test_invalid_selected_ids_never_contact_controller(self):
        self.dynamic()
        for request_id in ("", "bad id", "../other", "x" * 65):
            with self.subTest(request_id=request_id):
                self.assertEqual(self.cli("gather", request_id=request_id)[0], 2)
        self.assertEqual(self.calls(), [])

    def test_changed_attachment_after_mutation_is_uncertain(self):
        self.dynamic()
        self.request_body()
        changed = copy.deepcopy(self.settings["view"])
        changed["attachment"]["package_digest"] = "b" * 64
        self.settings["modes"] = {"submit": {"payload": changed}}
        code, result = self.cli("submit")
        self.assertEqual((code, result["status"]), (2, "uncertain"))
        self.assertFalse(result["retry_automatically"])
        self.assertEqual([call["operation"] for call in self.calls()].count("submit"), 1)

    def test_wrong_selected_request_cannot_acknowledge_a_different_result(self):
        self.dynamic()
        self.settings["view"]["request"] = {"body": {"request_id": "other"}}
        code, result = self.cli("gather", request_id="maker-1")
        self.assertEqual((code, result["status"]), (2, "rejected"))
        self.assertIn("selected request", result["error"])
        self.assertFalse(any(call["operation"] == "gather" for call in self.calls()))

    def test_changed_dynamic_request_reply_is_uncertain(self):
        self.dynamic()
        body = self.request_body()
        changed = copy.deepcopy(self.settings["view"])
        changed["request"] = {"body": {**body, "writable": False}}
        self.settings["modes"] = {"submit": {"payload": changed}}
        code, result = self.cli("submit")
        self.assertEqual((code, result["status"]), (2, "uncertain"))
        self.assertIn("selected request", result["error"])
        self.assertEqual([call["operation"] for call in self.calls()].count("submit"), 1)

    def test_legacy_context_keeps_unselected_single_request_gather(self):
        self.settings["view"].update(request={"state": "complete", "gathered": True})
        self.assertEqual(self.cli("gather"), (0, self.settings["view"]))
        self.assertEqual(self.calls()[-1]["args"],
                         ["--home", str(self.home), "gather", "root-1",
                          "--generation", "gen-1"])


if __name__ == "__main__":
    unittest.main()
