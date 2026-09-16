"""Native plugin entrypoints describe the same package, and every skill declares its invocation policy for both hosts."""

import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
AUTOMATIC = {"orch-dynamic-workflow"}
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)


def packages() -> list[Path]:
    return [ROOT, *sorted(path for path in (ROOT / "example-workflows").iterdir() if path.is_dir())]


class PluginPackageTests(unittest.TestCase):
    def test_host_manifests_match_package_identity_and_reachable_skills(self):
        for package in packages():
            identity = json.loads((package / "plugin.json").read_text(encoding="utf-8"))
            hosts = [host for host in (".claude-plugin", ".codex-plugin", ".kimi-plugin") if (package / host).is_dir()]
            self.assertIn(".claude-plugin", hosts, package.name)
            self.assertIn(".codex-plugin", hosts, package.name)
            for host in hosts:
                with self.subTest(package=package.name, host=host):
                    manifest = json.loads((package / host / "plugin.json").read_text(encoding="utf-8"))
                    self.assertEqual(manifest["name"], identity["name"])
                    self.assertEqual(manifest["version"], identity["version"])
                    skills = (package / manifest["skills"]).resolve()
                    self.assertTrue(skills.is_relative_to(package))
                    self.assertTrue(list(skills.glob("*/SKILL.md")))

    def test_core_manifests_and_checkout_catalogs_name_this_package_only(self):
        identity = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(identity["name"], "orchflows-firstmate")
        self.assertFalse((ROOT / ".kimi-plugin").exists(), "only the primary's harness loads the core")
        self.assertFalse((ROOT / "marketplace.json").exists())
        for relative in (".claude-plugin/marketplace.json", ".agents/plugins/marketplace.json"):
            with self.subTest(catalog=relative):
                catalog = json.loads((ROOT / relative).read_text(encoding="utf-8"))
                self.assertEqual(catalog["name"], "orchflows-firstmate-local")
                self.assertEqual([entry["name"] for entry in catalog["plugins"]], [identity["name"]])

    def test_every_skill_declares_the_same_invocation_policy_for_both_hosts(self):
        for package in packages():
            for skill in sorted((package / "skills").glob("*/SKILL.md")):
                with self.subTest(package=package.name, skill=skill.parent.name):
                    front = FRONTMATTER.match(skill.read_text(encoding="utf-8"))
                    self.assertIsNotNone(front, "frontmatter")
                    fields = dict(line.split(": ", 1) for line in front.group(1).splitlines() if ": " in line)
                    self.assertEqual(fields["name"], skill.parent.name)
                    automatic = package == ROOT and skill.parent.name in AUTOMATIC
                    self.assertEqual(fields.get("disable-model-invocation"), "false" if automatic else "true")
                    codex = (skill.parent / "agents/openai.yaml").read_text(encoding="utf-8")
                    policy = re.search(r"^\s*allow_implicit_invocation:\s*(true|false)\s*$", codex, re.M)
                    self.assertIsNotNone(policy, "Codex policy")
                    self.assertEqual(policy.group(1), "true" if automatic else "false")
                    for key in ("display_name", "short_description"):
                        self.assertRegex(codex, re.compile(rf"^\s*{key}:\s*\S", re.M), key)


if __name__ == "__main__":
    unittest.main()
