"""Focused tests for Phase 2 genetic operators and evolution."""

import unittest

from algorithms.genetic_algorithm import (
    GAConfig, initialize_population, order_crossover, run_genetic_algorithm,
    swap_mutation, tournament_selection,
)
from core.tsp import calculate_route_distance, validate_route
from core.utils import create_random_generator


class GeneticAlgorithmTests(unittest.TestCase):
    def setUp(self):
        self.matrix = [[0, 1, 2, 1], [1, 0, 1, 2],
                       [2, 1, 0, 1], [1, 2, 1, 0]]
        self.config = GAConfig(population_size=12, generations=8,
                               tournament_size=3, elitism_count=2)

    def test_population_size_validity_and_independence(self):
        population = initialize_population(10, 4, create_random_generator())
        self.assertEqual(len(population), 10)
        self.assertTrue(all(validate_route(route, 4) and route[0] == 0
                            for route in population))
        self.assertEqual(len({id(route) for route in population}), 10)

    def test_population_reproducibility(self):
        self.assertEqual(initialize_population(10, 4, create_random_generator(7)),
                         initialize_population(10, 4, create_random_generator(7)))

    def test_tournament_minimum_and_no_mutation(self):
        population = [[0, 1, 2], [0, 2, 1], [0, 1, 2]]
        original = [route.copy() for route in population]
        selected = tournament_selection(population, [5, 2, 3], 3,
                                        create_random_generator())
        self.assertIs(selected, population[1])
        self.assertEqual(population, original)

    def test_tournament_tie(self):
        population = [[0, 1, 2], [0, 2, 1]]
        self.assertIs(tournament_selection(population, [2, 2], 2,
                                           create_random_generator()), population[0])

    def test_crossover_validity_and_parent_preservation(self):
        first = [0, 1, 2, 3, 4, 5, 6]
        second = [0, 4, 1, 6, 2, 5, 3]
        child = order_crossover(first, second, create_random_generator())
        self.assertTrue(validate_route(child, 7))
        self.assertEqual(first, [0, 1, 2, 3, 4, 5, 6])
        self.assertEqual(second, [0, 4, 1, 6, 2, 5, 3])
        self.assertIsNot(child, first)

    def test_crossover_identical_and_small(self):
        for parent in ([0, 1], [0, 1, 2], [0, 1, 2, 3]):
            self.assertEqual(order_crossover(parent, parent,
                                             create_random_generator()), parent)
            self.assertIsNot(order_crossover(parent, parent,
                                             create_random_generator()), parent)

    def test_mutation_swaps_only_deliveries(self):
        original = [0, 1, 2, 3]
        mutated = swap_mutation(original, create_random_generator())
        self.assertTrue(validate_route(mutated, 4))
        self.assertNotEqual(mutated, original)
        self.assertEqual(original, [0, 1, 2, 3])

    def test_mutation_one_delivery(self):
        route = [0, 1]
        self.assertEqual(swap_mutation(route, create_random_generator()), route)
        self.assertIsNot(swap_mutation(route, create_random_generator()), route)

    def test_invalid_configuration(self):
        invalid = (
            {"population_size": 1}, {"population_size": True},
            {"generations": 0}, {"mutation_rate": -0.1},
            {"mutation_rate": 1.1}, {"crossover_rate": 1.1},
            {"tournament_size": 1}, {"tournament_size": 101},
            {"elitism_count": 0}, {"elitism_count": 100},
            {"seed": True},
        )
        for arguments in invalid:
            with self.subTest(arguments=arguments), self.assertRaises(ValueError):
                GAConfig(**arguments)

    def test_ga_result_and_reproducibility(self):
        matrix_copy = [row.copy() for row in self.matrix]
        first = run_genetic_algorithm(self.matrix, self.config)
        second = run_genetic_algorithm(self.matrix, self.config)
        self.assertTrue(validate_route(first.best_route, 4))
        self.assertEqual(first.best_distance,
                         calculate_route_distance(first.best_route, self.matrix))
        self.assertEqual(self.matrix, matrix_copy)
        self.assertEqual(first.final_population_size, self.config.population_size)
        self.assertEqual(first.generations_completed, self.config.generations)
        self.assertEqual(len(first.convergence_history), self.config.generations + 1)
        self.assertTrue(all(a >= b for a, b in zip(first.convergence_history,
                                                    first.convergence_history[1:])))
        self.assertEqual(first.best_route, second.best_route)
        self.assertEqual(first.convergence_history, second.convergence_history)
        self.assertEqual(first.initial_best_distance, first.convergence_history[0])
        self.assertGreaterEqual(first.execution_time, 0)

    def test_small_zero_distance_and_different_seed(self):
        matrix = [[0, 0], [0, 0]]
        for seed in (1, 2):
            config = GAConfig(population_size=4, generations=3,
                              tournament_size=2, elitism_count=1, seed=seed)
            result = run_genetic_algorithm(matrix, config)
            self.assertEqual(result.best_route, [0, 1])
            self.assertEqual(result.convergence_history, [0.0] * 4)

    def test_invalid_matrix(self):
        with self.assertRaises(ValueError):
            run_genetic_algorithm([[0, 1], [2, 0]], self.config)


if __name__ == "__main__":
    unittest.main()
