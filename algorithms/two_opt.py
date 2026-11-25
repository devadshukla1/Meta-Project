"""Deterministic first-improvement 2-Opt for symmetric matrices.

Implemented manually without built-in sum() or external optimization libraries.
"""

from core.tsp import calculate_route_distance

EPSILON = 1e-10


def _compute_route_distance_manual(route: list[int], distance_matrix: list[list[float]]) -> float:
    """Manually calculate round-trip route distance without sum()."""
    total = 0.0
    n = len(route)
    for k in range(n):
        curr = route[k]
        nxt = route[0] if k == n - 1 else route[k + 1]
        total = total + distance_matrix[curr][nxt]
    return total


def two_opt(route: list[int], distance_matrix: list[list[float]],
            max_passes: int = 10) -> tuple[list[int], float]:
    """Return an improved copy; one pass accepts at most one improvement then restarts."""
    if type(max_passes) is not int or max_passes < 1:
        raise ValueError("max_passes must be a positive integer")
    distance = calculate_route_distance(route, distance_matrix)
    best = list(route)
    n = len(best)

    for _ in range(max_passes):
        improved = False
        for i in range(1, n - 1):
            for j in range(i + 1, n):
                a, b = best[i - 1], best[i]
                c, d = best[j], best[0 if j + 1 == n else j + 1]
                delta = (distance_matrix[a][c] + distance_matrix[b][d]
                         - distance_matrix[a][b] - distance_matrix[c][d])
                if delta < -EPSILON:
                    # Reverse segment from i to j inclusive: candidate = best[:i] + reversed(best[i:j+1]) + best[j+1:]
                    segment = best[i:j + 1]
                    rev_segment = []
                    for seg_idx in range(len(segment) - 1, -1, -1):
                        rev_segment.append(segment[seg_idx])
                    candidate = best[:i] + rev_segment + best[j + 1:]

                    value = _compute_route_distance_manual(candidate, distance_matrix)
                    if value < distance - EPSILON:
                        best = candidate
                        distance = value
                        improved = True
                        break
            if improved:
                break
        if not improved:
            break

    return best, calculate_route_distance(best, distance_matrix)
