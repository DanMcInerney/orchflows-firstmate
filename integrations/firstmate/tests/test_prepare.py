"""Distribution integrity checks before any checkout or live runtime is touched."""

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


SPEC = importlib.util.spec_from_file_location("prepare", Path(__file__).parents[1] / "prepare.py")
prepare = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(prepare)


class DistributionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.manifest = {"schema": 1, "firstmate_commit": prepare.BASE,
                         "patches": ["patches/base.patch"], "files": []}
        for name, body in [("patches/base.patch", b"patch"), ("overlay/bin/owner.py", b"owner")]:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(body)
            self.manifest["files"].append({"path": name, "sha256": hashlib.sha256(body).hexdigest()})
        self.save()

    def save(self):
        (self.root / "manifest.json").write_text(json.dumps(self.manifest), encoding="utf-8")

    def test_exact_inventory(self):
        _, files = prepare.distribution(self.root)
        self.assertEqual(files, [self.root / "overlay/bin/owner.py"])

    def test_unlisted_deployable_file_refuses(self):
        (self.root / "overlay/bin/extra.py").write_bytes(b"unexpected")
        with self.assertRaisesRegex(ValueError, "inventory"):
            prepare.distribution(self.root)

    def test_changed_bytes_refuse(self):
        (self.root / "overlay/bin/owner.py").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "differs from its manifest"):
            prepare.distribution(self.root)

    def test_unverified_patch_sequence_refuses(self):
        self.manifest["patches"] = ["../outside.patch"]
        self.save()
        with self.assertRaisesRegex(ValueError, "patch sequence"):
            prepare.distribution(self.root)

    def test_traversal_and_duplicate_inventory_refuse(self):
        self.manifest["files"].append(self.manifest["files"][0])
        self.save()
        with self.assertRaisesRegex(ValueError, "duplicate"):
            prepare.distribution(self.root)
        self.manifest["files"][-1] = {"path": "overlay/../outside", "sha256": ""}
        self.save()
        with self.assertRaisesRegex(ValueError, "Invalid"):
            prepare.distribution(self.root)


if __name__ == "__main__":
    unittest.main()
