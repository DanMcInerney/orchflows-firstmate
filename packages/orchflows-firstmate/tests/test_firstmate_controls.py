"""Negotiated assignment controls and scoped caller client boundaries."""
import json
import unittest
import test_firstmate_dynamic as dynamic_fixtures
import test_firstmate_client as legacy


class AssignmentClientTests(unittest.TestCase):
    setUp = dynamic_fixtures.FirstMateDynamicClientTests.setUp
    dynamic = dynamic_fixtures.FirstMateDynamicClientTests.dynamic
    request_body = dynamic_fixtures.FirstMateDynamicClientTests.request_body
    cli = dynamic_fixtures.FirstMateDynamicClientTests.cli
    calls = dynamic_fixtures.FirstMateDynamicClientTests.calls

    def test_controls_forward_exact_body_after_negotiation(self):
        self.dynamic()
        self.settings["protocol"]["assignment_controls"] = ["model-effort-v1"]
        body = dict(self.request_body(), model="claude-sonnet-5", effort="high",
                    assignment_name="maker", operation_defaults={"effort": "medium"})
        legacy.write_json(self.request, body)
        code, result = self.cli("submit")
        self.assertEqual(code, 0, result)
        self.assertEqual(result["request"]["body"], body)
        self.assertEqual(self.calls()[-1]["operation"], "submit")

    def test_controls_require_explicit_capability_before_submit(self):
        self.dynamic()
        legacy.write_json(self.request, dict(self.request_body(), effort="high"))
        for value in (None, [], "model-effort-v1", [True], ["model-effort-v1", "model-effort-v1"]):
            self.settings["protocol"]["assignment_controls"] = value
            code, result = self.cli("submit")
            self.assertEqual(code, 2, result)
            self.assertIn("model-effort-v1", result["error"])
        self.assertFalse(any(call["operation"] == "submit" for call in self.calls()))

    def test_invalid_axes_refuse_before_controller_contact(self):
        self.dynamic()
        body = self.request_body()
        for fields in ({"model": ""}, {"model": "-m"}, {"model": "a b"},
                       {"effort": None}, {"effort": True}, {"effort": "maximum"},
                       {"operation_defaults": []}, {"operation_defaults": {"harness": "codex"}},
                       {"assignment_name": "../escape"}, {"assignment_name": True}):
            legacy.write_json(self.request, dict(body, **fields))
            self.assertEqual(self.cli("submit")[0], 2)
        self.assertEqual(self.calls(), [])

    def test_current_package_negotiates_default_semantics_without_overrides(self):
        self.dynamic()
        legacy.write_json(self.package / "scripts/firstmate-client.json",
                          {"schema": 1, "assignment_controls": ["model-effort-v1"]})
        self.request_body()
        self.assertEqual(self.cli("submit")[0], 2)
        self.settings["protocol"]["assignment_controls"] = ["model-effort-v1"]
        self.assertEqual(self.cli("submit")[0], 0)

    def test_saved_preferences_require_controls_even_without_caller_override(self):
        self.dynamic()
        self.settings["view"]["attachment"]["workflow_preferences"] = {
            "operations": {"Review": {"effort": "high"}}}
        self.request_body()
        self.assertEqual(self.cli("submit")[0], 2)
        self.assertFalse(any(call["operation"] == "submit" for call in self.calls()))

    def test_workflow_call_requires_capability_and_preserves_request_identity(self):
        self.dynamic()
        body = dict(self.request_body(), workflow_call="phase-a")
        legacy.write_json(self.request, body)
        self.assertEqual(self.cli("submit")[0], 2)
        self.settings["protocol"]["composition"] = ["scoped-composition-v1"]
        code, result = self.cli("submit")
        self.assertEqual(code, 0, result)
        self.assertEqual(result["request"]["body"], body)

    def test_descendant_context_keeps_actual_caller_and_outer_attachment_distinct(self):
        self.dynamic()
        self.context_data["group_root"] = "outer-root"
        legacy.write_json(self.context, self.context_data)
        self.settings["view"]["attachment"]["root"] = "outer-root"
        self.request_body()
        self.assertEqual(self.cli("submit")[0], 2)
        self.settings["protocol"]["composition"] = ["scoped-composition-v1"]
        code, result = self.cli("submit")
        self.assertEqual(code, 0, result)
        self.assertEqual(result["root"], "root-1")
        self.assertEqual(result["attachment"]["root"], "outer-root")


if __name__ == "__main__":
    unittest.main()
