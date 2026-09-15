"""The actual shipped core must install, resolve and keep its documentation reachable."""

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
SKILLS = {"orch-work", "orch-review", "orch-dynamic-workflow", "orch-self-improve", "orch-build-workflow"}


class InstalledCliTests(unittest.TestCase):
    def test_real_core_installs_resolves_and_keeps_its_documentation_reachable(self):
        with tempfile.TemporaryDirectory(prefix="orchflows-installed-cli-") as temporary:
            outside = Path(temporary).resolve()
            home = outside / "home"
            project = outside / "unrelated-project"
            project.mkdir()
            environment = dict(os.environ, ORCHFLOWS_FIRSTMATE_HOME=str(home), PYTHONDONTWRITEBYTECODE="1",
                               CODEX_HOME=str(outside / "codex"), CLAUDE_CONFIG_DIR=str(outside / "claude"))

            def cli(python, script, *arguments, expected=0):
                result = subprocess.run(
                    [str(python), "-B", str(script), *map(str, arguments)],
                    cwd=project, env=environment, capture_output=True, text=True, timeout=60,
                )
                self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
                return json.loads(result.stdout or result.stderr)

            installed = cli(sys.executable, ROOT / "scripts/orchflows.py", "setup", "--example", "social-search")
            self.assertEqual(installed["status"], "ready", installed)
            self.assertFalse((outside / "codex").exists())
            self.assertFalse((outside / "claude").exists())
            for absent in ("host_configs", "host_config_status", "readiness_scope", "integration"):
                self.assertNotIn(absent, installed)
            python = installed["runtime_python"]
            core = Path(installed["core"]["package_root"])
            script = core / "scripts/orchflows.py"
            self.assertEqual(sorted(path.name for path in (core / "scripts").glob("*.py")),
                             ["orchflows.py", "package_identity.py"])
            self.assertFalse((core / "example-workflows").exists())
            self.assertEqual(cli(python, script, "setup")["core"]["status"], "reused")
            self.assertEqual(cli(python, script, "doctor")["status"], "ready")

            self.assertEqual({skill.name for skill in (core / "skills").iterdir()}, SKILLS)
            for skill in SKILLS:
                for alias in ("orchflows", "orchflows-firstmate"):
                    resolved_core = cli(python, script, "resolve", alias, "--skill", skill)
                    self.assertEqual(Path(resolved_core["skill_path"]), core / "skills" / skill / "SKILL.md")
                text = (core / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
                self.assertRegex(text, rf"^---\nname: {skill}\ndescription: .+\n---\n", "frontmatter")
                self.assertLess(len(text.split()), 260, f"{skill} is not terse")
            self.assertIn("Use when no more specific workflow is named",
                          (core / "skills/orch-dynamic-workflow/SKILL.md").read_text(encoding="utf-8"))
            unavailable = cli(python, script, "resolve", "orchflows", "--skill", "orch-parallel", expected=2)
            self.assertIn("error", unavailable)

            def files(path):
                return {item.relative_to(path).as_posix(): hashlib.sha256(item.read_bytes()).hexdigest()
                        for item in path.rglob("*") if item.is_file()
                        and "__pycache__" not in item.parts and item.suffix not in {".pyc", ".pyo"}}

            self.assertEqual(files(ROOT / "example-workflows/social-search"), files(home / "libraries/social-search"))
            resolved = cli(python, script, "resolve", "social-search", "--skill", "social-search")
            self.assertEqual(resolved["runtime_python"], python)
            self.assertEqual(Path(resolved["skill_path"]), home / "libraries/social-search/skills/social-search/SKILL.md")

            for document in core.rglob("*.md"):
                for target in re.findall(r'\]\(([^)\s]+)(?:\s+"[^"]*")?\)', document.read_text(encoding="utf-8")):
                    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target):
                        continue
                    relative = unquote(target.partition("#")[0])
                    linked = (document.parent / relative).resolve() if relative else document
                    with self.subTest(document=document.relative_to(core), target=target):
                        self.assertTrue(linked.is_relative_to(core), "Link escapes the installed package")
                        self.assertTrue(linked.exists(), "Link target is absent from the installed package")


if __name__ == "__main__":
    unittest.main()
