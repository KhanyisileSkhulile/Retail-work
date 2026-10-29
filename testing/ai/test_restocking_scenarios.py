"""M12-05: Validation scenarios for restocking logic and assumptions."""

import sys
import unittest
from pathlib import Path

# Setup path to import the restocking modules
REPO_ROOT = Path(__file__).resolve().parents[2]
RESTOCKING_DIR = REPO_ROOT / "python-ai" / "restocking"
sys.path.insert(0, str(RESTOCKING_DIR))

from reorder import calculate_reorder_recommendation
from stockout import detect_stockout

class RestockingValidationTests(unittest.TestCase):
    """Validate the scenarios outlined in the M12-01 baseline assumptions."""

    def test_scenario_1_stock_above_reorder_point(self):
        """Stock is above reorder point: No order (WATCH or HEALTHY)."""
        # Demand 5 -> safety 5, reorder point 20, target 25.
        # Stock 22 is above reorder point, so WATCH.
        result = calculate_reorder_recommendation(22, 5)
        self.assertEqual(result["recommendation_status"], "WATCH")
        self.assertEqual(result["suggested_order_quantity"], 0)

    def test_scenario_2_stock_equals_reorder_point(self):
        """Stock equals reorder point: REORDER_NOW; order up to target."""
        # Demand 5 -> safety 5, reorder point 20, target 25.
        result = calculate_reorder_recommendation(20, 5)
        self.assertEqual(result["recommendation_status"], "REORDER_NOW")
        self.assertEqual(result["suggested_order_quantity"], 5)

    def test_scenario_3_stock_below_reorder_point(self):
        """Stock is below reorder point: REORDER_NOW; positive quantity."""
        # Demand 5 -> safety 5, reorder point 20, target 25.
        result = calculate_reorder_recommendation(8, 5)
        self.assertEqual(result["recommendation_status"], "REORDER_NOW")
        self.assertEqual(result["suggested_order_quantity"], 17)

    def test_scenario_4_forecast_is_negative(self):
        """Forecast is negative: Use zero demand and record the normalization."""
        result = calculate_reorder_recommendation(0, -10)
        self.assertEqual(result["safety_stock"], 0)
        self.assertEqual(result["reorder_point"], 0)
        self.assertEqual(result["suggested_order_quantity"], 0)
        self.assertEqual(result["recommendation_status"], "REORDER_NOW")

    def test_scenario_5_stock_missing_or_invalid(self):
        """Stock is missing/invalid: DATA_REQUIRED; no numeric recommendation."""
        result = calculate_reorder_recommendation(None, 5)
        self.assertEqual(result["recommendation_status"], "DATA_REQUIRED")
        self.assertIsNone(result["suggested_order_quantity"])

        result = calculate_reorder_recommendation(-5, 5)
        self.assertEqual(result["recommendation_status"], "DATA_REQUIRED")

    def test_scenario_6_forecast_missing(self):
        """Forecast missing but no fallback logic: INSUFFICIENT_HISTORY."""
        # The function itself only takes the demand value, so passing None
        # simulates that neither a model forecast nor a fallback was available.
        result = calculate_reorder_recommendation(10, None)
        self.assertEqual(result["recommendation_status"], "INSUFFICIENT_HISTORY")
        self.assertIsNone(result["suggested_order_quantity"])

    def test_scenario_7_same_product_two_stores(self):
        """Same product in two stores: Calculate independently."""
        # We simulate this by running calculations with different inputs
        # and verifying the statuses are distinct.
        store_a_result = calculate_reorder_recommendation(15, 5)  # REORDER_NOW
        store_b_result = calculate_reorder_recommendation(30, 5)  # HEALTHY

        self.assertEqual(store_a_result["recommendation_status"], "REORDER_NOW")
        self.assertEqual(store_b_result["recommendation_status"], "HEALTHY")

    def test_scenario_8_stockout_detection_zero_stock(self):
        """Stockout detection: On-hand inventory zero."""
        result = detect_stockout(0, 5)
        self.assertEqual(result["stockout_status"], "STOCKOUT")

    def test_scenario_9_stockout_detection_risk(self):
        """Stockout detection: Positive stock at/below reorder point."""
        result = detect_stockout(15, 5) # Demand 5 -> Reorder point 20
        self.assertEqual(result["stockout_status"], "STOCKOUT_RISK")

if __name__ == "__main__":
    unittest.main()