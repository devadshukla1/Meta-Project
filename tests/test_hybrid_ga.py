import unittest
from algorithms.genetic_algorithm import GAConfig, run_genetic_algorithm
from algorithms.hybrid_ga import HybridGAConfig, run_hybrid_ga


class HybridTests(unittest.TestCase):
    def test_equivalence(self):
        matrix = [[0, 2, 3], [2, 0, 1], [3, 1, 0]]
        standard = run_genetic_algorithm(matrix, GAConfig(generations=3))
        hybrid = run_hybrid_ga(matrix, HybridGAConfig(generations=3, local_search_rate=0))
        self.assertEqual(standard.best_route, hybrid.best_route)
        self.assertEqual(standard.convergence_history, hybrid.convergence_history)
        self.assertEqual(hybrid.local_search_applications, 0)

    def test_counters_and_reproducibility(self):
        matrix = [[0, 0], [0, 0]]
        config = HybridGAConfig(generations=3, local_search_rate=1)
        first = run_hybrid_ga(matrix, config)
        second = run_hybrid_ga(matrix, config)
        self.assertEqual(first.local_search_applications, 294)
        self.assertEqual(first.local_search_improvements, 0)
        self.assertEqual(first.best_route, [0, 1])
        self.assertEqual(first.convergence_history, second.convergence_history)
        self.assertEqual(first.convergence_history, [0] * 4)
        self.assertEqual(first.final_population_size, 100)
        self.assertEqual(matrix, [[0, 0], [0, 0]])

    def test_configuration(self):
        for arguments in ({'local_search_rate': True}, {'local_search_rate': 2},
                          {'local_search_max_passes': 0}, {'population_size': 1}):
            with self.assertRaises(ValueError):
                HybridGAConfig(**arguments)
