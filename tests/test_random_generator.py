"""Focused unit tests for the manual Linear Congruential Generator (LCG)."""

import unittest

from core.random_generator import CustomRandom


class RandomGeneratorTests(unittest.TestCase):
    def test_reproducibility(self):
        """Identical seeds must produce identical sequences."""
        rng1 = CustomRandom(12345)
        rng2 = CustomRandom(12345)
        seq1 = [rng1.next_integer() for _ in range(50)]
        seq2 = [rng2.next_integer() for _ in range(50)]
        self.assertEqual(seq1, seq2)

    def test_independent_instances(self):
        """Independent generators must maintain independent states."""
        rng1 = CustomRandom(42)
        rng2 = CustomRandom(42)
        _ = [rng1.next_integer() for _ in range(10)]
        self.assertNotEqual(rng1.state, rng2.state)
        self.assertEqual(rng2.next_integer(), CustomRandom(42).next_integer())

    def test_random_interval(self):
        """Random decimals must be in half-open interval [0.0, 1.0)."""
        rng = CustomRandom(999)
        for _ in range(1000):
            val = rng.random()
            self.assertGreaterEqual(val, 0.0)
            self.assertLess(val, 1.0)

    def test_randint_bounds(self):
        """Generated integers must lie within requested inclusive bounds."""
        rng = CustomRandom(777)
        for _ in range(500):
            val = rng.randint(5, 15)
            self.assertGreaterEqual(val, 5)
            self.assertLessEqual(val, 15)

    def test_randint_single_value(self):
        """Generating randint where minimum == maximum returns that value."""
        rng = CustomRandom(42)
        for _ in range(20):
            self.assertEqual(rng.randint(10, 10), 10)

    def test_invalid_bounds(self):
        """minimum > maximum or non-integer bounds must be rejected."""
        rng = CustomRandom(42)
        with self.assertRaises(ValueError):
            rng.randint(10, 5)
        with self.assertRaises(ValueError):
            rng.randint(True, 5)  # bool rejected
        with self.assertRaises(ValueError):
            rng.randint(1.5, 5)

    def test_invalid_seeds(self):
        """Booleans and non-integers must be rejected as seeds."""
        with self.assertRaises(ValueError):
            CustomRandom(True)
        with self.assertRaises(ValueError):
            CustomRandom("42")
        with self.assertRaises(ValueError):
            CustomRandom(3.14)

    def test_shuffle_preserves_elements(self):
        """Shuffle must preserve all elements and multiset equality."""
        rng = CustomRandom(42)
        original = list(range(20))
        shuffled = list(original)
        rng.shuffle(shuffled)
        self.assertEqual(sorted(shuffled), original)
        self.assertNotEqual(shuffled, original)  # Highly likely permutation change

    def test_sample_no_duplicates(self):
        """Sampling without replacement must not produce duplicates."""
        rng = CustomRandom(42)
        items = list(range(50))
        sampled = rng.sample(items, 15)
        self.assertEqual(len(sampled), 15)
        self.assertEqual(len(set(sampled)), 15)
        for x in sampled:
            self.assertIn(x, items)

    def test_sample_invalid_counts(self):
        """Sampling more items than pool or negative count must raise ValueError."""
        rng = CustomRandom(42)
        with self.assertRaises(ValueError):
            rng.sample([1, 2, 3], 5)
        with self.assertRaises(ValueError):
            rng.sample([1, 2, 3], -1)
        with self.assertRaises(ValueError):
            rng.sample([1, 2, 3], True)


if __name__ == "__main__":
    unittest.main()
