import tempfile
import unittest
from pathlib import Path

import storage


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_path = storage.DATABASE_PATH
        storage.DATABASE_PATH = Path(self.temp_dir.name) / "pro-english-ai-test.db"
        storage.initialize_database()

    def tearDown(self):
        storage.DATABASE_PATH = self.original_path
        self.temp_dir.cleanup()

    def test_profile_history_and_dashboard_lifecycle(self):
        profile = storage.update_profile("Test User", "C1", 5, True)
        self.assertEqual(profile["target_level"], "C1")

        result = {
            "created_at": "2026-06-07T18:00:00+00:00",
            "level": "B2",
            "level_index": 3,
            "reliability": 82,
            "quality_score": 75,
            "metrics": {"word_count": 70},
            "text": "A test writing sample.",
        }
        storage.save_analysis(result)
        storage.save_assessment(
            "B2",
            8,
            10,
            details={"level": "B2", "focus_domain": "Vocabulary"},
        )
        storage.set_task_completed("2026-W23-B2-C1-1")

        self.assertEqual(len(storage.list_analyses()), 1)
        self.assertEqual(
            storage.get_latest_assessment()["details"]["focus_domain"],
            "Vocabulary",
        )
        self.assertIn(
            "2026-W23-B2-C1-1",
            storage.list_completed_tasks(),
        )
        stats = storage.get_dashboard_stats()
        self.assertEqual(stats["analysis_total"], 1)
        self.assertEqual(stats["average_assessment_score"], 80)

        storage.clear_profile_data()
        self.assertEqual(storage.get_dashboard_stats()["analysis_total"], 0)
        self.assertEqual(storage.list_completed_tasks(), set())


if __name__ == "__main__":
    unittest.main()
