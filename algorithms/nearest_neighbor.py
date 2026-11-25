"""Deterministic nearest-neighbor TSP baseline implemented from scratch.

Does not use built-in min() or external optimization libraries.
Maintains a boolean visited array and loops manually over unvisited destinations.
"""

from core.tsp import _validate_distance_matrix, calculate_route_distance


def nearest_neighbor(distance_matrix: list[list[float]]) -> tuple[list[int], float]:
    """Visit the nearest unvisited ID, breaking distance ties by smallest ID."""
    _validate_distance_matrix(distance_matrix)
    n = len(distance_matrix)
    if n < 2:
        raise ValueError("At least two locations are required")

    visited = [False] * n
    visited[0] = True
    route = [0]
    unvisited_count = n - 1

    while unvisited_count > 0:
        current = route[-1]
        best_candidate = None
        best_distance = None

        for candidate in range(1, n):
            if not visited[candidate]:
                dist = distance_matrix[current][candidate]
                if best_distance is None:
                    best_distance = dist
                    best_candidate = candidate
                elif dist < best_distance:
                    best_distance = dist
                    best_candidate = candidate
                elif dist == best_distance:
                    # Break ties deterministically by smaller location ID
                    if candidate < best_candidate:
                        best_candidate = candidate

        visited[best_candidate] = True
        route.append(best_candidate)
        unvisited_count = unvisited_count - 1

    return route, calculate_route_distance(route, distance_matrix)
