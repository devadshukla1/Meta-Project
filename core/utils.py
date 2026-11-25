"""Reproducible route generation using custom pseudorandom generator."""

from core.random_generator import CustomRandom


def create_random_generator(seed: int = 42) -> CustomRandom:
    """Return an independent custom pseudorandom generator."""
    return CustomRandom(seed)


def generate_random_route(number_of_locations: int, rng: CustomRandom) -> list[int]:
    """Shuffle delivery IDs using Fisher-Yates via the supplied custom generator; keep warehouse first."""
    if type(number_of_locations) is not int or number_of_locations < 2:
        raise ValueError("Number of locations must be an integer of at least 2")
    if not isinstance(rng, CustomRandom):
        raise ValueError("rng must be a CustomRandom instance")
    deliveries = list(range(1, number_of_locations))
    rng.shuffle(deliveries)
    return [0] + deliveries
