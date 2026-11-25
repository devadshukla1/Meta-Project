import unittest
from algorithms.nearest_neighbor import nearest_neighbor


class NearestNeighborTests(unittest.TestCase):
    def test_ties_and_return(self):
        matrix = [[0, 1, 1], [1, 0, 2], [1, 2, 0]]
        self.assertEqual(nearest_neighbor(matrix), ([0, 1, 2], 4))
        self.assertEqual(matrix[0], [0, 1, 1])
        self.assertEqual(nearest_neighbor(matrix), nearest_neighbor(matrix))

    def test_small_zero_and_invalid(self):
        self.assertEqual(nearest_neighbor([[0, 0], [0, 0]]), ([0, 1], 0))
        with self.assertRaises(ValueError):
            nearest_neighbor([[0, 1], [2, 0]])
