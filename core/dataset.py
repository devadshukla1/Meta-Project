"""Synthetic Delhi-NCR-inspired delivery locations."""

from typing import TypedDict


class Location(TypedDict):
    id: int
    name: str
    x: float
    y: float
    type: str


# This dataset is fictional and intended for educational optimization experiments.
# Distances are calculated from synthetic Cartesian coordinates and do not
# represent actual road distances.
_LOCATIONS: tuple[Location, ...] = (
    {"id": 0, "name": "Central Warehouse", "x": 50.0, "y": 50.0, "type": "warehouse"},
    {"id": 1, "name": "Connaught Place", "x": 48.0, "y": 58.0, "type": "delivery"},
    {"id": 2, "name": "Karol Bagh", "x": 39.0, "y": 62.0, "type": "delivery"},
    {"id": 3, "name": "Chandni Chowk", "x": 52.0, "y": 70.0, "type": "delivery"},
    {"id": 4, "name": "Rohini", "x": 27.0, "y": 82.0, "type": "delivery"},
    {"id": 5, "name": "Pitampura", "x": 32.0, "y": 72.0, "type": "delivery"},
    {"id": 6, "name": "Dwarka", "x": 23.0, "y": 43.0, "type": "delivery"},
    {"id": 7, "name": "Janakpuri", "x": 31.0, "y": 51.0, "type": "delivery"},
    {"id": 8, "name": "Vasant Kunj", "x": 39.0, "y": 35.0, "type": "delivery"},
    {"id": 9, "name": "Saket", "x": 54.0, "y": 35.0, "type": "delivery"},
    {"id": 10, "name": "Lajpat Nagar", "x": 58.0, "y": 48.0, "type": "delivery"},
    {"id": 11, "name": "Mayur Vihar", "x": 68.0, "y": 55.0, "type": "delivery"},
    {"id": 12, "name": "Shahdara", "x": 72.0, "y": 72.0, "type": "delivery"},
    {"id": 13, "name": "Noida Sector 18", "x": 76.0, "y": 46.0, "type": "delivery"},
    {"id": 14, "name": "Greater Noida", "x": 91.0, "y": 29.0, "type": "delivery"},
    {"id": 15, "name": "Ghaziabad", "x": 84.0, "y": 79.0, "type": "delivery"},
    {"id": 16, "name": "Vaishali", "x": 76.0, "y": 65.0, "type": "delivery"},
    {"id": 17, "name": "Gurugram Cyber City", "x": 36.0, "y": 22.0, "type": "delivery"},
    {"id": 18, "name": "Faridabad", "x": 67.0, "y": 19.0, "type": "delivery"},
    {"id": 19, "name": "Sonipat", "x": 42.0, "y": 94.0, "type": "delivery"},
)


def get_delivery_locations() -> list[Location]:
    """Return independent copies of the predefined delivery locations."""
    return [location.copy() for location in _LOCATIONS]
