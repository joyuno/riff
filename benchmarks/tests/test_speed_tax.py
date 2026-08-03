import unittest

from benchmarks.scoring.speed_tax import ValidationError, calculate_report


class SpeedTaxReportTests(unittest.TestCase):
    def test_calculates_odd_medians_and_passes_under_budget(self):
        report = calculate_report([100, 110, 105], [110, 120, 115])

        self.assertEqual(report["baseline_median_ms"], 105)
        self.assertEqual(report["riff_median_ms"], 115)
        self.assertEqual(report["overhead_percent"], 9.5238)
        self.assertTrue(report["passed"])

    def test_calculates_even_medians(self):
        report = calculate_report([100, 120], [110, 130])

        self.assertEqual(report["baseline_median_ms"], 110)
        self.assertEqual(report["riff_median_ms"], 120)

    def test_passes_at_exactly_fifteen_percent(self):
        report = calculate_report([100, 100, 100], [115, 115, 115])

        self.assertEqual(report["overhead_percent"], 15.0)
        self.assertTrue(report["passed"])

    def test_fails_above_fifteen_percent(self):
        report = calculate_report([100, 100, 100], [116, 116, 116])

        self.assertFalse(report["passed"])

    def test_rejects_zero_or_negative_timings(self):
        for baseline, riff in (([0], [1]), ([-1], [1]), ([1], [0])):
            with self.subTest(baseline=baseline, riff=riff):
                with self.assertRaises(ValidationError):
                    calculate_report(baseline, riff)

    def test_rejects_empty_or_mismatched_samples(self):
        for baseline, riff in (([], []), ([1], [1, 2])):
            with self.subTest(baseline=baseline, riff=riff):
                with self.assertRaises(ValidationError):
                    calculate_report(baseline, riff)

    def test_rejects_negative_budget(self):
        with self.assertRaises(ValidationError):
            calculate_report([100], [100], budget_percent=-1)


if __name__ == "__main__":
    unittest.main()
