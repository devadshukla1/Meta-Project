import unittest
from algorithms.two_opt import two_opt
from core.tsp import calculate_route_distance


class TwoOptTests(unittest.TestCase):
    def test_crossing(self):
        matrix = [[0, 1, 2**0.5, 1], [1, 0, 1, 2**0.5],
                  [2**0.5, 1, 0, 1], [1, 2**0.5, 1, 0]]
        route = [0, 2, 1, 3]
        improved, distance = two_opt(route, matrix)
        self.assertEqual(route, [0, 2, 1, 3])
        self.assertEqual(distance, 4)
        self.assertEqual(sorted(improved), list(range(4)))
        self.assertEqual(improved[0], 0)
        self.assertEqual(distance, calculate_route_distance(improved, matrix))
        self.assertEqual(two_opt(improved, matrix), (improved, distance))
        self.assertEqual(two_opt(route, matrix), (improved, distance))

    def test_small_and_invalid(self):
        self.assertEqual(two_opt([0, 1], [[0, 0], [0, 0]]), ([0, 1], 0))
        for passes in (0, True, 1.5):
            with self.assertRaises(ValueError):
                two_opt([0, 1], [[0, 1], [1, 0]], passes)
        for route, matrix in (([1, 0], [[0, 1], [1, 0]]),
                              ([0, 1], [[0, 1], [2, 0]])):
            with self.assertRaises(ValueError):
                two_opt(route, matrix)
