"""Launch-context client calls with private Linux snapshots and a fixture controller."""

import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import test_firstmate_client as legacy
import test_firstmate_review as review_tests


class FirstMateContextClientTests(unittest.TestCase):
    calls = legacy.FirstMateClientTests.calls
    review = review_tests.FirstMateReviewClientTests.review

    def setUp(self):
        legacy.FirstMateClientTests.setUp(self)
        self.environment.pop("ORCHFLOWS_FIRSTMATE_CONTEXT", None)
        self.context = self.area / "launch context.json"
        self.context_data = {
            "schema": 1, "firstmate_root": str(self.code), "home": str(self.home),
            "root": "root-1", "generation": "gen-1", "primitive": "Work",
            "package_path": str(self.package),
        }
        legacy.write_json(self.context, self.context_data)

    def cli(self, operation="status", *, context="environment", extra=()):
        legacy.write_json(self.home / "fixture.json", self.settings)
        environment = dict(self.environment)
        command = [sys.executable, "-B", str(self.script), "--timeout", "3"]
        if context == "environment":
            environment["ORCHFLOWS_FIRSTMATE_CONTEXT"] = str(self.context)
        elif context == "argument":
            # An explicit selected file wins over an unrelated inherited value.
            environment["ORCHFLOWS_FIRSTMATE_CONTEXT"] = str(self.area / "missing-context")
            command.extend(("--context", str(self.context)))
        command.extend(extra)
        command.append(operation)
        if operation == "submit":
            command.extend(("--request", str(self.request)))
        result = subprocess.run(command, env=environment, capture_output=True, text=True,
                                encoding="utf-8", timeout=15)
        self.assertEqual(result.stderr, "", result.stderr)
        return result.returncode, json.loads(result.stdout)

    def rejected_before_controller(self, **kwargs):
        before = self.calls()
        code, result = self.cli("submit", **kwargs)
        self.assertEqual((code, result["status"]), (2, "rejected"))
        self.assertEqual(result["operation"], "preflight")
        self.assertFalse(result["retry_automatically"])
        self.assertEqual(self.calls(), before)
        return result

    def test_short_environment_commands_preserve_work_request_result_and_identity(self):
        self.assertEqual(self.cli(), (0, self.settings["view"]))
        code, result = self.cli("submit")
        self.assertEqual(code, 0)
        self.assertEqual(result["request"]["body"],
                         json.loads(self.request.read_text(encoding="utf-8")))
        self.assertEqual(self.calls()[-1]["args"],
                         ["--home", str(self.home), "submit", "root-1",
                          "--generation", "gen-1", "--request", str(self.request)])
        self.settings["view"].update(request={"state": "complete", "gathered": True})
        self.assertEqual(self.cli("gather"), (0, self.settings["view"]))
        self.assertEqual(self.calls()[-1]["args"],
                         ["--home", str(self.home), "gather", "root-1", "--generation", "gen-1"])
        self.assertTrue(all(call["bytecode"] for call in self.calls()))
        self.assertFalse(list(self.package.rglob("__pycache__")))
        self.assertFalse((self.area / "wrong-firstmate-home").exists())

    def test_explicit_context_file_selects_launch_over_inherited_environment(self):
        self.assertEqual(self.cli(context="argument"), (0, self.settings["view"]))

    def test_review_context_still_requires_explicit_controller_authorization(self):
        self.context_data["primitive"] = "Review"
        legacy.write_json(self.context, self.context_data)
        self.assertEqual(self.cli("submit")[0], 2)
        self.assertEqual([call["operation"] for call in self.calls()], ["protocol"])
        self.review()
        self.assertEqual(self.cli("submit")[0], 0)
        self.settings["view"]["attachment"]["review_policy"] = "none"
        before = len(self.calls())
        self.assertEqual(self.cli("gather")[0], 2)
        self.assertEqual([call["operation"] for call in self.calls()[before:]], ["protocol", "status"])

    def test_context_work_cannot_accept_review_attachment(self):
        self.review()
        self.assertEqual(self.cli("submit")[0], 2)
        self.assertFalse(any(call["operation"] == "submit" for call in self.calls()))

    def test_manual_authority_cannot_override_any_context_field(self):
        for field, value in (("firstmate-root", str(self.code)), ("home", str(self.home)),
                             ("root", "root-1"), ("generation", "gen-1"),
                             ("primitive", "Work")):
            for source in ("environment", "argument"):
                with self.subTest(field=field, source=source):
                    result = self.rejected_before_controller(
                        context=source, extra=("--" + field, value))
                    self.assertIn("mixed", result["error"])

    def test_missing_context_and_incomplete_explicit_inputs_refuse(self):
        for extra in ((), ("--root", "root-1"), ("--primitive", "Work")):
            with self.subTest(extra=extra):
                self.rejected_before_controller(context=None, extra=extra)
        self.environment["ORCHFLOWS_FIRSTMATE_CONTEXT"] = ""
        self.rejected_before_controller(context=None)

    def test_context_requires_exact_schema_fields_and_types(self):
        candidates = [{key: value for key, value in self.context_data.items() if key != missing}
                      for missing in self.context_data]
        for key, value in (("schema", True), ("schema", 2), ("root", True), ("generation", 1),
                           ("root", "bad root"), ("generation", ""), ("primitive", "Dynamic"),
                           ("primitive", None), ("home", None), ("firstmate_root", []),
                           ("package_path", False), ("extra", "not-supported")):
            candidates.append({**self.context_data, key: value})
        for context in candidates:
            with self.subTest(context=context):
                legacy.write_json(self.context, context)
                self.rejected_before_controller()

    def test_context_rejects_invalid_json_unicode_duplicates_and_size(self):
        for raw in (b"[]", b"null", b"{}", b"invalid", b"\xff",
                    b'{"schema":1,"schema":1}', b" " * (16 * 1024 + 1),
                    b"[" * 1500):
            with self.subTest(raw=raw[:40]):
                self.context.write_bytes(raw)
                self.rejected_before_controller()

    def test_context_requires_existing_canonical_absolute_authority_directories(self):
        other = self.area / "other-package"
        other.mkdir()
        for key in ("firstmate_root", "home", "package_path"):
            for value in (".", str(self.area / "missing"), str(self.request),
                          str(self.area / ".." / self.area.name), "/invalid\0path"):
                with self.subTest(key=key, value=value):
                    legacy.write_json(self.context, {**self.context_data, key: value})
                    self.rejected_before_controller()
        legacy.write_json(self.context, {**self.context_data, "package_path": str(other)})
        self.assertIn("exact context package snapshot", self.rejected_before_controller()["error"])

    @unittest.skipUnless(sys.platform == "linux", "Linux context file semantics")
    def test_context_refuses_symlinks_and_nonregular_files(self):
        original = self.context
        link = self.area / "context-link.json"
        link.symlink_to(original)
        self.context = link
        self.rejected_before_controller()
        parent_link = self.area / "parent-link"
        parent_link.symlink_to(self.area, target_is_directory=True)
        self.context = parent_link / original.name
        self.rejected_before_controller()
        self.context = original
        for key in ("firstmate_root", "home", "package_path"):
            legacy.write_json(original, {**self.context_data,
                                         key: str(parent_link / Path(self.context_data[key]).name)})
            self.rejected_before_controller()
        fifo = self.area / "context-fifo"
        os.mkfifo(fifo)
        self.context = fifo
        self.rejected_before_controller()
        self.context = self.area
        self.rejected_before_controller()

    def test_old_launch_does_not_upgrade_generation_from_mutable_metadata(self):
        (self.home / "tasks").mkdir()
        (self.home / "tasks/root-1.meta").write_text("spawn_gen: gen-2\n", encoding="utf-8")
        self.settings["view"]["generation"] = "gen-2"
        for operation in ("submit", "gather"):
            with self.subTest(operation=operation):
                before = len(self.calls())
                code, result = self.cli(operation)
                self.assertEqual(code, 2)
                self.assertIn("root and generation", result["error"])
                self.assertEqual([call["operation"] for call in self.calls()[before:]],
                                 ["protocol", "status"])
                self.assertEqual(self.calls()[-1]["args"][-1], "gen-1")
        self.assertEqual(json.loads(self.context.read_text())["generation"], "gen-1")
        new_context = self.area / "replacement launch.json"
        legacy.write_json(new_context, {**self.context_data, "generation": "gen-2"})
        self.context = new_context
        self.assertEqual(self.cli("gather")[0], 0)
        self.assertEqual(self.calls()[-1]["args"][-1], "gen-2")

    def test_imported_context_namespace_remains_unchanged_across_calls(self):
        spec = importlib.util.spec_from_file_location("context_test_client", self.script)
        client = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(client)
        args = argparse.Namespace(context=self.context, timeout=3, operation="status")
        original = vars(args).copy()
        with patch.object(client, "call_controller",
                          side_effect=[self.settings["protocol"], self.settings["view"]] * 2):
            self.assertEqual(client.run(args), self.settings["view"])
            self.assertEqual(client.run(args), self.settings["view"])
        self.assertEqual(vars(args), original)


if __name__ == "__main__":
    unittest.main()
