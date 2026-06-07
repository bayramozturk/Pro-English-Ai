from types import SimpleNamespace
import unittest

from writing_coach import analyze_writing, apply_corrections


class FakeChecker:
    def check(self, text):
        return [
            SimpleNamespace(
                offset=0,
                error_length=1,
                replacements=["I"],
                category="TYPOS",
                message="The pronoun I should be uppercase.",
                rule_id="I_LOWERCASE",
            ),
            SimpleNamespace(
                offset=2,
                error_length=3,
                replacements=["have"],
                category="GRAMMAR",
                message="Use have with I.",
                rule_id="BASE_FORM",
            ),
        ]


class WritingCoachTests(unittest.TestCase):
    def test_reports_exact_location_and_rebuilds_sentence(self):
        result = analyze_writing("i has a plan.", checker=FakeChecker())

        self.assertEqual(result["corrected_text"], "I have a plan.")
        self.assertEqual(result["issues"][0]["line"], 1)
        self.assertEqual(result["issues"][0]["column"], 1)
        self.assertEqual(result["issues"][1]["original"], "has")
        self.assertEqual(result["issues"][1]["replacement"], "have")
        self.assertEqual(
            result["sentence_comparisons"],
            [{"before": "i has a plan.", "after": "I have a plan."}],
        )

    def test_applies_corrections_from_right_to_left(self):
        issues = [
            {"offset": 0, "length": 1, "replacement": "I"},
            {"offset": 2, "length": 3, "replacement": "have"},
        ]
        self.assertEqual(apply_corrections("i has ideas", issues), "I have ideas")

    def test_fallback_engine_handles_common_errors(self):
        result = analyze_writing("i dont think we is ready .", checker=None)

        self.assertEqual(result["engine"], "Pro English AI hızlı yazım motoru")
        self.assertEqual(result["corrected_text"], "I don't think we are ready.")
        self.assertGreaterEqual(len(result["issues"]), 4)

    def test_multiline_location(self):
        checker = FakeChecker()
        checker.check = lambda text: [
            SimpleNamespace(
                offset=6,
                error_length=1,
                replacements=["I"],
                category="TYPOS",
                message="Uppercase I.",
                rule_id="I_LOWERCASE",
            )
        ]
        result = analyze_writing("Hello\ni work.", checker=checker)
        self.assertEqual(result["issues"][0]["line"], 2)
        self.assertEqual(result["issues"][0]["column"], 1)


if __name__ == "__main__":
    unittest.main()
