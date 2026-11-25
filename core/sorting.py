"""Manual stable Merge Sort algorithm implemented from scratch.

Does not use sorted() or list.sort().
Complexity:
    Time: O(n log n) in worst, average, and best cases.
    Space: O(n) auxiliary space.
"""


def _merge(left: list, right: list, key) -> list:
    """Merge two sorted lists stably using custom key function."""
    result = []
    i = 0
    j = 0
    len_left = len(left)
    len_right = len(right)

    while i < len_left and j < len_right:
        key_left = left[i] if key is None else key(left[i])
        key_right = right[j] if key is None else key(right[j])

        # <= preserves stability: if elements are equal, left item comes first
        if key_left <= key_right:
            result.append(left[i])
            i = i + 1
        else:
            result.append(right[j])
            j = j + 1

    while i < len_left:
        result.append(left[i])
        i = i + 1

    while j < len_right:
        result.append(right[j])
        j = j + 1

    return result


def merge_sort(values: list, key=None) -> list:
    """Return a new list containing all items from values in ascending order.

    Does not modify the original list.
    Preserves relative order of items with identical keys (stable sort).
    """
    if not isinstance(values, (list, tuple)):
        values = list(values)
    else:
        values = list(values)

    n = len(values)
    if n <= 1:
        return values

    mid = n // 2
    left = merge_sort(values[:mid], key=key)
    right = merge_sort(values[mid:], key=key)

    return _merge(left, right, key=key)
