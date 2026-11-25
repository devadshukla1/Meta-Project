"""Focused unit tests for manual mathematics utilities."""

import math
import unittest

from core.mathematics import (is_finite_number, manual_abs, manual_max,
                              manual_min, manual_sqrt, manual_sum)


class MathematicsTests(unittest.TestCase):
    def test_manual_sqrt_perfect_squares(self):
        self.assertAlmostEqual(manual_sqrt(0), 0.0)
        self.assertAlmostEqual(manual_sqrt(1), 1.0)
        self.assertAlmostEqual(manual_sqrt(4), 2.0)
        self.assertAlmostEqual(manual_sqrt(9), 3.0)
        self.assertAlmostEqual(manual_sqrt(25), 5.0)
        self.assertAlmostEqual(manual_sqrt(10000), 100.0)

    def test_manual_sqrt_non_perfect_squares(self):
        for num in (2, 3, 5, 7, 10, 50, 123.456):
            expected = math.sqrt(num)
            actual = manual_sqrt(num)
            self.assertAlmostEqual(actual, expected, places=9)

    def test_manual_sqrt_small_and_large(self):
        # Small numbers
        self.assertAlmostEqual(manual_sqrt(1e-6), 1e-3, places=7)
        # Large numbers
        self.assertAlmostEqual(manual_sqrt(1e8), 1e4, places=4)

    def test_manual_sqrt_negative_and_invalid(self):
        with self.assertRaises(ValueError):
            manual_sqrt(-1)
        with self.assertRaises(ValueError):
            manual_sqrt(float("nan"))
        with self.assertRaises(ValueError):
            manual_sqrt(float("inf"))
        with self.assertRaises(ValueError):
            manual_sqrt("16")

    def test_is_finite_number(self):
        self.assertTrue(is_finite_number(0))
        self.assertTrue(is_finite_number(42))
        self.assertTrue(is_finite_number(-3.14))
        self.assertTrue(is_finite_number(1e20))

        # Rejections
        self.assertFalse(is_finite_number(True))
        self.assertFalse(is_finite_number(False))
        self.assertFalse(is_finite_number(float("nan")))
        self.assertFalse(is_finite_number(float("inf")))
        self.assertFalse(is_finite_number(float("-inf")))
        self.assertFalse(is_finite_number("123"))
        self.assertFalse(is_finite_number(None))

    def test_manual_abs(self):
        self.assertEqual(manual_abs(5), 5)
        self.assertEqual(manual_abs(-5), 5)
        self.assertEqual(manual_abs(0), 0)
        self.assertEqual(manual_abs(-3.5), 3.5)
        with self.assertRaises(ValueError):
            manual_abs(float("inf"))

    def test_manual_sum(self):
        self.assertEqual(manual_sum([]), 0)
        self.assertEqual(manual_sum([1, 2, 3, 4, 5]), 15)
        self.assertEqual(manual_sum([1.5, 2.5, 3.0]), 7.0)
        self.assertEqual(manual_sum([10, -5, 3]), 8)

    def test_manual_min_max(self):
        items = [10, 4, 7, 2, 9, 25, -3]
        self.assertEqual(manual_min(items), -3)
        self.assertEqual(manual_max(items), 25)

        # Custom key
        tuples = [(1, "b"), (3, "a"), (2, "c")]
        self.assertEqual(manual_min(tuples, key=lambda x: x[0]), (1, "b"))
        self.assertEqual(manual_max(tuples, key=lambda x: x[0]), (3, "a"))

        # Empty sequence raises ValueError
        with self.assertRaises(ValueError):
            manual_min([])
        with self.assertRaises(ValueError):
            manual_max([])


if __name__ == "__main__":
    unittest.main()
