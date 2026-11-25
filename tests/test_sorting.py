"""Focused unit tests for manual Merge Sort."""

import unittest

from core.sorting import merge_sort


class SortingTests(unittest.TestCase):
    def test_empty_and_single(self):
        self.assertEqual(merge_sort([]), [])
        self.assertEqual(merge_sort([42]), [42])

    def test_already_sorted_and_reversed(self):
        sorted_list = [1, 2, 3, 4, 5, 6, 7]
        self.assertEqual(merge_sort(sorted_list), sorted_list)
        reverse_list = [7, 6, 5, 4, 3, 2, 1]
        self.assertEqual(merge_sort(reverse_list), sorted_list)

    def test_duplicates_and_negatives(self):
        data = [5, -2, 3, 5, -2, 0, 10, -8]
        expected = [-8, -2, -2, 0, 3, 5, 5, 10]
        self.assertEqual(merge_sort(data), expected)

    def test_stability(self):
        """Stable sort preserves input order of elements with equal keys."""
        # List of items where key is only first element
        pairs = [(2, "first_2"), (1, "1"), (2, "second_2"), (0, "0"), (2, "third_2")]
        sorted_pairs = merge_sort(pairs, key=lambda item: item[0])
        self.assertEqual(
            sorted_pairs,
            [(0, "0"), (1, "1"), (2, "first_2"), (2, "second_2"), (2, "third_2")],
        )

    def test_does_not_mutate_input(self):
        original = [5, 2, 8, 1]
        copy = list(original)
        sorted_res = merge_sort(original)
        self.assertEqual(original, copy)
        self.assertEqual(sorted_res, [1, 2, 5, 8])


if __name__ == "__main__":
    unittest.main()
