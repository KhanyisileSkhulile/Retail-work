"""M12-03 tests for observed stockouts and demand-based stockout risk."""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RESTOCKING_DIR = REPO_ROOT / "python-ai" / "restocking"
sys.path.insert(0, str(RESTOCKING_DIR))

from stockout import detect_stockout, build_stockout_detections  # noqa: E402


class StockoutDetectionTests(unittest.TestCase):
    def test_zero_stock_is_observed_stockout_even_without_demand(self):
        result = detect_stockout(0, None)
        self.assertEqual(result["stockout_status"], "STOCKOUT")
        self.assertEqual(result["days_of_cover"], 0.0)

    def test_stock_at_reorder_point_is_stockout_risk(self):
        # Demand 5, safety stock 5, reorder point 20.
        result = detect_stockout(20, 5)
        self.assertEqual(result["reorder_point"], 20)
        self.assertEqual(result["stockout_status"], "STOCKOUT_RISK")

    def test_stock_below_reorder_point_is_stockout_risk(self):
        result = detect_stockout(8, 5)
        self.assertEqual(result["stockout_status"], "STOCKOUT_RISK")

    def test_stock_between_reorder_point_and_target_is_watch(self):
        result = detect_stockout(22, 5)
        self.assertEqual(result["target_stock"], 25)
        self.assertEqual(result["stockout_status"], "WATCH")

    def test_stock_at_target_is_not_flagged_as_risk(self):
        result = detect_stockout(25, 5)
        self.assertEqual(result["stockout_status"], "NO_STOCKOUT_RISK")

    def test_missing_or_negative_stock_requires_data_review(self):
        self.assertEqual(detect_stockout(None, 5)["stockout_status"], "DATA_REQUIRED")
        self.assertEqual(detect_stockout(-1, 5)["stockout_status"], "DATA_REQUIRED")

    def test_missing_demand_with_positive_stock_is_insufficient_history(self):
        result = detect_stockout(10, None)
        self.assertEqual(result["stockout_status"], "INSUFFICIENT_HISTORY")
        self.assertIsNone(result["reorder_point"])

    def test_negative_demand_is_normalized_to_zero(self):
        result = detect_stockout(5, -10)
        self.assertEqual(result["safety_stock"], 0)
        self.assertEqual(result["reorder_point"], 0)
        self.assertEqual(result["stockout_status"], "NO_STOCKOUT_RISK")

    def test_zero_demand_and_zero_stock_is_still_stockout(self):
        self.assertEqual(detect_stockout(0, 0)["stockout_status"], "STOCKOUT")

    def test_negative_settings_are_rejected(self):
        with self.assertRaises(ValueError):
            detect_stockout(10, 2, lead_time_days=-1)

    def test_infinite_settings_are_rejected(self):
        with self.assertRaises(ValueError):
            detect_stockout(10, 2, safety_stock_days=float("inf"))

    def test_build_detects_forecast_and_stockout_rows_separately_by_product(self):
        import pandas as pd

        inventory = pd.DataFrame([
            {"Date": "2024-01-01", "Store ID": "S1", "Product ID": "P1", "Inventory Level": 0, "Units Sold": 3},
            {"Date": "2024-01-01", "Store ID": "S1", "Product ID": "P2", "Inventory Level": 100, "Units Sold": 2},
        ])
        forecasts = pd.DataFrame([
            {"Date": "2024-01-01", "Store ID": "S1", "Product ID": "P1", "Forecast Units Sold": 4},
            {"Date": "2024-01-01", "Store ID": "S1", "Product ID": "P2", "Forecast Units Sold": 2},
        ])
        results = build_stockout_detections(inventory, forecasts).set_index("Product ID")
        self.assertEqual(results.loc["P1", "stockout_status"], "STOCKOUT")
        self.assertEqual(results.loc["P2", "stockout_status"], "NO_STOCKOUT_RISK")
        self.assertEqual(len(results), 2)

    def test_duplicate_inventory_keys_are_rejected(self):
        import pandas as pd

        row = {"Date": "2024-01-01", "Store ID": "S1", "Product ID": "P1", "Inventory Level": 3, "Units Sold": 1}
        inventory = pd.DataFrame([row, row])
        forecasts = pd.DataFrame([{"Date": "2024-01-01", "Store ID": "S1", "Product ID": "P1", "Forecast Units Sold": 1}])
        with self.assertRaises(ValueError):
            build_stockout_detections(inventory, forecasts)

    def test_duplicate_forecast_keys_are_rejected(self):
        import pandas as pd

        inventory = pd.DataFrame([{"Date": "2024-01-01", "Store ID": "S1", "Product ID": "P1", "Inventory Level": 3, "Units Sold": 1}])
        forecast = {"Date": "2024-01-01", "Store ID": "S1", "Product ID": "P1", "Forecast Units Sold": 1}
        with self.assertRaises(ValueError):
            build_stockout_detections(inventory, pd.DataFrame([forecast, forecast]))


if __name__ == "__main__":
    unittest.main()
