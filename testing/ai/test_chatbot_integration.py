import sys
import unittest
from pathlib import Path
from unittest.mock import patch

CHATBOT_DIR = Path(__file__).resolve().parents[2] / "python-ai" / "chatbot"
sys.path.insert(0, str(CHATBOT_DIR))
import integration


class ChatbotIntegrationTests(unittest.TestCase):
    def test_greeting_does_not_require_data_files(self):
        result = integration.process_project_message("Hello RetailAI")
        self.assertEqual(result["intent"], "GREETING")
        self.assertEqual(result["integration"]["mode"], "assistant_only")
        self.assertFalse(result["integration"]["live_data_connected"])

    def test_missing_inventory_source_is_reported(self):
        availability = {"inventory": {"available": False}}
        with patch.object(integration.queries, "data_availability", return_value=availability):
            result = integration.process_project_message("Show sales for S001")
        self.assertTrue(result["needs_clarification"])
        self.assertIn("not available yet", result["response"])
        self.assertFalse(result["integration"]["source_available"])

    def test_forecast_uses_forecast_source(self):
        availability = {"forecast": {"available": False}}
        with patch.object(integration.queries, "data_availability", return_value=availability):
            result = integration.process_project_message("Forecast for S001 P0001")
        self.assertEqual(result["integration"]["source"], "forecast")
        self.assertIn("forecast project data file", result["response"])

    def test_reorder_uses_reorder_source(self):
        availability = {"reorder": {"available": False}}
        with patch.object(integration.queries, "data_availability", return_value=availability):
            result = integration.process_project_message("Reorder for S001 P0001")
        self.assertEqual(result["integration"]["source"], "reorder")

    def test_stockout_uses_stockout_source(self):
        availability = {"stockout": {"available": False}}
        with patch.object(integration.queries, "data_availability", return_value=availability):
            result = integration.process_project_message("Stockout status S001 P0001")
        self.assertEqual(result["integration"]["source"], "stockout")

    def test_available_source_routes_to_assistant(self):
        availability = {"inventory": {"available": True, "records": 73100,
                                      "date_start": "2023-01-01", "date_end": "2024-01-01"}}
        expected = {"intent": "SALES_SUMMARY", "slots": {"store_id": "S001"},
                    "needs_clarification": False, "data": {"units_sold": 23},
                    "response": "Historical sales summary: 23 observed units."}
        with patch.object(integration.queries, "data_availability", return_value=availability), \
             patch.object(integration.assistant, "process_message", return_value=expected.copy()) as routed:
            result = integration.process_project_message("Show sales for S001")
        routed.assert_called_once()
        self.assertTrue(result["integration"]["source_available"])
        self.assertEqual(result["integration"]["source_records"], 73100)

    def test_real_inventory_data_answer_when_prepared(self):
        source = integration.queries.SOURCES["inventory"]
        path = integration.queries.REPO_ROOT / source
        if not path.exists():
            self.skipTest("Run the approved dataset preparation pipeline first; cleaned inventory file is missing.")
        import pandas as pd
        df = pd.read_csv(path, usecols=["Store ID", "Product ID"])
        if df.empty:
            self.skipTest("Prepared inventory data contains no rows.")
        row = df.iloc[0]
        message = f"Show sales for {row['Store ID']} {row['Product ID']}"
        result = integration.process_project_message(message)
        self.assertEqual(result["intent"], "SALES_SUMMARY")
        self.assertTrue(result["integration"]["source_available"])
        self.assertFalse(result["integration"]["live_data_connected"])
        self.assertIn("Historical sales summary", result["response"])


if __name__ == "__main__":
    unittest.main()
