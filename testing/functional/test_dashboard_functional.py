"""Functional tests for the RetailAI Streamlit dashboard."""

import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


class DashboardFunctionalTests(unittest.TestCase):

    def test_dashboard_loads_successfully(self):
        app = AppTest.from_file(str(Path(__file__).resolve().parents[2] / "app.py")).run(timeout=60)

        self.assertEqual(
            len(app.exception),
            0,
            f"Dashboard errors: {[e.message for e in app.exception]}"
        )

        titles = [element.value for element in app.title]
        self.assertIn("📦 RetailAI", titles)

    def test_all_dashboard_pages_load_successfully(self):
        expected_pages = [
            "Dashboard",
            "Sales Analysis",
            "AI Forecasting",
            "Smart Restocking",
            "Inventory Alerts",
            "AI Chatbot",
            "Model Performance",
        ]

        app = AppTest.from_file(str(Path(__file__).resolve().parents[2] / "app.py")).run(timeout=60)

        self.assertEqual(len(app.exception), 0)

        navigation = app.sidebar.radio[0]

        self.assertEqual(
            list(navigation.options),
            expected_pages
        )

        for page in expected_pages:
            app.sidebar.radio[0].set_value(page).run(timeout=60)

            self.assertEqual(
                len(app.exception),
                0,
                f"Page '{page}' errors: "
                f"{[e.message for e in app.exception]}"
            )


if __name__ == "__main__":
    unittest.main()

