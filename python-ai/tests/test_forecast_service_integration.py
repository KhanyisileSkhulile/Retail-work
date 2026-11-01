"""Tests for M14-03 application demand forecast integration."""

import math
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import by package path so this test cannot collide with the database
# integration test's separate module also named "service".
from application.backend.forecasts import service


class ForecastServiceIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.temp_path = Path(self.temp_dir.name)
        self.csv_path = self.temp_path / "forecasts.csv"

        self.frame = pd.DataFrame([
            {
                "Date": "2023-09-14",
                "Store ID": "S001",
                "Product ID": "P0001",
                "Actual Units Sold": 10.0,
                "Forecast Units Sold": 12.0,
                "Absolute Error": 2.0,
            },
            {
                "Date": "2023-09-14",
                "Store ID": "S001",
                "Product ID": "P0002",
                "Actual Units Sold": 8.0,
                "Forecast Units Sold": 6.0,
                "Absolute Error": 2.0,
            },
            {
                "Date": "2023-09-15",
                "Store ID": "S002",
                "Product ID": "P0001",
                "Actual Units Sold": 5.0,
                "Forecast Units Sold": 4.0,
                "Absolute Error": 1.0,
            },
        ])

    def write_csv(self, frame=None):
        (frame if frame is not None else self.frame).to_csv(
            self.csv_path,
            index=False,
        )
        return self.csv_path

    def test_loads_and_validates_forecast_csv(self):
        self.write_csv()
        loaded = service.load_forecasts(self.csv_path)

        self.assertEqual(len(loaded), 3)
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(loaded["Date"]))
        self.assertEqual(loaded.iloc[0]["Store ID"], "S001")

    def test_filters_by_store_product_and_inclusive_dates(self):
        self.write_csv()
        loaded = service.load_forecasts(self.csv_path)

        filtered = service.filter_forecasts(
            loaded,
            store_id="S001",
            product_id="P0002",
            start_date="2023-09-14",
            end_date="2023-09-14",
        )

        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered.iloc[0]["Product ID"], "P0002")

    def test_summary_and_daily_aggregation(self):
        self.write_csv()
        loaded = service.load_forecasts(self.csv_path)

        summary = service.summarize_forecasts(loaded)
        daily = service.build_daily_summary(loaded)

        self.assertEqual(summary["records"], 3)
        self.assertEqual(summary["stores"], 2)
        self.assertEqual(summary["products"], 2)
        self.assertAlmostEqual(summary["mae"], 5 / 3)
        self.assertAlmostEqual(summary["rmse"], math.sqrt(3))
        self.assertEqual(len(daily), 2)
        self.assertEqual(int(daily.iloc[0]["Forecast Rows"]), 2)

    def test_rejects_missing_required_columns(self):
        self.write_csv(self.frame.drop(columns=["Absolute Error"]))

        with self.assertRaisesRegex(ValueError, "missing required columns"):
            service.load_forecasts(self.csv_path)

    def test_rejects_duplicate_date_store_product_rows(self):
        duplicated = pd.concat(
            [self.frame, self.frame.iloc[[0]]],
            ignore_index=True,
        )
        self.write_csv(duplicated)

        with self.assertRaisesRegex(ValueError, "duplicate"):
            service.load_forecasts(self.csv_path)

    def test_rejects_incorrect_absolute_error(self):
        invalid = self.frame.copy()
        invalid.loc[0, "Absolute Error"] = 999
        self.write_csv(invalid)

        with self.assertRaisesRegex(ValueError, "do not match"):
            service.load_forecasts(self.csv_path)

    def test_rejects_invalid_date_range(self):
        self.write_csv()
        loaded = service.load_forecasts(self.csv_path)

        with self.assertRaisesRegex(ValueError, "Start date"):
            service.filter_forecasts(
                loaded,
                start_date="2023-09-15",
                end_date="2023-09-14",
            )

    def test_validates_metadata_against_forecast_csv(self):
        self.write_csv()
        loaded = service.load_forecasts(self.csv_path)
        summary = service.summarize_forecasts(loaded)
        metadata = {
            "model_name": "Ridge Regression",
            "forecast_rows": 3,
            "unique_forecast_dates": 2,
            "forecast_start_date": "2023-09-14",
            "forecast_end_date": "2023-09-15",
            "mae": summary["mae"],
            "rmse": summary["rmse"],
        }

        service.validate_forecast_metadata(loaded, metadata)

        metadata["forecast_rows"] = 4
        with self.assertRaisesRegex(ValueError, "row count"):
            service.validate_forecast_metadata(loaded, metadata)


if __name__ == "__main__":
    unittest.main()
