import importlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import app as app_module


class PersistenceTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.data_file = Path(self.temp_dir.name) / "activities.json"
        os.environ["ACTIVITIES_DATA_FILE"] = str(self.data_file)

    def reload_app_module(self):
        return importlib.reload(app_module)

    def test_create_default_file_when_missing(self):
        self.data_file.unlink(missing_ok=True)

        module = self.reload_app_module()

        self.assertTrue(self.data_file.exists())
        saved_data = json.loads(self.data_file.read_text())
        self.assertIn("Chess Club", saved_data)
        self.assertIn("Programming Class", saved_data)
        self.assertEqual(module.activities["Chess Club"]["participants"][0], "michael@mergington.edu")

    def test_signup_persists_to_disk(self):
        module = self.reload_app_module()
        client = TestClient(module.app)

        response = client.post("/activities/Chess Club/signup?email=student@example.com")

        self.assertEqual(response.status_code, 200)
        saved_data = json.loads(self.data_file.read_text())
        self.assertIn("student@example.com", saved_data["Chess Club"]["participants"])

        reloaded_module = self.reload_app_module()
        self.assertIn("student@example.com", reloaded_module.activities["Chess Club"]["participants"])


if __name__ == "__main__":
    unittest.main()
