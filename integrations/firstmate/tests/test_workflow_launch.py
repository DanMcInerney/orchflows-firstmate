"""Exercise FirstMate's actual launch quoting and environment filtering with Python."""
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

import test_task_group as fixtures
from fm_orchflows import launch_context


class WorkflowLaunchTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.ControllerTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.owner = self.fixture.owner

    def test_context_survives_filter_and_clears_inherited_context(self):
        source = (Path(os.environ["FM_STAGE1_FIRSTMATE_ROOT"]) / "bin/fm-spawn.sh").read_text()
        quote = "shell_quote() {" + source.split("shell_quote() {", 1)[1].split("\n}\n", 1)[0] + "\n}\n"
        launch = "ORCHFLOWS_CONTEXT=\n" + source.split("\nORCHFLOWS_CONTEXT=\n", 1)[1].split(
            '\nif [ "$HARNESS" = claude ] &&', 1)[0]
        observer = self.fixture.base / "observe context.py"
        observer.write_text("import os,json; print(json.dumps(os.environ.get('ORCHFLOWS_FIRSTMATE_CONTEXT')))\n")
        script = quote + '''
set -eu
fm_task_group_python() { "$PYTHON" -B "$@"; }
LAUNCH="$(shell_quote "$PYTHON") $(shell_quote "$OBSERVER")"
''' + launch + '''
if [ "$FILTER" = 1 ]; then
  LAUNCH="/usr/bin/env -i PATH=/usr/bin:/bin /bin/sh -c $(shell_quote "$LAUNCH")"
fi
eval "$LAUNCH"
'''
        for bound in ("0", "1"):
            for filtered in ("0", "1"):
                with self.subTest(bound=bound, filtered=filtered):
                    env = dict(os.environ, PYTHON=sys.executable, OBSERVER=str(observer),
                               FM_HOME=str(self.owner.home), SCRIPT_DIR=str(fixtures.BIN),
                               ID="root", SPAWN_GEN="s1.123.4", TASK_GROUP_BOUND=bound,
                               FILTER=filtered, ORCHFLOWS_FIRSTMATE_CONTEXT="/stale/parent.json")
                    result = subprocess.run(["bash", "-c", script], env=env,
                                            capture_output=True, text=True, timeout=30)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    observed = json.loads(result.stdout)
                    if bound == "1":
                        self.assertEqual(observed, launch_context(self.owner, "root", "s1.123.4"))
                        self.assertEqual(json.loads(Path(observed).read_text())["generation"], "s1.123.4")
                    else:
                        self.assertEqual(observed, "")


if __name__ == "__main__":
    unittest.main()
