"""Phase 6 regression checks for operator details and dashboard controls."""

import copy
import unittest
from unittest.mock import patch

from algorithms.genetic_algorithm import (GAConfig, evaluate_population,
                                          order_crossover, run_genetic_algorithm,
                                          swap_mutation)
from algorithms.hybrid_ga import HybridGAConfig, run_hybrid_ga
from core.dataset import get_delivery_locations
from core.tsp import (calculate_route_distance, create_distance_matrix,
                      validate_route)
from ui.helpers import route_svg


class FixedPairs:
    def __init__(self, pair):
        self.pair = pair

    def sample(self, population, count):
        return self.pair


class RegressionTests(unittest.TestCase):
    def test_order_crossover_segment_and_fill_order(self):
        first = [0, 1, 2, 3, 4, 5, 6]
        second = [0, 4, 1, 6, 2, 5, 3]
        self.assertEqual(order_crossover(first, second, FixedPairs((1, 2))),
                         [0, 6, 2, 3, 5, 4, 1])
        self.assertEqual(first, [0, 1, 2, 3, 4, 5, 6])
        self.assertEqual(second, [0, 4, 1, 6, 2, 5, 3])

    def test_swap_only_selected_deliveries(self):
        route = [0, 1, 2, 3, 4]
        self.assertEqual(swap_mutation(route, FixedPairs((1, 3))), [0, 3, 2, 1, 4])
        self.assertEqual(route, [0, 1, 2, 3, 4])

    def test_all_generations_contain_valid_independent_routes(self):
        locations = get_delivery_locations()[:6]
        matrix = create_distance_matrix(locations)
        original = copy.deepcopy(matrix)
        real_evaluate = evaluate_population
        observed = []

        def inspect(population, distance_matrix):
            self.assertEqual(len(population), 8)
            self.assertEqual(len({id(route) for route in population}), 8)
            self.assertTrue(all(validate_route(route, 6) for route in population))
            observed.append(copy.deepcopy(population))
            return real_evaluate(population, distance_matrix)

        with patch("algorithms.genetic_algorithm.evaluate_population", side_effect=inspect):
            result = run_genetic_algorithm(matrix, GAConfig(population_size=8,
                generations=4, tournament_size=2, elitism_count=2, mutation_rate=1))
            hybrid = run_hybrid_ga(matrix, HybridGAConfig(population_size=8,
                generations=4, tournament_size=2, elitism_count=2,
                mutation_rate=1, local_search_rate=1))
        self.assertEqual(len(observed), 10)
        self.assertEqual(matrix, original)
        for output in (result, hybrid):
            self.assertEqual(output.best_distance,
                             calculate_route_distance(output.best_route, matrix))
            self.assertEqual(output.best_distance, output.convergence_history[-1])

    def test_dataset_and_svg_integrity(self):
        locations = get_delivery_locations()
        self.assertEqual(len(locations), 20)
        self.assertEqual(len({place["name"] for place in locations}), 20)
        self.assertEqual(len({place["id"] for place in locations}), 20)
        route = list(range(20))
        drawing = route_svg(locations, route)
        self.assertEqual(drawing.count("<circle "), 20)
        self.assertEqual(drawing.count("<line "), 20)

    def test_hybrid_reproducible_and_disabled_equivalent(self):
        matrix = create_distance_matrix(get_delivery_locations()[:5])
        for seed in (42, 43, 44, 45, 46):
            settings = dict(population_size=8, generations=4,
                            tournament_size=2, elitism_count=1, seed=seed)
            standard = run_genetic_algorithm(matrix, GAConfig(**settings))
            disabled = run_hybrid_ga(matrix, HybridGAConfig(**settings,
                                                              local_search_rate=0))
            first = run_hybrid_ga(matrix, HybridGAConfig(**settings))
            second = run_hybrid_ga(matrix, HybridGAConfig(**settings))
            self.assertEqual(standard.best_route, disabled.best_route)
            self.assertEqual(standard.convergence_history, disabled.convergence_history)
            self.assertEqual(first.best_route, second.best_route)
            self.assertEqual(first.convergence_history, second.convergence_history)
            self.assertEqual(first.local_search_applications,
                             second.local_search_applications)


if __name__ == "__main__":
    unittest.main()
