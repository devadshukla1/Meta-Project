"""Fast Streamlit interaction regression checks without a browser."""

import unittest

from streamlit.testing.v1 import AppTest


class DashboardIntegrationTests(unittest.TestCase):
    def test_navigation_and_hybrid_controls(self):
        app = AppTest.from_file("app.py", default_timeout=30).run()
        self.assertFalse(app.exception)
        for page in ("Dataset Explorer", "About the Project", "Route Optimization"):
            app.sidebar.radio[0].set_value(page).run()
            self.assertFalse(app.exception)
        app.selectbox[0].set_value("Hybrid Genetic Algorithm + 2-Opt").run()
        self.assertIn("2-Opt application rate", [slider.label for slider in app.slider])
        app.number_input[0].set_value(6)
        app.number_input[1].set_value(2)
        app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["latest_optimization_result"]["name"],
                         "Hybrid Genetic Algorithm + 2-Opt")

    def test_invalid_combination_is_reported(self):
        app = AppTest.from_file("app.py", default_timeout=30).run()
        app.sidebar.radio[0].set_value("Route Optimization").run()
        app.selectbox[0].set_value("Standard Genetic Algorithm").run()
        app.number_input[0].set_value(2)
        app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertTrue(any("tournament_size" in error.value for error in app.error))

    def test_dataset_explorer_renders_distance_matrix_without_exception(self):
        """Regression test: navigate to Dataset Explorer, ensure no exceptions and matrix renders."""
        app = AppTest.from_file("app.py", default_timeout=30).run()
        self.assertFalse(app.exception)
        app.sidebar.radio[0].set_value("Dataset Explorer").run()
        self.assertFalse(app.exception, f"Dataset Explorer raised exceptions: {[e.value for e in app.exception]}")
        self.assertEqual(len(app.dataframe), 1, "Distance matrix dataframe should be rendered")
        matrix_df = app.dataframe[0].value
        self.assertEqual(len(matrix_df), 20, "Distance matrix should have 20 rows")
        self.assertEqual(len(matrix_df.columns), 20, "Distance matrix should have 20 columns")
        # Check download buttons on Dataset Explorer
        download_buttons = app.get("download_button")
        labels = [btn.proto.label.lower() for btn in download_buttons]
        self.assertTrue(any("locations" in label for label in labels))
        self.assertTrue(any("distance matrix" in label for label in labels))

    def test_algorithm_comparison_quick_mode_only(self):
        """Verify Algorithm Comparison runs Quick Comparison for all three algorithms without Statistical Benchmark."""
        app = AppTest.from_file("app.py", default_timeout=30).run()
        app.sidebar.radio[0].set_value("Algorithm Comparison").run()
        self.assertFalse(app.exception)

        # Ensure no Mode radio (only the sidebar navigation radio exists)
        self.assertEqual(len(app.radio), 1)

        # Ensure Runs and Base seed are not present, and single Seed is present
        number_labels = [ni.label for ni in app.number_input]
        self.assertNotIn("Runs", number_labels)
        self.assertNotIn("Base seed", number_labels)
        self.assertIn("Seed", number_labels)

        # Configure small run and execute Run Comparison
        app.number_input[0].set_value(10)  # Population size
        app.number_input[1].set_value(5)   # Generations
        app.button[0].click().run()
        self.assertFalse(app.exception)

        latest = app.session_state["latest_comparison"]
        self.assertEqual(len(latest["runs"]), 3)
        self.assertEqual(
            [run["name"] for run in latest["runs"]],
            ["Nearest Neighbor", "Standard Genetic Algorithm", "Hybrid Genetic Algorithm + 2-Opt"],
        )
        download_labels = [btn.proto.label for btn in app.get("download_button")]
        self.assertIn("Download comparison CSV", download_labels)
        self.assertNotIn("Download benchmark runs CSV", download_labels)
        self.assertNotIn("Download summary CSV", download_labels)


if __name__ == "__main__":
    unittest.main()
