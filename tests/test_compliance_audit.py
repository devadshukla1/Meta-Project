"""Automated library compliance audit test.

Inspects computational modules (algorithms/, core/, evaluation/statistics.py)
to verify that no prohibited standard libraries, external packages, or built-in
shortcuts are used.
"""

import ast
from pathlib import Path
import unittest

PROHIBITED_MODULES = {
    "random",
    "math",
    "statistics",
    "numpy",
    "scipy",
    "pandas",
    "deap",
    "pyswarms",
    "pygad",
    "ortools",
    "networkx",
    "itertools",
    "heapq",
    "functools",
    "collections",
    "dataclasses",
}

PROHIBITED_CALLS = {
    "sum",
    "min",
    "max",
    "sorted",
}

COMPUTATIONAL_FILES = [
    Path("algorithms/genetic_algorithm.py"),
    Path("algorithms/hybrid_ga.py"),
    Path("algorithms/nearest_neighbor.py"),
    Path("algorithms/two_opt.py"),
    Path("core/random_generator.py"),
    Path("core/mathematics.py"),
    Path("core/sorting.py"),
    Path("core/tsp.py"),
    Path("core/utils.py"),
    Path("evaluation/statistics.py"),
]


class LibraryComplianceAuditTests(unittest.TestCase):
    def _parse_file(self, file_path: Path):
        self.assertTrue(file_path.exists(), f"File {file_path} does not exist")
        source = file_path.read_text(encoding="utf-8")
        return ast.parse(source, filename=str(file_path))

    def test_no_prohibited_imports(self):
        """Ensure no computational module imports prohibited libraries."""
        violations = []
        for file_path in COMPUTATIONAL_FILES:
            tree = self._parse_file(file_path)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        top_pkg = alias.name.split(".")[0].lower()
                        if top_pkg in PROHIBITED_MODULES:
                            violations.append(f"{file_path}:{node.lineno} imports '{alias.name}'")
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        top_pkg = node.module.split(".")[0].lower()
                        if top_pkg in PROHIBITED_MODULES:
                            violations.append(f"{file_path}:{node.lineno} imports from '{node.module}'")

        self.assertEqual(violations, [], f"Prohibited imports detected:\n" + "\n".join(violations))

    def test_no_prohibited_builtin_calls(self):
        """Ensure no computational module invokes prohibited built-in shortcuts (sum, min, max, sorted)."""
        violations = []
        for file_path in COMPUTATIONAL_FILES:
            # Skip checking function definitions of min/max if named min/max (none are named that, they are manual_min/manual_max)
            tree = self._parse_file(file_path)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    # Check direct function calls like sum(...) or min(...)
                    if isinstance(node.func, ast.Name):
                        if node.func.id in PROHIBITED_CALLS:
                            violations.append(f"{file_path}:{node.lineno} calls prohibited built-in '{node.func.id}()'")
                    # Check method calls like list.sort(...)
                    elif isinstance(node.func, ast.Attribute):
                        if node.func.attr == "sort":
                            violations.append(f"{file_path}:{node.lineno} calls prohibited method '.sort()'")

        self.assertEqual(violations, [], f"Prohibited built-in calls detected:\n" + "\n".join(violations))


if __name__ == "__main__":
    unittest.main()
