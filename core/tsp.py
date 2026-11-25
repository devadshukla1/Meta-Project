"""Distance and route operations for the symmetric TSP.

Implemented using manual mathematical operations without built-in math or external libraries.
"""

from core.mathematics import is_finite_number, manual_sqrt, manual_sum


def _coordinates(point) -> tuple[float, float]:
    # Check if point behaves like a mapping (dict)
    if not hasattr(point, "__getitem__"):
        raise ValueError("Location must be a mapping with numeric x and y fields")
    try:
        x, y = point["x"], point["y"]
    except (KeyError, TypeError) as error:
        raise ValueError(f"Location is missing coordinate or invalid mapping") from error
    if not is_finite_number(x) or not is_finite_number(y):
        raise ValueError("Location coordinates must be finite numbers")
    return float(x), float(y)


def calculate_euclidean_distance(point1, point2) -> float:
    """Calculate full-precision Euclidean distance between two locations using Newton-Raphson sqrt."""
    x1, y1 = _coordinates(point1)
    x2, y2 = _coordinates(point2)
    dx = x2 - x1
    dy = y2 - y1
    return manual_sqrt(dx * dx + dy * dy)


def create_distance_matrix(locations: list) -> list[list[float]]:
    """Build a symmetric matrix; location IDs must equal their list indices."""
    if not isinstance(locations, list) or len(locations) == 0:
        raise ValueError("Locations must be a nonempty list")
    for index, location in enumerate(locations):
        loc_id = location.get("id") if hasattr(location, "get") else None
        if type(loc_id) is not int or loc_id != index:
            raise ValueError("Location IDs must be consecutive and ordered from zero")
        _coordinates(location)
    size = len(locations)
    matrix = [[0.0] * size for _ in range(size)]
    for row in range(size):
        for column in range(row + 1, size):
            distance = calculate_euclidean_distance(locations[row], locations[column])
            matrix[row][column] = matrix[column][row] = distance
    return matrix


def validate_route(route: list[int], number_of_locations: int) -> bool:
    """Accept only a list of each integer ID once, starting with warehouse 0.

    Verifies permutation manually using a visited array rather than set equality.
    """
    if type(number_of_locations) is not int or number_of_locations <= 0:
        return False
    if not isinstance(route, list) or len(route) != number_of_locations:
        return False
    if len(route) == 0 or route[0] != 0:
        return False

    visited = [False] * number_of_locations
    for location_id in route:
        if type(location_id) is not int:
            return False
        if location_id < 0 or location_id >= number_of_locations:
            return False
        if visited[location_id]:
            # Duplicate location
            return False
        visited[location_id] = True

    for was_visited in visited:
        if not was_visited:
            return False

    return True


def _validate_distance_matrix(matrix: list[list[float]]) -> None:
    if not isinstance(matrix, list) or len(matrix) == 0:
        raise ValueError("Distance matrix must be a nonempty square list")
    size = len(matrix)
    for row in matrix:
        if not isinstance(row, list) or len(row) != size:
            raise ValueError("Distance matrix must be square")
        for value in row:
            if not is_finite_number(value) or value < 0:
                raise ValueError("Distances must be finite nonnegative numbers")
    for index in range(size):
        if matrix[index][index] != 0:
            raise ValueError("Distance matrix diagonal must be zero")
        for other in range(index + 1, size):
            if matrix[index][other] != matrix[other][index]:
                raise ValueError("Distance matrix must be symmetric")


def calculate_route_distance(route: list[int], distance_matrix: list[list[float]]) -> float:
    """Return the route distance including the final return to warehouse 0.

    Calculated using manual summation loop without built-in sum().
    """
    _validate_distance_matrix(distance_matrix)
    if not validate_route(route, len(distance_matrix)):
        raise ValueError("Route must visit each location once, starting at warehouse 0")

    total_distance = 0.0
    n = len(route)
    for i in range(n):
        current = route[i]
        following = route[0] if i == n - 1 else route[i + 1]
        total_distance = total_distance + distance_matrix[current][following]

    return float(total_distance)


def _main() -> None:
    from core.dataset import get_delivery_locations
    from core.utils import create_random_generator, generate_random_route

    locations = get_delivery_locations()
    matrix = create_distance_matrix(locations)
    route = generate_random_route(len(locations), create_random_generator(42))
    print("=" * 40)
    print("       ROUTE OPTIMIZER - PHASE 1")
    print("=" * 40)
    print(f"Total Locations : {len(locations)}")
    print(f"Warehouse       : {locations[0]['name']}")
    print("Random Seed     : 42\n")
    print("Generated Route:")
    print("\n    ->\n".join(locations[index]["name"] for index in route + [0]))
    print(f"\nRoute Valid     : {validate_route(route, len(locations))}")
    print(f"Returns to Warehouse : {route[0] == 0 and locations[route[0]]['name'] == locations[0]['name']}")
    print(f"Total Distance  : {calculate_route_distance(route, matrix):.2f} synthetic units")
    print("=" * 40)


if __name__ == "__main__":
    _main()
