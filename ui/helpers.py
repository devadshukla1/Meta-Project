"""Pure formatting, CSV, and synthetic-route drawing helpers."""

import csv
import html
import io
from algorithms.genetic_algorithm import GAConfig
from algorithms.hybrid_ga import HybridGAConfig
from core.tsp import validate_route
from evaluation.statistics import percentage_improvement


def csv_text(headers, rows) -> str:
    """Create an in-memory CSV with consistent column order."""
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(rows)
    return output.getvalue()


def locations_csv(locations) -> str:
    return csv_text(("id", "name", "type", "x", "y"),
                    ((place["id"], place["name"], place["type"], place["x"], place["y"])
                     for place in locations))


def matrix_csv(matrix) -> str:
    return csv_text(("id", *range(len(matrix))),
                    ((index, *row) for index, row in enumerate(matrix)))


def route_csv(route, locations, algorithm, seed=None, config=None) -> str:
    """Export each visit including the final warehouse return."""
    settings = "" if config is None else str(config)
    return csv_text(("visit_order", "location_id", "location_name", "algorithm", "seed", "configuration"),
                    ((order, index, locations[index]["name"], algorithm,
                      "" if seed is None else seed, settings)
                     for order, index in enumerate(route + [0])))


def history_csv(series: dict[str, list[float]]) -> str:
    length = len(next(iter(series.values())))
    if any(len(values) != length for values in series.values()):
        raise ValueError("Convergence histories must have the same length")
    return csv_text(("generation", *series),
                    ((index, *(values[index] for values in series.values()))
                     for index in range(length)))


def improvement_text(reference, candidate) -> str:
    value = percentage_improvement(reference, candidate)
    return "N/A" if value is None else f"{value:.2f}%"


def make_ga_config(values: dict, hybrid: bool = False):
    """Map form values directly to validated optimization configuration."""
    fields = ("population_size", "generations", "crossover_rate", "mutation_rate",
              "tournament_size", "elitism_count", "seed")
    arguments = {key: values[key] for key in fields}
    if hybrid:
        arguments.update({key: values[key] for key in
                          ("local_search_rate", "local_search_max_passes")})
        return HybridGAConfig(**arguments)
    return GAConfig(**arguments)


def route_svg(locations, route=None) -> str:
    """Draw actual Cartesian points and an optional round-trip route."""
    if route is not None and not validate_route(route, len(locations)):
        raise ValueError("Route must visit each location once")
    width, height, margin = 900, 570, 54
    xs = [place["x"] for place in locations]
    ys = [place["y"] for place in locations]
    low_x, high_x, low_y, high_y = min(xs), max(xs), min(ys), max(ys)

    def point(place):
        x = margin + (place["x"] - low_x) / (high_x - low_x or 1) * (width - 2 * margin)
        y = height - margin - (place["y"] - low_y) / (high_y - low_y or 1) * (height - 2 * margin)
        return x, y

    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
             'role="img" aria-label="Synthetic Cartesian delivery route" '
             'style="width:100%;height:auto;background:#111827;border-radius:18px">',
             '<defs><marker id="arrow" markerWidth="7" markerHeight="7" refX="5" '
             'refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7" fill="#10b981"/></marker></defs>']
    if route is not None:
        for start, end in zip(route + [0], (route + [0])[1:]):
            x1, y1 = point(locations[start])
            x2, y2 = point(locations[end])
            parts.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" '
                         f'y2="{y2:.2f}" stroke="#10b981" stroke-width="2.5" '
                         'opacity=".8" marker-end="url(#arrow)"/>')
    for place in locations:
        x, y = point(place)
        warehouse = place["id"] == 0
        color = "#f59e0b" if warehouse else "#38bdf8"
        name = html.escape(place["name"])
        parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{8 if warehouse else 5}" '
                     f'fill="{color}" stroke="#f8fafc" stroke-width="1"><title>{name}</title></circle>')
        parts.append(f'<text x="{x + 9:.2f}" y="{y - 8:.2f}" fill="#f8fafc" '
                     f'font-size="12" font-family="Arial">{name}</text>')
    return "".join(parts) + "</svg>"
