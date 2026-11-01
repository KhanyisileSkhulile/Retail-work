"""M15-06 integration tests for Retail-X-AI services."""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "application" / "backend"))

from database import service as db_service
from application.backend.forecasts import service as forecast_service
from recommendations import service as restocking_service


class PerformanceIntegrationTests(unittest.TestCase):

    def test_database_inventory_integration(self):
        summary = db_service.get_inventory_summary()

        self.assertGreater(summary["records"], 0)
        self.assertGreater(summary["stores"], 0)
        self.assertGreater(summary["products"], 0)
        self.assertGreater(summary["categories"], 0)

    def test_forecast_csv_and_metadata_integration(self):
        forecasts = forecast_service.load_forecasts()
        metadata = forecast_service.load_forecast_metadata()

        forecast_service.validate_forecast_metadata(
            forecasts, metadata
        )

        self.assertGreater(len(forecasts), 0)
        self.assertGreater(forecasts["Date"].nunique(), 0)

    def test_complete_restocking_integration(self):
        result = restocking_service.get_restocking_recommendations()

        self.assertTrue(result["success"])
        self.assertEqual(
            result["data_classification"], "HISTORICAL_DATA"
        )
        self.assertGreater(result["record_count"], 0)
        self.assertEqual(
            result["record_count"], len(result["recommendations"])
        )

        for record in result["recommendations"]:
            self.assertIn("reorder_recommendation", record)
            self.assertIn("stockout_status", record)

        json.dumps(result, allow_nan=False)

    def test_forecast_and_inventory_data_are_available(self):
        forecasts = forecast_service.load_forecasts()
        inventory = db_service.get_inventory_summary()

        self.assertGreater(len(forecasts), 0)
        self.assertGreater(inventory["records"], 0)


if __name__ == "__main__":
    unittest.main()
