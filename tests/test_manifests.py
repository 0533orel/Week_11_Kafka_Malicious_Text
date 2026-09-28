import unittest
from pathlib import Path
import yaml


class ManifestTests(unittest.TestCase):
    def test_no_embedded_kubernetes_secrets(self):
        for path in Path(".").rglob("*.yaml"):
            if ".venv" in path.parts:
                continue
            for doc in yaml.safe_load_all(path.read_text(encoding="utf-8-sig")):
                if isinstance(doc, dict):
                    self.assertNotEqual(doc.get("kind"), "Secret", str(path))

    def test_secret_templates_have_empty_passwords(self):
        for path in Path("infrastructure").rglob("*.env.example"):
            for line in path.read_text().splitlines():
                if "PASSWORD=" in line:
                    self.assertEqual(line.split("=", 1)[1], "")
