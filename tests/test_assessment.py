import unittest

from assessment import QUESTION_BANK, build_assessment, score_assessment


class AssessmentTests(unittest.TestCase):
    def test_question_bank_is_balanced(self):
        self.assertEqual(len(QUESTION_BANK), 36)
        for level in ["A1", "A2", "B1", "B2", "C1", "C2"]:
            level_questions = [q for q in QUESTION_BANK if q["level"] == level]
            self.assertEqual(len(level_questions), 6)
            self.assertEqual(
                {q["domain"] for q in level_questions},
                {"Grammar", "Vocabulary", "Reading"},
            )

    def test_placement_uses_all_levels(self):
        questions = build_assessment("placement")
        self.assertEqual(len(questions), 36)

    def test_level_check_uses_three_nearby_levels(self):
        questions = build_assessment("level_check", "B2")
        self.assertEqual(len(questions), 18)
        self.assertEqual({q["level"] for q in questions}, {"B1", "B2", "C1"})

    def test_all_correct_reaches_c2(self):
        questions = build_assessment("placement")
        answers = [question["answer"] for question in questions]
        result = score_assessment(questions, answers)
        self.assertEqual(result["level"], "C2")
        self.assertEqual(result["score_percent"], 100)

    def test_all_wrong_stays_at_a1(self):
        questions = build_assessment("placement")
        answers = [
            next(option for option in question["options"] if option != question["answer"])
            for question in questions
        ]
        result = score_assessment(questions, answers)
        self.assertEqual(result["level"], "A1")
        self.assertEqual(result["score_percent"], 0)

    def test_mastery_through_b2_does_not_over_promote_to_c1(self):
        questions = build_assessment("placement")
        answers = [
            question["answer"]
            if question["level"] in {"A1", "A2", "B1", "B2"}
            else next(
                option
                for option in question["options"]
                if option != question["answer"]
            )
            for question in questions
        ]
        result = score_assessment(questions, answers)
        self.assertEqual(result["level"], "B2")


if __name__ == "__main__":
    unittest.main()
