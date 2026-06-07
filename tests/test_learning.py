import unittest
from datetime import date

from learning import generate_weekly_plan, infer_learning_context


class LearningPlanTests(unittest.TestCase):
    def test_plan_is_deterministic_and_balanced(self):
        plan = generate_weekly_plan("B1", "C1", "Vocabulary", date(2026, 6, 7))
        self.assertEqual(len(plan), 5)
        self.assertEqual(len({task["id"] for task in plan}), 5)
        self.assertEqual(plan[0]["domain"], "Vocabulary")
        self.assertGreater(sum(task["minutes"] for task in plan), 60)

    def test_assessment_focus_overrides_default(self):
        context = infer_learning_context(
            {"target_level": "C1"},
            [{"level": "B1"}],
            {"details": {"level": "B2", "focus_domain": "Reading"}},
        )
        self.assertEqual(context["current_level"], "B2")
        self.assertEqual(context["focus_domain"], "Reading")


if __name__ == "__main__":
    unittest.main()
