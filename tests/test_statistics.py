import math
import unittest
from evaluation.statistics import (calculate_mean, calculate_median,
                                   calculate_standard_deviation,
                                   calculate_summary_statistics, percentage_improvement)


class StatisticsTests(unittest.TestCase):
    def test_summary(self):
        values = [1, 2, 3, 4]
        self.assertEqual(calculate_mean(values), 2.5)
        self.assertEqual(calculate_median(values), 2.5)
        self.assertAlmostEqual(calculate_standard_deviation(values), (5 / 3) ** .5)
        self.assertEqual(calculate_summary_statistics(values)['max'], 4)
        self.assertIsNone(calculate_standard_deviation([1]))

    def test_invalid_and_percent(self):
        for values in ([], [True], [math.nan], [math.inf], ['1']):
            with self.assertRaises(ValueError):
                calculate_summary_statistics(values)
        self.assertEqual(percentage_improvement(10, 8), 20)
        self.assertIsNone(percentage_improvement(0, 0))
