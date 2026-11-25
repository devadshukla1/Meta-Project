"""Phase 1 TSP foundation tests."""

import unittest

from core.dataset import get_delivery_locations
from core.tsp import (calculate_euclidean_distance, calculate_route_distance,
                      create_distance_matrix, validate_route)
from core.utils import create_random_generator, generate_random_route


class TspTests(unittest.TestCase):
    def setUp(self):
        self.square = [
            {"id": 0, "x": 0, "y": 0}, {"id": 1, "x": 1, "y": 0},
            {"id": 2, "x": 1, "y": 1}, {"id": 3, "x": 0, "y": 1},
        ]
        self.matrix = create_distance_matrix(self.square)

    def test_identical_coordinates(self):
        self.assertEqual(calculate_euclidean_distance(self.square[0], self.square[0]), 0)

    def test_three_four_five(self):
        self.assertEqual(calculate_euclidean_distance({"x": 0, "y": 0}, {"x": 3, "y": 4}), 5)

    def test_distance_symmetry(self):
        self.assertEqual(calculate_euclidean_distance(self.square[0], self.square[2]),
                         calculate_euclidean_distance(self.square[2], self.square[0]))

    def test_malformed_coordinate(self):
        with self.assertRaises(ValueError):
            calculate_euclidean_distance({"x": 1}, self.square[0])

    def test_matrix_dimensions(self):
        self.assertEqual([len(row) for row in self.matrix], [4] * 4)

    def test_matrix_diagonal(self):
        self.assertTrue(all(self.matrix[i][i] == 0 for i in range(4)))

    def test_matrix_symmetry(self):
        self.assertTrue(all(self.matrix[i][j] == self.matrix[j][i]
                            for i in range(4) for j in range(4)))

    def test_matrix_nonnegative(self):
        self.assertTrue(all(value >= 0 for row in self.matrix for value in row))

    def test_invalid_dataset(self):
        with self.assertRaises(ValueError):
            create_distance_matrix([self.square[1], self.square[0]])

    def test_dataset_copy_and_count(self):
        locations = get_delivery_locations()
        self.assertEqual(len(locations), 20)
        locations[0]["name"] = "Changed"
        self.assertEqual(get_delivery_locations()[0]["name"], "Central Warehouse")

    def test_valid_route(self):
        self.assertTrue(validate_route([0, 1, 2, 3], 4))

    def test_missing_location(self):
        self.assertFalse(validate_route([0, 1, 2], 4))

    def test_duplicate_location(self):
        self.assertFalse(validate_route([0, 1, 1, 3], 4))

    def test_wrong_start(self):
        self.assertFalse(validate_route([1, 0, 2, 3], 4))

    def test_out_of_range(self):
        self.assertFalse(validate_route([0, 1, 2, 4], 4))

    def test_empty_route(self):
        self.assertFalse(validate_route([], 4))

    def test_noninteger_id(self):
        self.assertFalse(validate_route([0, 1, 2, "3"], 4))

    def test_boolean_id(self):
        self.assertFalse(validate_route([0, True, 2, 3], 4))

    def test_invalid_route_type(self):
        self.assertFalse(validate_route((0, 1, 2, 3), 4))

    def test_square_route_distance(self):
        self.assertEqual(calculate_route_distance([0, 1, 2, 3], self.matrix), 4.0)

    def test_automatic_return(self):
        self.assertEqual(calculate_route_distance([0, 1], [[0, 3], [3, 0]]), 6.0)

    def test_invalid_route_rejected(self):
        with self.assertRaises(ValueError):
            calculate_route_distance([0, 1, 1, 3], self.matrix)

    def test_invalid_matrix_rejected(self):
        with self.assertRaises(ValueError):
            calculate_route_distance([0, 1], [[0, 3], [2, 0]])

    def test_random_reproducibility(self):
        self.assertEqual(generate_random_route(20, create_random_generator(42)),
                         generate_random_route(20, create_random_generator(42)))

    def test_random_route_valid(self):
        self.assertTrue(validate_route(generate_random_route(20, create_random_generator()), 20))

    def test_random_warehouse_first(self):
        self.assertEqual(generate_random_route(20, create_random_generator())[0], 0)

    def test_random_no_repeats(self):
        self.assertEqual(len(set(generate_random_route(20, create_random_generator()))), 20)

    def test_random_invalid_count(self):
        with self.assertRaises(ValueError):
            generate_random_route(1, create_random_generator())


if __name__ == "__main__":
    unittest.main()
