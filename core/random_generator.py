"""Manual pseudorandom number generator using Linear Congruential Generator (LCG).

Mathematical formulation:
    X_{n+1} = (a * X_n + c) mod m

Parameters (Numerical Recipes standard 32-bit LCG):
    multiplier a = 1664525
    increment c  = 1013904223
    modulus m    = 2^32 = 4294967296

Educational note:
    The Linear Congruential Generator is a lightweight, reproducible PRNG suitable
    for educational and algorithmic demonstrations. It does NOT possess cryptographic
    security or the high-dimensional equidistribution properties of generators such
    as the Mersenne Twister or PCG.
"""


class CustomRandom:
    """Manual Linear Congruential Generator (LCG) with reproducible state."""

    A = 1664525
    C = 1013904223
    M = 4294967296  # 2 ** 32

    def __init__(self, seed: int = 42):
        self._validate_and_set_seed(seed)

    def _validate_and_set_seed(self, seed: int) -> None:
        """Validate seed and normalize into valid 32-bit state range [0, M - 1]."""
        if isinstance(seed, bool) or not isinstance(seed, int):
            raise ValueError("Seed must be an integer")
        self.state = seed % self.M

    def next_integer(self) -> int:
        """Advance internal state and return next 32-bit unsigned integer [0, M - 1]."""
        self.state = (self.A * self.state + self.C) % self.M
        return self.state

    def random(self) -> float:
        """Return next random float in half-open interval [0.0, 1.0)."""
        return self.next_integer() / self.M

    def randint(self, minimum: int, maximum: int) -> int:
        """Return a random integer N in inclusive range [minimum, maximum].

        Uses rejection sampling to eliminate modulo bias.
        """
        if isinstance(minimum, bool) or not isinstance(minimum, int):
            raise ValueError("minimum must be an integer")
        if isinstance(maximum, bool) or not isinstance(maximum, int):
            raise ValueError("maximum must be an integer")
        if minimum > maximum:
            raise ValueError(f"minimum ({minimum}) cannot exceed maximum ({maximum})")

        range_size = maximum - minimum + 1
        if range_size == 1:
            return minimum

        # To avoid modulo bias, find largest multiple of range_size <= M
        limit = (self.M // range_size) * range_size
        while True:
            raw = self.next_integer()
            if raw < limit:
                return minimum + (raw % range_size)

    def shuffle(self, values: list) -> None:
        """Fisher-Yates in-place shuffle of elements using manual RNG."""
        if not isinstance(values, list):
            raise ValueError("values must be a list")
        n = len(values)
        for i in range(n - 1, 0, -1):
            j = self.randint(0, i)
            values[i], values[j] = values[j], values[i]

    def sample(self, values: list, count: int) -> list:
        """Sample count unique elements without replacement from values.

        Returns a new list containing the sampled elements.
        """
        if not isinstance(values, (list, tuple)):
            raise ValueError("values must be a list or tuple")
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise ValueError("count must be a non-negative integer")
        n = len(values)
        if count > n:
            raise ValueError(f"Cannot sample {count} elements from collection of size {n}")
        if count == 0:
            return []

        # Partial Fisher-Yates on a copy of indices or values
        pool = list(values)
        result = []
        for i in range(count):
            idx = self.randint(i, n - 1)
            pool[i], pool[idx] = pool[idx], pool[i]
            result.append(pool[i])
        return result
