"""Upgrade regression using the exact pre-context dev.4 client."""
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import unittest

import test_enablement as enablement
from fm_orchflows import enable, launch_context, supports_launch_context
from fm_task_group_launch import launch_meta, launch_overlay
from fm_task_group_store import GroupError


class LegacyClientUpgradeTests(unittest.TestCase):
    def setUp(self):
        self.fixture = enablement.EnablementTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.owner = self.fixture.owner
        self.owner.code_root = Path(os.environ["FM_STAGE1_FIRSTMATE_ROOT"]).resolve()
        package = self.fixture.package
        (package / "scripts/firstmate-client.json").unlink()
        legacy = Path(__file__).parent / "fixtures/firstmate-dev4.py"
        payload = legacy.read_bytes()
        self.assertEqual(hashlib.sha256(payload).hexdigest(), "febc4304b844878d1acc4eb14dbf782ab3602f12b803dfb421fc9a52c983fdc9")
        (package / "scripts/firstmate.py").write_bytes(payload)

    def test_new_enablement_refuses_undeclared_client_before_publication(self):
        with self.assertRaisesRegex(GroupError, "declaring launch-context support"):
            enable(self.owner, self.fixture.package, self.fixture.project)
        self.assertFalse((self.owner.home / "config/orchflows.json").exists())

    def test_legacy_relaunch_status_and_gather_keep_accepted_work(self):
        owner, fixture = self.owner, self.fixture.fixture
        owner.attach("legacy", self.fixture.package, self.fixture.project)
        meta = dict(fixture.root_meta, endpoint_task_id="legacy")
        meta.update(fixture.fields(launch_meta(owner, "legacy")))
        fixture.save_meta("legacy", meta)
        child = owner.submit("legacy", meta["spawn_gen"], fixture.body)["request"]["child"]
        owner.complete(child, "s2.345.6", fixture.report(child))
        meta["spawn_gen"] = "s3.456.7"
        fixture.save_meta("legacy", meta)
        self.assertEqual(launch_context(owner, "legacy", meta["spawn_gen"]), "")
        overlay = launch_overlay(owner, "legacy")
        self.assertIn("--generation CURRENT_SPAWN_GEN", overlay)
        self.assertNotIn("do not add authority flags", overlay)
        for operation in ("status", "gather"):
            command = next(line.strip() for line in overlay.splitlines()
                           if line.strip().endswith(" " + operation))
            argv = shlex.split(command.replace("CURRENT_SPAWN_GEN", meta["spawn_gen"]))
            result = subprocess.run(argv, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            value = json.loads(result.stdout)
            self.assertEqual(value["request"]["child"], child)
            self.assertEqual(value["generation"], meta["spawn_gen"])
            if operation == "gather":
                self.assertEqual(value["request"]["gathered_parent_gen"], meta["spawn_gen"])

    def test_legacy_review_keeps_explicit_primitive(self):
        self.owner.attach("audit", self.fixture.package, self.fixture.project, "Review", "explicit-audit")
        overlay = launch_overlay(self.owner, "audit")
        for operation in ("status", "submit", "gather"):
            self.assertIn("--primitive Review " + operation, overlay)

    def test_unknown_capability_metadata_is_not_legacy(self):
        marker = self.fixture.package / "scripts/firstmate-client.json"
        for value in ({"schema": True, "launch_context_schema": 1},
                      {"schema": 1, "launch_context_schema": 2}):
            marker.write_text(json.dumps(value))
            with self.assertRaisesRegex(GroupError, "capability"):
                supports_launch_context(self.fixture.package)


if __name__ == "__main__":
    unittest.main()
