"""Memetic GA using the shared evolution loop and 2-Opt.

Implemented manually without built-in dataclasses or ready-made optimization libraries.
"""

from algorithms.genetic_algorithm import GAConfig, GAResult, _run_evolution
from algorithms.two_opt import EPSILON, two_opt
from core.tsp import calculate_route_distance, validate_route


class HybridGAConfig(GAConfig):
    """Hybrid GA settings extending GAConfig with local search rate and passes."""

    def __init__(
        self,
        population_size: int = 100,
        generations: int = 200,
        crossover_rate: float = 0.9,
        mutation_rate: float = 0.2,
        tournament_size: int = 3,
        elitism_count: int = 2,
        seed: int = 42,
        local_search_rate: float = 0.2,
        local_search_max_passes: int = 5,
    ):
        self.local_search_rate = local_search_rate
        self.local_search_max_passes = local_search_max_passes
        super().__init__(
            population_size=population_size,
            generations=generations,
            crossover_rate=crossover_rate,
            mutation_rate=mutation_rate,
            tournament_size=tournament_size,
            elitism_count=elitism_count,
            seed=seed,
        )

    def _validate(self) -> None:
        super()._validate()
        rate = self.local_search_rate
        if isinstance(rate, bool) or not isinstance(rate, (int, float)) or not 0 <= rate <= 1:
            raise ValueError("local_search_rate must be between 0 and 1")
        if type(self.local_search_max_passes) is not int or self.local_search_max_passes < 1:
            raise ValueError("local_search_max_passes must be a positive integer")

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["local_search_rate"] = self.local_search_rate
        data["local_search_max_passes"] = self.local_search_max_passes
        return data

    def __repr__(self) -> str:
        return (f"HybridGAConfig(population_size={self.population_size}, generations={self.generations}, "
                f"crossover_rate={self.crossover_rate}, mutation_rate={self.mutation_rate}, "
                f"tournament_size={self.tournament_size}, elitism_count={self.elitism_count}, "
                f"seed={self.seed}, local_search_rate={self.local_search_rate}, "
                f"local_search_max_passes={self.local_search_max_passes})")


class HybridGAResult(GAResult):
    """Hybrid GA result including local search statistics."""

    def __init__(
        self,
        best_route: list[int],
        best_distance: float,
        convergence_history: list[float],
        initial_best_distance: float,
        final_population_size: int,
        generations_completed: int,
        seed: int,
        execution_time: float,
        local_search_applications: int = 0,
        local_search_improvements: int = 0,
    ):
        super().__init__(
            best_route=best_route,
            best_distance=best_distance,
            convergence_history=convergence_history,
            initial_best_distance=initial_best_distance,
            final_population_size=final_population_size,
            generations_completed=generations_completed,
            seed=seed,
            execution_time=execution_time,
        )
        self.local_search_applications = local_search_applications
        self.local_search_improvements = local_search_improvements

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["local_search_applications"] = self.local_search_applications
        data["local_search_improvements"] = self.local_search_improvements
        return data


def run_hybrid_ga(distance_matrix: list[list[float]],
                  config: HybridGAConfig | None = None) -> HybridGAResult:
    """Apply bounded local search to selected offspring, never to elites."""
    settings = HybridGAConfig() if config is None else config
    if not isinstance(settings, HybridGAConfig):
        raise ValueError("config must be HybridGAConfig")
    applications = 0
    improvements = 0

    def improve(route, rng):
        nonlocal applications, improvements
        if settings.local_search_rate > 0 and rng.random() < settings.local_search_rate:
            before = calculate_route_distance(route, distance_matrix)
            route, after = two_opt(route, distance_matrix, settings.local_search_max_passes)
            applications += 1
            if after < before - EPSILON:
                improvements += 1
        if not validate_route(route, len(distance_matrix)):
            raise ValueError("Invalid offspring")
        return route

    result = _run_evolution(distance_matrix, settings, improve)
    return HybridGAResult(
        best_route=result.best_route,
        best_distance=result.best_distance,
        convergence_history=result.convergence_history,
        initial_best_distance=result.initial_best_distance,
        final_population_size=result.final_population_size,
        generations_completed=result.generations_completed,
        seed=result.seed,
        execution_time=result.execution_time,
        local_search_applications=applications,
        local_search_improvements=improvements,
    )


def _main() -> None:
    from core.dataset import get_delivery_locations
    from core.tsp import create_distance_matrix
    locations = get_delivery_locations()
    config = HybridGAConfig()
    result = run_hybrid_ga(create_distance_matrix(locations), config)
    print("ROUTE OPTIMIZER - PHASE 3: Hybrid GA + 2-Opt")
    print(config)
    print(f"Initial Distance: {result.initial_best_distance:.2f}")
    print(f"Best Distance: {result.best_distance:.2f} synthetic units")
    percentage = (100 * (1 - result.best_distance / result.initial_best_distance)
                  if result.initial_best_distance else 0)
    print(f"Improvement: {percentage:.2f}%")
    print(f"Execution Time: {result.execution_time:.3f} seconds")
    print(f"Applications: {result.local_search_applications}")
    print(f"Improvements: {result.local_search_improvements}")
    print(f"Generations: {result.generations_completed}")
    print(" -> ".join(locations[i]['name'] for i in result.best_route + [0]))
    print(f"Route Valid: {validate_route(result.best_route, len(locations))}")


if __name__ == '__main__':
    _main()
