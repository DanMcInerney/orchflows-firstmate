"""Observable client boundaries with a disposable controller, never fleet dispatch."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = {"protocol": "firstmate-task-group", "version": 1,
            "experimental": True, "scope": "local-readonly-work"}
FIXTURE = '''import json, os, pathlib, sys, time
home = pathlib.Path(sys.argv[2])
operation = sys.argv[3]
settings = json.loads((home / "fixture.json").read_text(encoding="utf-8"))
with (home / "calls.jsonl").open("a", encoding="utf-8") as out:
    out.write(json.dumps({"operation": operation, "args": sys.argv[1:],
                          "bytecode": sys.dont_write_bytecode}) + "\\n")
mode = settings.get("modes", {}).get(operation, {})
time.sleep(mode.get("sleep", 0))
payload = settings["protocol"] if operation == "protocol" else settings["view"]
payload = mode.get("payload", payload)
if operation == "submit" and "payload" not in mode:
    request = pathlib.Path(sys.argv[sys.argv.index("--request") + 1])
    payload["request"] = {"body": json.loads(request.read_text(encoding="utf-8")),
                          "child": "tg-fixture", "state": "launched"}
stream = sys.stderr if mode.get("stderr") else sys.stdout
print(mode.get("raw", json.dumps(payload)), file=stream)
sys.exit(mode.get("exit", 0))
'''


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


class FirstMateClientTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="firstmate-client-")
        self.addCleanup(temporary.cleanup)
        self.area = Path(temporary.name).resolve()
        self.package = self.area / "package snapshot with spaces"
        self.script = self.package / "scripts/firstmate.py"
        self.script.parent.mkdir(parents=True)
        shutil.copyfile(ROOT / "scripts/firstmate.py", self.script)
        for relative in ("plugin.json", ".codex-plugin/plugin.json", ".claude-plugin/plugin.json"):
            write_json(self.package / relative, {"name": "orchflows-firstmate", "version": "0.1.0-dev.2"})
        self.code = self.area / "FirstMate code"
        (self.code / "bin").mkdir(parents=True)
        (self.code / "bin/fm-task-group.py").write_text(FIXTURE, encoding="utf-8")
        self.home = self.area / "explicit FirstMate home"
        self.home.mkdir()
        self.request = self.area / "request λ.json"
        write_json(self.request, {"request_id": "inspect-1", "assignment": "Inspect source; return findings λ."})
        self.settings = {"protocol": dict(PROTOCOL), "view": {
            **PROTOCOL, "attached": True, "root": "root-1", "generation": "gen-1", "epoch": 1,
            "attachment": {"schema": 1, "root": "root-1", "epoch": 1, "primitive": "Work",
                           "readonly": True, "max_components": 1, "package_path": str(self.package),
                           "package_digest": "a" * 64}, "request": None}}
        self.environment = dict(os.environ, CODEX_HOME=str(self.area / "unused-codex"),
                                CLAUDE_CONFIG_DIR=str(self.area / "unused-claude"),
                                ORCHFLOWS_HOME=str(self.area / "unused-normal-home"),
                                FM_HOME=str(self.area / "wrong-firstmate-home"))
        self.environment.pop("PYTHONDONTWRITEBYTECODE", None)

    def cli(self, operation="status", *, generation="gen-1", timeout="3", script=None):
        write_json(self.home / "fixture.json", self.settings)
        command = [sys.executable, str(script or self.script), "--firstmate-root", str(self.code),
                   "--home", str(self.home), "--root", "root-1", "--generation", generation,
                   "--timeout", timeout, operation]
        if operation == "submit":
            command += ["--request", str(self.request)]
        result = subprocess.run(command, env=self.environment, capture_output=True, text=True,
                                encoding="utf-8", timeout=15)
        self.assertEqual(result.stderr, "", result.stderr)
        return result.returncode, json.loads(result.stdout)

    def calls(self):
        path = self.home / "calls.jsonl"
        return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []

    def test_status_negotiates_and_preserves_owner_response_without_host_writes(self):
        code, result = self.cli()
        self.assertEqual(code, 0)
        self.assertEqual(result, self.settings["view"])
        self.assertEqual([call["operation"] for call in self.calls()], ["protocol", "status"])
        self.assertTrue(all(call["bytecode"] for call in self.calls()))
        self.assertFalse(list(self.package.rglob("__pycache__")))
        for relative in ("unused-codex", "unused-claude", "unused-normal-home", "wrong-firstmate-home"):
            self.assertFalse((self.area / relative).exists())

    def test_submit_forwards_exact_request_with_explicit_identity_and_no_shell(self):
        code, result = self.cli("submit")
        self.assertEqual(code, 0)
        self.assertEqual(result["request"]["body"], json.loads(self.request.read_text(encoding="utf-8")))
        self.assertEqual([call["operation"] for call in self.calls()], ["protocol", "status", "submit"])
        self.assertEqual(self.calls()[-1]["args"], ["--home", str(self.home), "submit", "root-1",
                                                   "--generation", "gen-1", "--request", str(self.request)])

    def test_gather_preserves_retained_result_and_acknowledgement(self):
        self.settings["view"].update(request={"state": "complete", "gathered": True},
                                     result={"report_digest": "b" * 64}, report_path="owner-retained-report")
        code, result = self.cli("gather")
        self.assertEqual(code, 0)
        self.assertEqual(result, self.settings["view"])
        self.assertEqual([call["operation"] for call in self.calls()], ["protocol", "status", "gather"])

    def test_missing_controller_refuses_without_fallback(self):
        (self.code / "bin/fm-task-group.py").unlink()
        code, result = self.cli("submit")
        self.assertEqual(code, 2)
        self.assertIn("controller is missing", result["error"])
        self.assertEqual(self.calls(), [])

    def test_wrong_protocol_and_scope_refuse_before_status(self):
        for key, value in (("version", 2), ("version", True), ("protocol", "other"),
                           ("experimental", False), ("scope", "full-work")):
            with self.subTest(key=key, value=value):
                self.settings["protocol"] = {**PROTOCOL, key: value}
                code, result = self.cli("submit")
                self.assertEqual(code, 2)
                self.assertIn("Unsupported", result["error"])
        self.assertTrue(all(call["operation"] == "protocol" for call in self.calls()))

    def test_stale_or_wrong_root_view_cannot_dispatch(self):
        for key, value in (("generation", "old"), ("root", "other"), ("attached", False), ("generation", 1)):
            with self.subTest(key=key):
                self.settings["modes"] = {"status": {"payload": {**self.settings["view"], key: value}}}
                code, result = self.cli("submit")
                self.assertEqual(code, 2)
                self.assertIn("root and generation", result["error"])
        self.assertFalse(any(call["operation"] == "submit" for call in self.calls()))

    def test_missing_or_unsupported_attachment_refuses(self):
        for attachment in (None, {}, {**self.settings["view"]["attachment"], "readonly": False},
                           {**self.settings["view"]["attachment"], "max_components": 2}):
            with self.subTest(attachment=attachment):
                self.settings["modes"] = {"status": {"payload": {**self.settings["view"], "attachment": attachment}}}
                self.assertEqual(self.cli("submit")[0], 2)
        self.assertFalse(any(call["operation"] == "submit" for call in self.calls()))

    def test_different_or_unpinned_snapshot_cannot_substitute(self):
        for key, value in (("package_path", str(self.area / "other")), ("package_path", "."),
                           ("package_digest", "")):
            with self.subTest(key=key):
                attachment = {**self.settings["view"]["attachment"], key: value}
                self.settings["modes"] = {"status": {"payload": {**self.settings["view"], "attachment": attachment}}}
                code, result = self.cli("submit")
                self.assertEqual(code, 2)
                self.assertIn("exact FirstMate-attached", result["error"])
        self.assertFalse(any(call["operation"] == "submit" for call in self.calls()))

    def test_normal_or_inconsistent_package_fails_before_controller(self):
        for change in ({"name": "orchflows", "version": "0.1.0-dev.2"},
                       {"name": "orchflows-firstmate", "version": "0.7.0"}):
            with self.subTest(change=change):
                write_json(self.package / "plugin.json", change)
                code, result = self.cli("submit")
                self.assertEqual(code, 2)
                self.assertIn("Invalid fork package", result["error"])
        self.assertEqual(self.calls(), [])

    def test_invalid_request_never_contacts_controller(self):
        cases = [{"request_id": "one", "assignment": "inspect", "model": "override"},
                 {"request_id": "one"}, {"request_id": "", "assignment": "inspect"},
                 {"request_id": "one", "assignment": None}, []]
        for value in cases:
            with self.subTest(value=value):
                write_json(self.request, value)
                self.assertEqual(self.cli("submit")[0], 2)
        self.request.write_text('{"request_id":"one","assignment":"a","assignment":"b"}', encoding="utf-8")
        self.assertEqual(self.cli("submit")[0], 2)
        self.assertEqual(self.calls(), [])

    def test_controller_rejections_are_returned_unchanged(self):
        rejection = {"error": "parent generation changed during admission", "execution_ready": False}
        self.settings["modes"] = {"submit": {"payload": rejection, "stderr": True, "exit": 2}}
        code, result = self.cli("submit")
        self.assertEqual((code, result), (2, rejection))
        self.assertEqual([call["operation"] for call in self.calls()].count("submit"), 1)

    def test_malformed_or_error_success_response_never_authorizes_dispatch(self):
        for mode in ({"raw": "not JSON"}, {"raw": "[]"},
                     {"raw": '{"version":1,"version":1}'}, {"payload": {"error": "not attached"}}):
            with self.subTest(mode=mode):
                self.settings["modes"] = {"status": mode}
                self.assertEqual(self.cli("submit")[0], 2)
        self.assertFalse(any(call["operation"] == "submit" for call in self.calls()))

    def test_malformed_submit_response_remains_uncertain_without_retry(self):
        self.settings["modes"] = {"submit": {"raw": "truncated response"}}
        code, result = self.cli("submit")
        self.assertEqual(code, 2)
        self.assertEqual(result["status"], "uncertain")
        self.assertFalse(result["retry_automatically"])
        self.assertEqual([call["operation"] for call in self.calls()].count("submit"), 1)

    def test_controller_timeout_is_uncertain_and_never_retried(self):
        self.settings["modes"] = {"submit": {"sleep": 4}}
        code, result = self.cli("submit", timeout="1")
        self.assertEqual(code, 2)
        self.assertEqual((result["status"], result["operation"]), ("uncertain", "submit"))
        self.assertFalse(result["retry_automatically"])
        self.assertEqual([call["operation"] for call in self.calls()].count("submit"), 1)

    def test_invalid_timeout_and_generation_do_not_contact_controller(self):
        for value in ("0", "-1", "nan", "inf"):
            with self.subTest(timeout=value):
                self.assertEqual(self.cli(timeout=value)[0], 2)
        self.assertEqual(self.cli(generation="bad generation")[0], 2)
        self.assertEqual(self.calls(), [])


if __name__ == "__main__":
    unittest.main()
