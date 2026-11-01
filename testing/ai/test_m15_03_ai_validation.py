"""Unit tests for M15-03 cross-artifact AI output validation."""
import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_ai_outputs import validate_frames


class M1503ValidationTests(unittest.TestCase):
    def setUp(self):
        self.forecasts = pd.DataFrame([
            ["2023-09-14", "S001", "P0001", 8.0, 10.0, 2.0],
            ["2023-09-14", "S001", "P0002", 10.0, 8.0, 2.0],
        ], columns=["Date", "Store ID", "Product ID", "Actual Units Sold", "Forecast Units Sold", "Absolute Error"])
        self.reorder = pd.DataFrame([
            ["2023-09-14", "S001", "P0001", 5, 10, 10, "REORDER_NOW", 3],
            ["2023-09-14", "S001", "P0002", 30, 8, 8, "HEALTHY", 0],
        ], columns=["Date", "Store ID", "Product ID", "Inventory Level", "Forecast Units Sold", "Demand Used for Recommendation", "recommendation_status", "suggested_order_quantity"])
        self.stockout = pd.DataFrame([
            ["2023-09-14", "S001", "P0001", 5, 10, 10, "STOCKOUT_RISK", 0.5],
            ["2023-09-14", "S001", "P0002", 30, 8, 8, "NO_STOCKOUT_RISK", 3.75],
        ], columns=["Date", "Store ID", "Product ID", "Inventory Level", "Forecast Units Sold", "Demand Used for Detection", "stockout_status", "days_of_cover"])
        self.evaluation = {
            "mae": 2, "rmse": 2, "test_rows": 2,
            "test_data_used_for_training": False,
            "model_retrained_during_evaluation": False,
        }
        self.forecast_summary = {
            "mae": 2, "rmse": 2, "forecast_rows": 2,
            "unique_forecast_dates": 1,
            "forecast_start_date": "2023-09-14",
            "forecast_end_date": "2023-09-14",
            "test_data_used_for_training": False,
            "model_retrained_during_forecasting": False,
        }
        self.reorder_summary = {
            "records_processed": 2,
            "status_counts": {"REORDER_NOW": 1, "HEALTHY": 1},
            "reorder_now_count": 1,
        }
        self.stockout_summary = {
            "records_processed": 2,
            "status_counts": {"STOCKOUT_RISK": 1, "NO_STOCKOUT_RISK": 1},
            "observed_stockout_count": 0,
            "stockout_risk_count": 1,
        }

    def run_validation(self):
        return validate_frames(
            self.forecasts, self.reorder, self.stockout,
            self.evaluation, self.forecast_summary,
            self.reorder_summary, self.stockout_summary,
        )

    def test_consistent_aligned_outputs_pass(self):
        result = self.run_validation()
        self.assertEqual(result["overall_status"], "PASS")
        self.assertEqual(result["metrics"]["mae"], 2.0)
        self.assertEqual(result["metrics"]["forecast_rows"], 2)

    def test_duplicate_forecast_key_fails(self):
        self.forecasts = pd.concat([self.forecasts, self.forecasts.iloc[[0]]], ignore_index=True)
        result = self.run_validation()
        check = next(x for x in result["checks"] if x["check"] == "forecast_business_keys_unique")
        self.assertEqual(check["status"], "FAIL")

    def test_reorder_key_mismatch_fails(self):
        self.reorder = self.reorder.iloc[[0]].copy()
        result = self.run_validation()
        check = next(x for x in result["checks"] if x["check"] == "reorder_forecast_key_alignment")
        self.assertEqual(check["status"], "FAIL")

    def test_negative_suggested_quantity_fails(self):
        self.reorder.loc[0, "suggested_order_quantity"] = -1
        result = self.run_validation()
        check = next(x for x in result["checks"] if x["check"] == "reorder_quantities_valid")
        self.assertEqual(check["status"], "FAIL")

    def test_single_status_concentration_is_warning(self):
        self.reorder["recommendation_status"] = "REORDER_NOW"
        self.reorder["suggested_order_quantity"] = [3, 5]
        self.reorder_summary = {
            "records_processed": 2,
            "status_counts": {"REORDER_NOW": 2},
            "reorder_now_count": 2,
        }
        self.stockout["stockout_status"] = "STOCKOUT_RISK"
        self.stockout_summary = {
            "records_processed": 2,
            "status_counts": {"STOCKOUT_RISK": 2},
            "observed_stockout_count": 0,
            "stockout_risk_count": 2,
        }
        result = self.run_validation()
        self.assertEqual(result["overall_status"], "PASS_WITH_WARNINGS")
        states = {x["check"]: x["status"] for x in result["checks"]}
        self.assertEqual(states["reorder_status_distribution"], "WARN")
        self.assertEqual(states["stockout_status_distribution"], "WARN")

    def test_metric_disagreement_fails(self):
        self.forecast_summary["mae"] = 99
        result = self.run_validation()
        check = next(x for x in result["checks"] if x["check"] == "forecast_metrics_recomputed")
        self.assertEqual(check["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
