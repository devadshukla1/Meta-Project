"""Validated descriptive statistics for benchmark observations.

Implemented manually without built-in math, statistics, sum(), min(), max(), or sorted().
Uses manual_sqrt(), manual_sum(), manual_min(), manual_max(), merge_sort(), and is_finite_number().
"""

from core.mathematics import (is_finite_number, manual_max, manual_min,
                              manual_sqrt, manual_sum)
from core.sorting import merge_sort


def _values(values) -> list[float]:
    if not isinstance(values, (list, tuple)) or len(values) == 0:
        raise ValueError("values must be a nonempty list or tuple")
    result = []
    for value in values:
        if not is_finite_number(value):
            raise ValueError("values must contain only finite numbers")
        result.append(float(value))
    return result


def calculate_mean(values) -> float:
    """Return the arithmetic mean of finite numeric observations."""
    numbers = _values(values)
    total = manual_sum(numbers)
    return total / len(numbers)


def calculate_median(values) -> float:
    """Return the middle observation or mean of the two middle values using manual Merge Sort."""
    numbers = _values(values)
    sorted_numbers = merge_sort(numbers)
    n = len(sorted_numbers)
    mid = n // 2
    if n % 2 == 1:
        return sorted_numbers[mid]
    else:
        return (sorted_numbers[mid - 1] + sorted_numbers[mid]) / 2.0


def calculate_standard_deviation(values) -> float | None:
    """Return sample standard deviation, or None for one observation.

    Formula:
        Variance = Sum_{i=1}^n (x_i - mean)^2 / (n - 1)
        Standard Deviation = manual_sqrt(Variance)
    """
    numbers = _values(values)
    n = len(numbers)
    if n <= 1:
        return None

    mean = calculate_mean(numbers)
    sum_squared_deviations = 0.0
    for x in numbers:
        diff = x - mean
        sum_squared_deviations = sum_squared_deviations + diff * diff

    variance = sum_squared_deviations / (n - 1)
    return manual_sqrt(variance)


def calculate_summary_statistics(values) -> dict:
    """Summarize count, extrema, center, and sample spread using manual algorithms."""
    numbers = _values(values)
    return {
        "count": len(numbers),
        "min": manual_min(numbers),
        "max": manual_max(numbers),
        "mean": calculate_mean(numbers),
        "median": calculate_median(numbers),
        "standard_deviation": calculate_standard_deviation(numbers),
    }


def percentage_improvement(reference: float, candidate: float) -> float | None:
    """Return percentage reduction, or None when reference is zero."""
    _values([reference, candidate])
    return (reference - candidate) / reference * 100.0 if reference != 0.0 else None
