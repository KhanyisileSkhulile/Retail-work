"""Focused M12-02 unit tests for reorder decision rules."""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RESTOCKING_DIR = REPO_ROOT / "python-ai" / "restocking"
sys.path.insert(0, str(RESTOCKING_DIR))

from reorder import calculate_reorder_recommendation  # noqa: E402


class ReorderRecommendationTests(unittest.TestCase):
    def test_stock_at_reorder_point_recommends_order(self):
        result = calculate_reorder_recommendation(20, 5)
        self.assertEqual(result["safety_stock"], 5)
        self.assertEqual(result["reorder_point"], 20)
        self.assertEqual(result["target_stock"], 25)
        self.assertEqual(result["suggested_order_quantity"], 5)
        self.assertEqual(result["recommendation_status"], "REORDER_NOW")

    def test_stock_below_reorder_point_recommends_order(self):
        result = calculate_reorder_recommendation(8, 5)
        self.assertEqual(result["suggested_order_quantity"], 17)
        self.assertEqual(result["recommendation_status"], "REORDER_NOW")

    def test_stock_between_reorder_point_and_target_is_watch(self):
        result = calculate_reorder_recommendation(22, 5)
        self.assertEqual(result["suggested_order_quantity"], 0)
        self.assertEqual(result["recommendation_status"], "WATCH")

    def test_stock_at_target_is_healthy(self):
        result = calculate_reorder_recommendation(25, 5)
        self.assertEqual(result["suggested_order_quantity"], 0)
        self.assertEqual(result["recommendation_status"], "HEALTHY")

    def test_missing_or_negative_stock_requires_data_review(self):
        self.assertEqual(
            calculate_reorder_recommendation(None, 5)["recommendation_status"],
            "DATA_REQUIRED",
        )
        self.assertEqual(
            calculate_reorder_recommendation(-1, 5)["recommendation_status"],
            "DATA_REQUIRED",
        )

    def test_missing_demand_is_flagged(self):
        result = calculate_reorder_recommendation(10, None)
        self.assertEqual(result["recommendation_status"], "INSUFFICIENT_HISTORY")
        self.assertIsNone(result["suggested_order_quantity"])

    def test_negative_forecast_is_treated_as_zero(self):
        result = calculate_reorder_recommendation(0, -10)
        self.assertEqual(result["safety_stock"], 0)
        self.assertEqual(result["reorder_point"], 0)
        self.assertEqual(result["target_stock"], 0)
        self.assertEqual(result["suggested_order_quantity"], 0)
        self.assertEqual(result["recommendation_status"], "REORDER_NOW")

    def test_negative_settings_are_rejected(self):
        with self.assertRaises(ValueError):
            calculate_reorder_recommendation(10, 2, lead_time_days=-1)


if __name__ == "__main__":
    unittest.main()
