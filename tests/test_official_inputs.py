from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from data.official_inputs import load_official_inputs, validate_official_manifest


class OfficialInputTests(unittest.TestCase):
    def test_generated_instance_and_catalogs_match_manifest(self):
        manifest = validate_official_manifest()
        self.assertEqual(manifest["grupo"], "G01")
        self.assertEqual(manifest["seed_base"], 31)
        self.assertEqual(manifest["seed_final"], 1031)
        self.assertEqual(manifest["id_instancia"], "ec52f3b45b22")
        self.assertEqual(manifest["quantidade_skus"], {"q1": 30, "q2": 24})
        self.assertIn("meta_caixa_90d", manifest["metas_financeiras"]["q1"])
        self.assertIn("dividas", manifest["metas_financeiras"]["q2"])
        self.assertEqual(len(load_official_inputs("q1")[0]), 30)
        self.assertEqual(len(load_official_inputs("q2")[0]), 24)

    def test_loader_rejects_modified_official_input(self):
        source = Path(__file__).resolve().parents[1] / "data"
        with tempfile.TemporaryDirectory() as temporary:
            copied = Path(temporary) / "data"
            shutil.copytree(source, copied)
            target = copied / "q1_catalogo_G01.csv"
            target.write_bytes(target.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                validate_official_manifest(copied)


if __name__ == "__main__":
    unittest.main()
