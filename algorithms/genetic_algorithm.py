"""Permutation-based genetic algorithm for the symmetric delivery TSP.

Implemented manually without built-in random, math, or dataclasses.
Uses CustomRandom, Merge Sort, and manual loops/comparisons throughout.
"""

import time

from core.random_generator import CustomRandom
from core.sorting import merge_sort
from core.tsp import _validate_distance_matrix, calculate_route_distance, validate_route
from core.utils import create_random_generator, generate_random_route


class GAConfig:
    """GA settings: rates are per offspring; generations exclude initialization."""

    def __init__(
        self,
        population_size: int = 100,
        generations: int = 200,
        crossover_rate: float = 0.9,
        mutation_rate: float = 0.2,
        tournament_size: int = 3,
        elitism_count: int = 2,
        seed: int = 42,
    ):
        self.population_size = population_size
        self.generations = generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.tournament_size = tournament_size
        self.elitism_count = elitism_count
        self.seed = seed
        self._validate()

    def _validate(self) -> None:
        for name, minimum in (("population_size", 2), ("generations", 1)):
            value = getattr(self, name)
            if type(value) is not int or value < minimum:
                raise ValueError(f"{name} must be an integer of at least {minimum}")
        for name in ("crossover_rate", "mutation_rate"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 1:
                raise ValueError(f"{name} must be between 0 and 1")
        if (type(self.tournament_size) is not int
                or not 2 <= self.tournament_size <= self.population_size):
            raise ValueError("tournament_size must be between 2 and population_size")
        if (type(self.elitism_count) is not int
                or not 1 <= self.elitism_count < self.population_size):
            raise ValueError("elitism_count must be at least 1 and below population_size")
        if type(self.seed) is not int:
            raise ValueError("seed must be an integer, not a boolean")

    def __setattr__(self, name, value):
        # Allow initial assignment during __init__
        if hasattr(self, "_initialized") and self._initialized:
            raise AttributeError(f"Cannot modify immutable instance of {self.__class__.__name__}")
        super().__setattr__(name, value)
        if name == "seed":
            super().__setattr__("_initialized", True)

    def to_dict(self) -> dict:
        return {
            "population_size": self.population_size,
            "generations": self.generations,
            "crossover_rate": self.crossover_rate,
            "mutation_rate": self.mutation_rate,
            "tournament_size": self.tournament_size,
            "elitism_count": self.elitism_count,
            "seed": self.seed,
        }

    def __repr__(self) -> str:
        return (f"GAConfig(population_size={self.population_size}, generations={self.generations}, "
                f"crossover_rate={self.crossover_rate}, mutation_rate={self.mutation_rate}, "
                f"tournament_size={self.tournament_size}, elitism_count={self.elitism_count}, "
                f"seed={self.seed})")


class GAResult:
    """Best-so-far route and measurements from one GA run."""

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
    ):
        self.best_route = best_route
        self.best_distance = best_distance
        self.convergence_history = convergence_history
        self.initial_best_distance = initial_best_distance
        self.final_population_size = final_population_size
        self.generations_completed = generations_completed
        self.seed = seed
        self.execution_time = execution_time

    def to_dict(self) -> dict:
        return {
            "best_route": self.best_route,
            "best_distance": self.best_distance,
            "convergence_history": self.convergence_history,
            "initial_best_distance": self.initial_best_distance,
            "final_population_size": self.final_population_size,
            "generations_completed": self.generations_completed,
            "seed": self.seed,
            "execution_time": self.execution_time,
        }


def initialize_population(population_size: int, number_of_locations: int,
                          rng: CustomRandom) -> list[list[int]]:
    """Generate independent valid routes; duplicate routes across population are allowed."""
    if type(population_size) is not int or population_size < 2:
        raise ValueError("population_size must be an integer of at least 2")
    population = []
    for _ in range(population_size):
        population.append(generate_random_route(number_of_locations, rng))
    return population


def evaluate_population(population: list[list[int]],
                        distance_matrix: list[list[float]]) -> list[float]:
    """Score every route by total round-trip distance; lower is better."""
    distances = []
    for route in population:
        distances.append(calculate_route_distance(route, distance_matrix))
    return distances


def tournament_selection(population: list[list[int]], distances: list[float],
                          tournament_size: int, rng: CustomRandom) -> list[int]:
    """Select lowest-distance sampled route; ties preserve earlier population index."""
    n = len(population)
    if (not population or n != len(distances)
            or type(tournament_size) is not int
            or not 2 <= tournament_size <= n):
        raise ValueError("Invalid tournament population, distances, or size")

    # Sample tournament_size unique indices from range(n) without replacement
    candidates = rng.sample(list(range(n)), tournament_size)

    # Find winner with minimum distance using manual comparison loop
    winner = candidates[0]
    best_dist = distances[winner]

    for candidate in candidates[1:]:
        c_dist = distances[candidate]
        if c_dist < best_dist:
            best_dist = c_dist
            winner = candidate
        elif c_dist == best_dist:
            # Deterministic tie-breaking: lower population index wins
            if candidate < winner:
                winner = candidate

    return population[winner]


def _check_parent(route: list[int]) -> None:
    if not isinstance(route, list) or not validate_route(route, len(route)):
        raise ValueError("Parents and mutation routes must be valid permutations")


def order_crossover(parent1: list[int], parent2: list[int],
                    rng: CustomRandom) -> list[int]:
    """OX: copy a P1 segment, then fill circularly from P2 after the cut."""
    _check_parent(parent1)
    _check_parent(parent2)
    if len(parent1) != len(parent2) or len(parent1) < 2:
        raise ValueError("Parents must contain the same warehouse and delivery IDs")

    deliveries1 = parent1[1:]
    deliveries2 = parent2[1:]
    n_deliv = len(deliveries1)

    if n_deliv == 1:
        return list(parent1)

    # Sample 2 distinct cut indices and order them manually
    cut1, cut2 = rng.sample(list(range(n_deliv)), 2)
    start = cut1 if cut1 < cut2 else cut2
    end = cut2 if cut1 < cut2 else cut1

    child = [None] * n_deliv

    # Visited tracker for deliveries (ids 1 to n_deliv in problem, but delivery values)
    # Track which delivery values have been copied
    used_lookup = {}
    for pos in range(start, end + 1):
        gene = deliveries1[pos]
        child[pos] = gene
        used_lookup[gene] = True

    cursor = (end + 1) % n_deliv
    for offset in range(n_deliv):
        gene = deliveries2[(end + 1 + offset) % n_deliv]
        if gene not in used_lookup:
            child[cursor] = gene
            used_lookup[gene] = True
            cursor = (cursor + 1) % n_deliv

    return [0] + child


def swap_mutation(route: list[int], rng: CustomRandom) -> list[int]:
    """Swap two delivery positions and return a new chromosome."""
    _check_parent(route)
    child = list(route)
    n = len(child)
    if n > 2:
        # Sample two distinct delivery indices in range [1, n - 1]
        first, second = rng.sample(list(range(1, n)), 2)
        child[first], child[second] = child[second], child[first]
    return child


def run_genetic_algorithm(distance_matrix: list[list[float]],
                          config: GAConfig | None = None) -> GAResult:
    """Evolve routes while preserving elites and recording best-so-far distance."""
    return _run_evolution(distance_matrix, config)


def _find_best_individual(population: list[list[int]], distances: list[float]) -> int:
    """Return index of individual with minimum distance using manual comparison."""
    best_idx = 0
    best_dist = distances[0]
    n = len(population)
    for i in range(1, n):
        if distances[i] < best_dist:
            best_dist = distances[i]
            best_idx = i
        elif distances[i] == best_dist:
            if i < best_idx:
                best_idx = i
    return best_idx


def _run_evolution(distance_matrix, config=None, improve_offspring=None):
    """Shared generation loop; optional offspring improvement preserves RNG order."""
    settings = GAConfig() if config is None else config
    if not isinstance(settings, GAConfig):
        raise ValueError("config must be a GAConfig instance")
    _validate_distance_matrix(distance_matrix)
    if len(distance_matrix) < 2:
        raise ValueError("GA requires a warehouse and at least one destination")

    started = time.perf_counter()
    rng = create_random_generator(settings.seed)
    population = initialize_population(settings.population_size, len(distance_matrix), rng)
    distances = evaluate_population(population, distance_matrix)

    best_index = _find_best_individual(population, distances)
    best_route = list(population[best_index])
    best_distance = distances[best_index]
    initial_best_distance = best_distance
    history = [best_distance]

    for _ in range(settings.generations):
        # Rank individuals using manual merge_sort on indices
        # Sort indices by (distances[index], index)
        indices = list(range(len(population)))
        ranked = merge_sort(indices, key=lambda idx: (distances[idx], idx))

        next_population = []
        for elite_idx in range(settings.elitism_count):
            next_population.append(list(population[ranked[elite_idx]]))

        while len(next_population) < settings.population_size:
            parent1 = tournament_selection(population, distances, settings.tournament_size, rng)
            parent2 = tournament_selection(population, distances, settings.tournament_size, rng)

            if rng.random() < settings.crossover_rate:
                child = order_crossover(parent1, parent2, rng)
            else:
                child = list(parent1)

            if rng.random() < settings.mutation_rate:
                child = swap_mutation(child, rng)

            if improve_offspring is not None:
                child = improve_offspring(child, rng)

            next_population.append(child)

        population = next_population
        distances = evaluate_population(population, distance_matrix)
        generation_best = _find_best_individual(population, distances)

        if distances[generation_best] < best_distance:
            best_distance = distances[generation_best]
            best_route = list(population[generation_best])
        history.append(best_distance)

    elapsed_time = time.perf_counter() - started

    return GAResult(
        best_route=best_route,
        best_distance=best_distance,
        convergence_history=history,
        initial_best_distance=initial_best_distance,
        final_population_size=len(population),
        generations_completed=settings.generations,
        seed=settings.seed,
        execution_time=elapsed_time,
    )


def _main() -> None:
    from core.dataset import get_delivery_locations
    from core.tsp import create_distance_matrix

    locations = get_delivery_locations()
    matrix = create_distance_matrix(locations)
    config = GAConfig()
    result = run_genetic_algorithm(matrix, config)
    improvement = (100 * (result.initial_best_distance - result.best_distance)
                   / result.initial_best_distance if result.initial_best_distance else 0.0)
    print("=" * 50)
    print("         ROUTE OPTIMIZER - PHASE 2")
    print("=" * 50)
    print("Algorithm       : Genetic Algorithm")
    print("Problem         : Traveling Salesman Problem")
    print(f"Locations       : {len(locations)}")
    print(f"Population      : {config.population_size}")
    print(f"Generations     : {config.generations}")
    print(f"Crossover Rate  : {config.crossover_rate:.2f}")
    print(f"Mutation Rate   : {config.mutation_rate:.2f}")
    print(f"Random Seed     : {config.seed}")
    print("-" * 50)
    print("RESULTS")
    print("-" * 50)
    print(f"Initial Distance : {result.initial_best_distance:.2f} synthetic units")
    print(f"Best Distance    : {result.best_distance:.2f} synthetic units")
    print(f"Improvement      : {improvement:.2f}%")
    print(f"Execution Time   : {result.execution_time:.3f} seconds")
    print("\nBest Delivery Route:\n")
    print("\n    ->\n".join(locations[index]["name"]
                              for index in result.best_route + [0]))
    print(f"\nRoute Valid      : {validate_route(result.best_route, len(locations))}")
    print("=" * 50)


if __name__ == "__main__":
    _main()
