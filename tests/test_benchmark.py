import csv
import json
import tempfile
import unittest
from pathlib import Path
from evaluation.benchmark import BenchmarkConfig, run_benchmark, save_benchmark


class BenchmarkTests(unittest.TestCase):
    def test_runs_and_exports(self):
        matrix = [[0, 1, 2], [1, 0, 1], [2, 1, 0]]
        config = BenchmarkConfig(number_of_runs=2, population_size=5,
                                 generations=2, tournament_size=2, elitism_count=1)
        result = run_benchmark(matrix, config)
        self.assertEqual([run['seed'] for run in result['ga_run_results']], [42, 43])
        self.assertEqual([run['seed'] for run in result['hybrid_run_results']], [42, 43])
        self.assertEqual(len(result['ga_mean_convergence']), 3)
        self.assertEqual(len(result['hybrid_mean_convergence']), 3)
        self.assertEqual(matrix[0], [0, 1, 2])
        repeat = run_benchmark(matrix, config)
        self.assertEqual([run['best_route'] for run in result['hybrid_run_results']],
                         [run['best_route'] for run in repeat['hybrid_run_results']])
        with tempfile.TemporaryDirectory() as folder:
            paths = save_benchmark(result, folder)
            self.assertEqual(len(paths), 3)
            self.assertEqual(json.loads(Path(paths[0]).read_text())['benchmark_config']['number_of_runs'], 2)
            with Path(paths[1]).open(newline='') as source:
                self.assertEqual(len(list(csv.DictReader(source))), 4)

    def test_zero_denominators_and_invalid_config(self):
        config = BenchmarkConfig(number_of_runs=1, population_size=4,
                                 generations=1, tournament_size=2, elitism_count=1)
        result = run_benchmark([[0, 0], [0, 0]], config)
        self.assertIsNone(result['ga_statistics']['improvements_over_nn'])
        for arguments in ({'number_of_runs': 0}, {'base_seed': True},
                          {'population_size': 1}, {'local_search_rate': 2}):
            with self.assertRaises(ValueError):
                BenchmarkConfig(**arguments)
