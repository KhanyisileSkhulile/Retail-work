import sys
import unittest
from pathlib import Path
from unittest.mock import patch

CHATBOT_DIR = Path(__file__).resolve().parents[2] / "python-ai" / "chatbot"
sys.path.insert(0, str(CHATBOT_DIR))
import assistant


class AssistantServiceTests(unittest.TestCase):
    def test_greeting(self):
        result = assistant.process_message("Hello RetailAI")
        self.assertEqual(result["intent"], "GREETING")
        self.assertIn("Hello", result["response"])

    def test_help(self):
        result = assistant.process_message("What can you help me with?")
        self.assertEqual(result["intent"], "HELP")
        self.assertIn("historical", result["response"])

    def test_unknown_message(self):
        result = assistant.process_message("Tell me a joke")
        self.assertEqual(result["intent"], "UNKNOWN")
        self.assertTrue(result["needs_clarification"])

    def test_classify_forecast(self):
        self.assertEqual(assistant.classify_intent("Show forecast for S001 P0001"), "DEMAND_FORECAST")

    def test_classify_reorder(self):
        self.assertEqual(assistant.classify_intent("What should S001 reorder for P0001?"), "REORDER_RECOMMENDATION")

    def test_extract_slots(self):
        slots = assistant.extract_slots("Top 8 products at s001 from 2023-09-14 to 2023-10-01")
        self.assertEqual(slots["store_id"], "S001")
        self.assertEqual(slots["start_date"], "2023-09-14")
        self.assertEqual(slots["end_date"], "2023-10-01")
        self.assertEqual(slots["limit"], 8)

    def test_extract_factor(self):
        self.assertEqual(assistant.extract_slots("Compare sales during promotions")["factor"], "promotion")

    def test_forecast_clarification(self):
        result = assistant.process_message("Show me the demand forecast")
        self.assertTrue(result["needs_clarification"])
        self.assertIn("store ID and a product ID", result["response"])

    def test_factor_clarification(self):
        result = assistant.process_message("Compare sales factors")
        self.assertTrue(result["needs_clarification"])
        self.assertIn("weather, promotion", result["response"])

    def test_inventory_clarification(self):
        result = assistant.process_message("Show inventory")
        self.assertTrue(result["needs_clarification"])

    def test_sales_summary_query(self):
        fake = {"records": 2, "units_sold": 15, "date_start": "2023-09-14", "date_end": "2023-09-15"}
        with patch.object(assistant.queries, "sales_summary", return_value=fake):
            result = assistant.process_message("Show sales for S001")
        self.assertEqual(result["intent"], "SALES_SUMMARY")
        self.assertIn("15 observed units", result["response"])

    def test_query_error(self):
        with patch.object(assistant.queries, "sales_summary",
                          side_effect=assistant.queries.QueryDataError("source missing")):
            result = assistant.process_message("Show sales for S001")
        self.assertTrue(result["needs_clarification"])
        self.assertIn("source missing", result["response"])

    def test_data_availability_disclaims_live(self):
        fake = {"inventory": {"available": True, "records": 10}, "live_data_connected": False}
        with patch.object(assistant.queries, "data_availability", return_value=fake):
            result = assistant.process_message("What data is available?")
        self.assertIn("Live store data connected: no", result["response"])

    def test_stockout_response_warns_about_risk(self):
        import pandas as pd
        frame = pd.DataFrame([{"Date": pd.Timestamp("2023-09-14"), "Store ID": "S001",
            "Product ID": "P0001", "stockout_status": "STOCKOUT_RISK", "days_of_cover": 1.2}])
        with patch.object(assistant.queries, "stockout_status", return_value=frame):
            result = assistant.process_message("Check stockout status for S001 P0001")
        self.assertIn("not proof", result["response"])

    def test_forecast_is_labelled_historical(self):
        import pandas as pd
        frame = pd.DataFrame([{"Date": pd.Timestamp("2023-09-14"), "Store ID": "S001",
            "Product ID": "P0001", "Actual Units Sold": 5, "Forecast Units Sold": 6.5}])
        with patch.object(assistant.queries, "demand_forecast", return_value=frame):
            result = assistant.process_message("Forecast for S001 P0001")
        self.assertIn("not a new future or live forecast", result["response"])


if __name__ == "__main__":
    unittest.main()
