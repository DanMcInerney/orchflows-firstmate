"""Exercise parent lock custody with real FirstMate lock helpers and a fake launch boundary."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[3]
SOURCE = Path(os.environ.get("FIRSTMATE_TEST_SOURCE", ROOT / ".sources/firstmate"))
BRIDGE = ROOT / "integrations/firstmate/overlay/bin/fm-task-group-spawn.sh"


@unittest.skipUnless(os.name == "posix", "FirstMate's launch bridge runs under Unix Bash")
class SpawnBridgeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="fm-group-bridge-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.code = self.root / "code"
        shutil.copytree(SOURCE / "bin", self.code / "bin")
        shutil.copyfile(BRIDGE, self.code / "bin/fm-task-group-spawn.sh")
        shutil.copyfile(BRIDGE.with_name("fm-task-group-runtime.sh"), self.code / "bin/fm-task-group-runtime.sh")
        self.bridge = self.code / "bin/fm-task-group-spawn.sh"
        self.home = self.root / "home"
        for name in ("state", "data", "config"):
            (self.home / name).mkdir(parents=True)
        self.project = self.root / "project"
        self.project.mkdir()
        self.meta = self.home / "state/root.meta"
        self.meta.write_text(f"spawn_gen=s1\nbackend=herdr\nkind=scout\ntask_group_role=root\nproject={self.project}\nharness=codex\nmodel=default\neffort=default\nherdr_session=fm-lab-bridge\n")
        self.env = {key: value for key, value in os.environ.items() if not key.startswith(("FM_", "HERDR_"))}
        self.env.update(FM_HOME=str(self.home), FM_ROOT_OVERRIDE=str(self.code), BRIDGE_HOME=str(self.home))
        self.spy = self.home / "spawn.json"
        (self.code / "bin/fm-spawn.sh").write_text("#!/usr/bin/env python3\nimport json,os,sys\nfrom pathlib import Path\nPath(os.environ['BRIDGE_HOME'],'spawn.json').write_text(json.dumps({'args':sys.argv[1:],'session':os.environ.get('HERDR_SESSION')}))\nsys.exit(int(os.environ.get('BRIDGE_SPAWN_EXIT','0')))\n")
        (self.code / "bin/fm-spawn.sh").chmod(0o755)

    def call(self, *args, env=None):
        return subprocess.run(["bash", str(self.bridge), *map(str, args)], env=env or self.env,
                              capture_output=True, text=True, timeout=15)

    def args(self, generation="s1"):
        return ("root", generation, "tg-" + "a" * 20, self.project, "codex", "default", "default")

    def test_stale_parent_refuses_without_launch_or_leftover_lock(self):
        result = self.call(*self.args("old"))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("stale", result.stderr)
        self.assertFalse(self.spy.exists())
        self.assertEqual(list((self.home / "state").glob(".*.lock")), [])

    def test_launch_inherits_profile_and_exact_session_and_releases_locks_on_failure(self):
        env = dict(self.env, BRIDGE_SPAWN_EXIT="5")
        result = self.call(*self.args(), env=env)
        self.assertEqual(result.returncode, 5, result.stderr)
        report = json.loads(self.spy.read_text())
        self.assertEqual(report["session"], "fm-lab-bridge")
        self.assertEqual(report["args"], ["tg-" + "a" * 20, str(self.project), "--scout", "--backend", "herdr", "--harness", "codex"])
        self.assertEqual(list((self.home / "state").glob(".*.lock")), [])

    def test_internal_verification_rejects_unowned_environment_marker(self):
        env = dict(self.env, FM_TASK_GROUP_LOCK_OWNER=str(os.getpid()),
                   FM_TASK_GROUP_LOCK_ROOT="root", FM_TASK_GROUP_LOCK_HOME=str(self.home))
        result = self.call("--verify-lock", "root", "s1", env=env)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.spy.exists())

    def test_submit_holds_parent_locks_and_nested_launch_proves_ancestor_custody(self):
        # Replace only the new controller boundary. The actual bridge, parent
        # control/meta locks and nested launch validation remain exercised.
        (self.code / "bin/fm-task-group.py").write_text('''import json,os,subprocess,sys
from pathlib import Path
b=Path(__file__).with_name("fm-task-group-spawn.sh")
h=Path(os.environ["FM_HOME"])
assert (h/"state/.control-root.lock/pid").is_file()
subprocess.run(["bash",str(b),"--verify-lock","root","s1"],check=True)
subprocess.run(["bash",str(b),"root","s1","tg-"+"a"*20,str(h.parent/"project"),"codex","default","default"],check=True)
print(json.dumps({"status":"launched"}))
''')
        result = self.call("--submit", "root", "s1", self.home / "request.json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {"status": "launched"})
        self.assertTrue(self.spy.exists())
        self.assertEqual(list((self.home / "state").glob(".*.lock")), [])


if __name__ == "__main__":
    unittest.main()
