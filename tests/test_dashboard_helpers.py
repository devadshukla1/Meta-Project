import csv
import io
import unittest

from ui.helpers import (history_csv, improvement_text, locations_csv,
                        make_ga_config, matrix_csv, route_csv, route_svg)


class DashboardHelperTests(unittest.TestCase):
    def setUp(self):
        self.places = [{"id": 0, "name": "Warehouse", "type": "warehouse", "x": 0, "y": 0},
                       {"id": 1, "name": "A&B", "type": "delivery", "x": 1, "y": 1}]

    def test_route_svg_and_csv(self):
        svg = route_svg(self.places, [0, 1])
        self.assertIn("A&amp;B", svg)
        self.assertEqual(svg.count("<line "), 2)
        rows = list(csv.DictReader(io.StringIO(route_csv([0, 1], self.places, "NN"))))
        self.assertEqual([row["location_id"] for row in rows], ["0", "1", "0"])
        self.assertEqual(len(list(csv.DictReader(io.StringIO(locations_csv(self.places))))), 2)

    def test_config_and_unavailable(self):
        values = dict(population_size=4, generations=2, crossover_rate=.9,
                      mutation_rate=.2, tournament_size=2, elitism_count=1, seed=42,
                      local_search_rate=.3, local_search_max_passes=2)
        self.assertEqual(make_ga_config(values, True).local_search_rate, .3)
        self.assertEqual(improvement_text(0, 0), "N/A")
        self.assertEqual(list(csv.reader(io.StringIO(history_csv({"GA": [3, 2]}))))[1], ["0", "3"])

    def test_matrix_export(self):
        matrix = [[0, 1], [1, 0]]
        rows = list(csv.reader(io.StringIO(matrix_csv(matrix))))
        self.assertEqual(rows, [["id", "0", "1"], ["0", "0", "1"], ["1", "1", "0"]])
