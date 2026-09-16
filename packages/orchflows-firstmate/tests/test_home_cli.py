"""The checkout is the core: its skills, policy files and documentation must be complete and self-contained."""

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
SKILLS = {"orch-work", "orch-review", "orch-dynamic-workflow", "orch-build-workflow"}


class CorePackageTests(unittest.TestCase):
    def test_core_ships_only_the_four_skills_with_policy_and_terse_bodies(self):
        self.assertEqual({skill.name for skill in (ROOT / "skills").iterdir()}, SKILLS)
        self.assertFalse((ROOT / "example-workflows").exists(), "no example libraries ship here")
        self.assertEqual(sorted(path.name for path in (ROOT / "scripts").glob("*.py")), ["orchflows.py"])
        for skill in SKILLS:
            text = (ROOT / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
            with self.subTest(skill=skill):
                self.assertRegex(text, rf"^---\nname: {skill}\ndescription: .+\ndisable-model-invocation: (true|false)\n---\n", "frontmatter")
                self.assertLess(len(text.split()), 260, f"{skill} is not terse")
                self.assertTrue((ROOT / "skills" / skill / "agents/openai.yaml").is_file(), "Codex policy")
        self.assertIn("Use when no more specific workflow is named",
                      (ROOT / "skills/orch-dynamic-workflow/SKILL.md").read_text(encoding="utf-8"))

    def test_every_core_markdown_link_resolves_inside_the_checkout(self):
        for document in ROOT.rglob("*.md"):
            if "tests" in document.relative_to(ROOT).parts:
                continue
            for target in re.findall(r'\]\(([^)\s]+)(?:\s+"[^"]*")?\)', document.read_text(encoding="utf-8")):
                if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target):
                    continue
                relative = unquote(target.partition("#")[0])
                linked = (document.parent / relative).resolve() if relative else document
                with self.subTest(document=document.relative_to(ROOT), target=target):
                    self.assertTrue(linked.is_relative_to(ROOT), "Link escapes the package")
                    self.assertTrue(linked.exists(), "Link target is absent")

    def test_checkout_cli_prepares_a_home_for_saved_libraries_without_copying_the_core(self):
        with tempfile.TemporaryDirectory(prefix="orchflows-firstmate-cli-") as temporary:
            outside = Path(temporary).resolve()
            home = outside / "home"
            project = outside / "unrelated-project"
            project.mkdir()
            library = home / "libraries/quickfix"
            (library / "skills/fix").mkdir(parents=True)
            (library / "plugin.json").write_text(json.dumps({"name": "quickfix", "version": "0.1.0"}), encoding="utf-8")
            (library / "skills/fix/SKILL.md").write_text("---\nname: fix\ndescription: Fixture.\ndisable-model-invocation: true\n---\nRun.\n", encoding="utf-8")
            environment = dict(os.environ, ORCHFLOWS_FIRSTMATE_HOME=str(home), PYTHONDONTWRITEBYTECODE="1",
                               CODEX_HOME=str(outside / "codex"), CLAUDE_CONFIG_DIR=str(outside / "claude"))

            def cli(*arguments, expected=0):
                result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/orchflows.py"), *arguments],
                                        cwd=project, env=environment, capture_output=True, text=True, timeout=60)
                self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
                return json.loads(result.stdout or result.stderr)

            installed = cli("setup")
            self.assertEqual(installed["status"], "ready", installed)
            self.assertEqual([entry["name"] for entry in installed["libraries"]], ["quickfix"])
            self.assertFalse((home / ".local").exists())
            self.assertFalse((outside / "codex").exists())
            self.assertFalse((outside / "claude").exists())
            for relative in (".agents/plugins/marketplace.json", ".claude-plugin/marketplace.json"):
                catalog = json.loads((home / relative).read_text(encoding="utf-8"))
                self.assertEqual(catalog["name"], "orchflows-firstmate-home")
                self.assertEqual([entry["name"] for entry in catalog["plugins"]], ["quickfix"])
            self.assertEqual(cli("doctor")["status"], "ready")
            self.assertTrue((home / "libraries/quickfix/skills/fix/SKILL.md").is_file(), "the captain reads it by this path")


if __name__ == "__main__":
    unittest.main()
