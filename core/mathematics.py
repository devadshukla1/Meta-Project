"""Manual mathematical functions implemented from scratch.

Provides exact replacements for:
    math.sqrt()      -> manual_sqrt() (Newton-Raphson approximation)
    math.isfinite()  -> is_finite_number()
    abs()            -> manual_abs()
    sum()            -> manual_sum()
    min()            -> manual_min()
    max()            -> manual_max()

No external or built-in mathematical libraries are used.
"""


def is_finite_number(value) -> bool:
    """Return True if value is a finite int or float; reject booleans, NaN, and +/-inf."""
    if isinstance(value, bool):
        return False
    if not isinstance(value, (int, float)):
        return False
    # In IEEE 754 float: NaN != NaN
    if value != value:
        return False
    # Check for infinity: inf - inf is NaN (which does not equal itself)
    # or float('inf') == value / float('-inf') == value
    # Without importing math or creating float('inf'):
    # A finite number multiplied by 1.0 does not produce an overflow or equality with its sign * inf
    # In standard Python: 1e308 is finite, inf is larger than any float, but we can check:
    # inf > 1e308 and -inf < -1e308 and value - value != 0.0 for non-finite floats
    try:
        diff = value - value
        if diff != 0.0 or diff != diff:
            return False
    except (OverflowError, ValueError):
        return False
    return True


def manual_abs(number: int | float) -> int | float:
    """Return absolute value of number using basic comparison."""
    if not is_finite_number(number):
        raise ValueError("Input to manual_abs must be a finite number")
    return -number if number < 0 else number


def manual_sqrt(number: int | float, tolerance: float = 1e-12, max_iterations: int = 100) -> float:
    """Compute square root using the Newton-Raphson method from scratch.

    Iterative formula:
        x_{n+1} = 0.5 * (x_n + S / x_n)

    Does not use math.sqrt() or number ** 0.5.
    """
    if not is_finite_number(number):
        raise ValueError("Input to manual_sqrt must be a finite number")
    if number < 0:
        raise ValueError("Cannot calculate square root of a negative number")
    if number == 0 or number == 0.0:
        return 0.0

    # Initial guess heuristic without using log/exp/power
    num = float(number)
    guess = num if num >= 1.0 else 1.0
    # Refine initial guess order of magnitude if very large or very small
    if num > 100.0:
        # Scale down roughly to avoid excess iterations
        scale = num
        rough = 1.0
        while scale >= 4.0:
            scale = scale / 4.0
            rough = rough * 2.0
        guess = rough * 1.5
    elif num < 0.01:
        scale = num
        rough = 1.0
        while scale <= 0.25:
            scale = scale * 4.0
            rough = rough / 2.0
        guess = rough * 0.5

    iteration = 0
    while iteration < max_iterations:
        next_guess = 0.5 * (guess + num / guess)
        diff = next_guess - guess
        if diff < 0:
            diff = -diff
        if diff <= tolerance:
            return next_guess
        guess = next_guess
        iteration = iteration + 1

    return guess


def manual_sum(values, start: int | float = 0) -> int | float:
    """Sum items of an iterable manually using an explicit loop.

    Does not use the built-in sum().
    """
    total = start
    for item in values:
        total = total + item
    return total


def manual_min(values, key=None):
    """Find minimum value in a collection using an explicit comparison loop.

    Does not use the built-in min().
    """
    iterator = iter(values)
    try:
        first = next(iterator)
    except StopIteration:
        raise ValueError("manual_min() arg is an empty sequence")

    min_val = first
    min_key = first if key is None else key(first)

    for item in iterator:
        k = item if key is None else key(item)
        if k < min_key:
            min_key = k
            min_val = item
    return min_val


def manual_max(values, key=None):
    """Find maximum value in a collection using an explicit comparison loop.

    Does not use the built-in max().
    """
    iterator = iter(values)
    try:
        first = next(iterator)
    except StopIteration:
        raise ValueError("manual_max() arg is an empty sequence")

    max_val = first
    max_key = first if key is None else key(first)

    for item in iterator:
        k = item if key is None else key(item)
        if k > max_key:
            max_key = k
            max_val = item
    return max_val
