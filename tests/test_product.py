import unittest

import numpy as np

from product import analyze_text, build_report


class FixedModel:
    def __init__(self, score):
        self.score = score

    def predict(self, texts):
        return np.asarray([self.score] * len(texts))


class ProductTests(unittest.TestCase):
    def test_analysis_contains_actionable_profile(self):
        text = (
            "Although learning English takes time, regular practice helps me "
            "communicate clearly and explain complex ideas with confidence."
        )
        result = analyze_text(
            FixedModel(2.2),
            ["A1", "A2", "B1", "B2", "C1", "C2"],
            text,
        )

        self.assertEqual(result["level"], "B1")
        self.assertEqual(result["likely_range"], "B1-B2")
        self.assertTrue(result["focus"])
        self.assertIn("word_count", result["metrics"])

    def test_report_is_valid_json_payload(self):
        result = analyze_text(
            FixedModel(1.0),
            ["A1", "A2", "B1", "B2", "C1", "C2"],
            "I write a short paragraph about my daily routine and my work.",
        )
        report = build_report(result, {"independent_test_accuracy": 0.78})
        self.assertIn('"product": "Pro English AI"', report)


if __name__ == "__main__":
    unittest.main()
