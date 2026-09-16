"""Native plugin entrypoints describe the same core package, and every core skill declares its invocation policy for both hosts."""

import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
AUTOMATIC = {"orch-dynamic-workflow"}
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)


class PluginPackageTests(unittest.TestCase):
    def test_host_manifests_match_package_identity_and_reachable_skills(self):
        identity = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(identity["name"], "orchflows-firstmate")
        for host in (".claude-plugin", ".codex-plugin"):
            with self.subTest(host=host):
                manifest = json.loads((ROOT / host / "plugin.json").read_text(encoding="utf-8"))
                self.assertEqual(manifest["name"], identity["name"])
                self.assertEqual(manifest["version"], identity["version"])
                skills = (ROOT / manifest["skills"]).resolve()
                self.assertTrue(skills.is_relative_to(ROOT))
                self.assertTrue(list(skills.glob("*/SKILL.md")))
        self.assertFalse((ROOT / ".kimi-plugin").exists(), "only the primary's harness loads the core")
        self.assertFalse((ROOT / "marketplace.json").exists())

    def test_checkout_catalogs_register_this_package_only(self):
        identity = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
        for relative in (".claude-plugin/marketplace.json", ".agents/plugins/marketplace.json"):
            with self.subTest(catalog=relative):
                catalog = json.loads((ROOT / relative).read_text(encoding="utf-8"))
                self.assertEqual(catalog["name"], "orchflows-firstmate-local")
                self.assertEqual([entry["name"] for entry in catalog["plugins"]], [identity["name"]])
                source = catalog["plugins"][0]["source"]
                self.assertEqual(source["path"] if isinstance(source, dict) else source, "./")

    def test_every_skill_declares_the_same_invocation_policy_for_both_hosts(self):
        for skill in sorted((ROOT / "skills").glob("*/SKILL.md")):
            with self.subTest(skill=skill.parent.name):
                front = FRONTMATTER.match(skill.read_text(encoding="utf-8"))
                self.assertIsNotNone(front, "frontmatter")
                fields = dict(line.split(": ", 1) for line in front.group(1).splitlines() if ": " in line)
                self.assertEqual(fields["name"], skill.parent.name)
                automatic = skill.parent.name in AUTOMATIC
                self.assertEqual(fields.get("disable-model-invocation"), "false" if automatic else "true")
                codex = (skill.parent / "agents/openai.yaml").read_text(encoding="utf-8")
                policy = re.search(r"^\s*allow_implicit_invocation:\s*(true|false)\s*$", codex, re.M)
                self.assertIsNotNone(policy, "Codex policy")
                self.assertEqual(policy.group(1), "true" if automatic else "false")
                for key in ("display_name", "short_description"):
                    self.assertRegex(codex, re.compile(rf"^\s*{key}:\s*\S", re.M), key)


if __name__ == "__main__":
    unittest.main()
