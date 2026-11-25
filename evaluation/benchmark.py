"""Repeatable NN, GA, and Hybrid GA experiments with JSON/CSV export.

Uses manually implemented algorithms and statistical operations.
Replaces dataclass with ordinary classes and manual dict serialization.
"""

import csv
import json
import time
from pathlib import Path

from algorithms.genetic_algorithm import GAConfig, run_genetic_algorithm
from algorithms.hybrid_ga import HybridGAConfig, run_hybrid_ga
from algorithms.nearest_neighbor import nearest_neighbor
from core.dataset import get_delivery_locations
from core.mathematics import manual_abs
from core.tsp import (_validate_distance_matrix, calculate_route_distance,
                      create_distance_matrix, validate_route)
from evaluation.statistics import (calculate_mean, calculate_summary_statistics,
                                   percentage_improvement)


class BenchmarkConfig:
    """Run count and shared GA settings; seeds are base_seed + run index."""

    def __init__(
        self,
        number_of_runs: int = 20,
        base_seed: int = 42,
        population_size: int = 100,
        generations: int = 200,
        crossover_rate: float = 0.9,
        mutation_rate: float = 0.2,
        tournament_size: int = 3,
        elitism_count: int = 2,
        local_search_rate: float = 0.2,
        local_search_max_passes: int = 5,
    ):
        self.number_of_runs = number_of_runs
        self.base_seed = base_seed
        self.population_size = population_size
        self.generations = generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.tournament_size = tournament_size
        self.elitism_count = elitism_count
        self.local_search_rate = local_search_rate
        self.local_search_max_passes = local_search_max_passes
        self._validate()

    def _validate(self) -> None:
        if type(self.number_of_runs) is not int or self.number_of_runs < 1:
            raise ValueError("number_of_runs must be a positive integer")
        if type(self.base_seed) is not int:
            raise ValueError("base_seed must be an integer")
        # Validate against HybridGAConfig
        HybridGAConfig(**self.algorithm_settings(self.base_seed))

    def __setattr__(self, name, value):
        if hasattr(self, "_initialized") and self._initialized:
            raise AttributeError(f"Cannot modify immutable instance of {self.__class__.__name__}")
        super().__setattr__(name, value)
        if name == "local_search_max_passes":
            super().__setattr__("_initialized", True)

    def algorithm_settings(self, seed: int) -> dict:
        return {
            "population_size": self.population_size,
            "generations": self.generations,
            "crossover_rate": self.crossover_rate,
            "mutation_rate": self.mutation_rate,
            "tournament_size": self.tournament_size,
            "elitism_count": self.elitism_count,
            "seed": seed,
            "local_search_rate": self.local_search_rate,
            "local_search_max_passes": self.local_search_max_passes,
        }

    def to_dict(self) -> dict:
        return {
            "number_of_runs": self.number_of_runs,
            "base_seed": self.base_seed,
            "population_size": self.population_size,
            "generations": self.generations,
            "crossover_rate": self.crossover_rate,
            "mutation_rate": self.mutation_rate,
            "tournament_size": self.tournament_size,
            "elitism_count": self.elitism_count,
            "local_search_rate": self.local_search_rate,
            "local_search_max_passes": self.local_search_max_passes,
        }


def _record(name: str, run_number: int, result, matrix, nn_distance) -> dict:
    if not validate_route(result.best_route, len(matrix)):
        raise ValueError(f"{name} returned an invalid route")
    calc_dist = calculate_route_distance(result.best_route, matrix)
    diff = calc_dist - result.best_distance
    if diff < 0:
        diff = -diff
    if diff > 1e-8:
        raise ValueError(f"{name} returned an inconsistent distance")
    history = result.convergence_history
    if len(history) != result.generations_completed + 1:
        raise ValueError(f"{name} returned invalid convergence history length")
    for i in range(len(history) - 1):
        if history[i] + 1e-10 < history[i + 1]:
            raise ValueError(f"{name} returned invalid non-monotone convergence history")

    record = {
        "algorithm_name": name,
        "run_number": run_number,
        "seed": result.seed,
        "best_route": result.best_route,
        "best_distance": result.best_distance,
        "initial_best_distance": result.initial_best_distance,
        "improvement_percentage": percentage_improvement(
            result.initial_best_distance, result.best_distance
        ),
        "improvement_over_nn_percentage": percentage_improvement(
            nn_distance, result.best_distance
        ),
        "execution_time": result.execution_time,
        "generations_completed": result.generations_completed,
        "population_size": result.final_population_size,
        "convergence_history": history,
        "local_search_applications": getattr(result, "local_search_applications", None),
        "local_search_improvements": getattr(result, "local_search_improvements", None),
    }
    return record


def _summaries(runs: list[dict]) -> dict:
    def available_summary(key):
        values = [run[key] for run in runs if run[key] is not None]
        return calculate_summary_statistics(values) if values else None

    return {
        "distances": calculate_summary_statistics([run["best_distance"] for run in runs]),
        "execution_times": calculate_summary_statistics([run["execution_time"] for run in runs]),
        "initial_improvements": available_summary("improvement_percentage"),
        "improvements_over_nn": available_summary("improvement_over_nn_percentage"),
    }


def run_benchmark(distance_matrix: list[list[float]],
                  config: BenchmarkConfig | None = None, progress=None) -> dict:
    """Run paired-seed experiments; timing is measured inside each algorithm."""
    settings = BenchmarkConfig() if config is None else config
    if not isinstance(settings, BenchmarkConfig):
        raise ValueError("config must be BenchmarkConfig")
    _validate_distance_matrix(distance_matrix)
    if len(distance_matrix) < 2:
        raise ValueError("At least two locations are required")

    started = time.perf_counter()
    nn_route, nn_distance = nearest_neighbor(distance_matrix)
    nn_time = time.perf_counter() - started

    ga_runs, hybrid_runs, paired = [], [], []
    for index in range(settings.number_of_runs):
        seed = settings.base_seed + index
        arguments = settings.algorithm_settings(seed)
        hybrid_config = HybridGAConfig(**arguments)
        ga_config = GAConfig(**{key: value for key, value in arguments.items()
                                if key not in ("local_search_rate", "local_search_max_passes")})

        ga = _record("Genetic Algorithm", index + 1,
                     run_genetic_algorithm(distance_matrix, ga_config), distance_matrix, nn_distance)
        hybrid = _record("Hybrid Genetic Algorithm", index + 1,
                         run_hybrid_ga(distance_matrix, hybrid_config), distance_matrix, nn_distance)

        ga_runs.append(ga)
        hybrid_runs.append(hybrid)
        paired.append({
            "run_number": index + 1,
            "seed": seed,
            "hybrid_over_ga_percentage": percentage_improvement(
                ga["best_distance"], hybrid["best_distance"]
            ),
        })
        if progress is not None:
            progress(index + 1, settings.number_of_runs)

    def mean_history(runs):
        return [
            calculate_mean([run["convergence_history"][generation] for run in runs])
            for generation in range(settings.generations + 1)
        ]

    paired_values = [item["hybrid_over_ga_percentage"] for item in paired
                     if item["hybrid_over_ga_percentage"] is not None]

    return {
        "benchmark_config": settings.to_dict(),
        "dataset_information": {
            "number_of_locations": len(distance_matrix),
            "distance_units": "synthetic Cartesian units",
        },
        "nearest_neighbor_result": {
            "algorithm_name": "Nearest Neighbor",
            "deterministic": True,
            "best_route": nn_route,
            "best_distance": nn_distance,
            "execution_time": nn_time,
        },
        "ga_run_results": ga_runs,
        "hybrid_run_results": hybrid_runs,
        "ga_statistics": _summaries(ga_runs),
        "hybrid_statistics": _summaries(hybrid_runs),
        "comparison_statistics": {
            "paired_runs": paired,
            "paired_hybrid_over_ga": (
                calculate_summary_statistics(paired_values)
                if paired_values else None
            ),
        },
        "ga_mean_convergence": mean_history(ga_runs),
        "hybrid_mean_convergence": mean_history(hybrid_runs),
        "evaluation_budget_notes": (
            "Same matrix, GA settings, and seed schedule. Hybrid adds 2-Opt work; "
            "equal generations are not equal computational budgets. Exact objective "
            "evaluation counts were not measured. Algorithm times include initialization, "
            "evolution, local search when applicable, and scoring. "
            "Uses manual Linear Congruential Generator (LCG) and scratch math/sorting implementations."
        ),
    }


def save_benchmark(result: dict, output_dir: str | Path = "results") -> list[Path]:
    """Write only the three named benchmark outputs; reruns replace these files."""
    folder = Path(output_dir)
    folder.mkdir(parents=True, exist_ok=True)
    summary = {key: value for key, value in result.items()
               if key not in ("ga_run_results", "hybrid_run_results",
                              "ga_mean_convergence", "hybrid_mean_convergence")}
    summary["comparison_statistics"] = {
        "paired_hybrid_over_ga": result["comparison_statistics"]["paired_hybrid_over_ga"]}
    summary_path = folder / "benchmark_summary.json"
    runs_path = folder / "benchmark_runs.csv"
    history_path = folder / "convergence_history.json"
    summary_path.write_text(json.dumps(summary, indent=2, allow_nan=False), encoding="utf-8")
    columns = ("algorithm_name", "run_number", "seed", "best_distance",
               "initial_best_distance", "improvement_percentage",
               "improvement_over_nn_percentage", "execution_time",
               "generations_completed", "population_size", "local_search_applications",
               "local_search_improvements")
    with runs_path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=columns)
        writer.writeheader()
        for run in result["ga_run_results"] + result["hybrid_run_results"]:
            writer.writerow({key: run[key] for key in columns})
    histories = {
        "generation_indices": list(range(result["benchmark_config"]["generations"] + 1)),
        "ga_runs": [{"seed": run["seed"], "history": run["convergence_history"]}
                    for run in result["ga_run_results"]],
        "hybrid_runs": [{"seed": run["seed"], "history": run["convergence_history"]}
                        for run in result["hybrid_run_results"]],
        "ga_mean_convergence": result["ga_mean_convergence"],
        "hybrid_mean_convergence": result["hybrid_mean_convergence"],
    }
    history_path.write_text(json.dumps(histories, indent=2, allow_nan=False), encoding="utf-8")
    return [summary_path, runs_path, history_path]


def _main() -> None:
    locations = get_delivery_locations()
    matrix = create_distance_matrix(locations)
    config = BenchmarkConfig()
    print("=" * 60)
    print("ROUTE OPTIMIZER - PHASE 4: Benchmark Framework (Manual LCG)")
    print("=" * 60)
    print(f"Dataset Size : {len(locations)} locations")
    print(f"Runs         : {config.number_of_runs}")
    print(f"Base Seed    : {config.base_seed}")
    print(f"Generations  : {config.generations}")
    print(f"Population   : {config.population_size}")
    print("-" * 60)
    print("Running benchmarks...")

    def progress(done, total):
        print(f"  Completed run {done}/{total}...")

    results = run_benchmark(matrix, config, progress)
    saved_files = save_benchmark(results)
    print("-" * 60)
    print("Benchmark complete. Saved outputs:")
    for file_path in saved_files:
        print(f"  - {file_path}")
    print("=" * 60)


if __name__ == "__main__":
    _main()
