import pickle
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DeploymentTests(unittest.TestCase):
    def test_model_bundle_loads_and_predicts(self):
        with (ROOT / "model.pkl").open("rb") as model_file:
            bundle = pickle.load(model_file)

        prediction = bundle["pipeline"].predict(
            ["Although the task was difficult, I completed it successfully."]
        )
        self.assertEqual(len(prediction), 1)
        self.assertEqual(bundle["levels"], ["A1", "A2", "B1", "B2", "C1", "C2"])

    def test_required_deployment_files_exist(self):
        required = [
            "app.py",
            "model.pkl",
            "requirements.txt",
            "Dockerfile",
            "render.yaml",
        ]
        for relative_path in required:
            self.assertTrue((ROOT / relative_path).is_file(), relative_path)

    def test_optional_landing_page_contains_no_direct_ai_api_call(self):
        landing_page = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("api.anthropic.com", landing_page)
        self.assertNotIn("api.openai.com", landing_page)


if __name__ == "__main__":
    unittest.main()
