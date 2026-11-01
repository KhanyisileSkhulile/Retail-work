
"""Integration tests for the RetailAI Python-to-SQLite data pipeline."""

import csv
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


# Locate the project and database service.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_SERVICE_DIR = (
    PROJECT_ROOT / "application" / "backend" / "database"
)

if str(DATABASE_SERVICE_DIR) not in sys.path:
    sys.path.insert(0, str(DATABASE_SERVICE_DIR))

import service


class DatabasePipelineIntegrationTests(unittest.TestCase):

    def setUp(self):
        # Use a temporary database so the real project database
        # is never changed by these tests.
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        self.temp_path = Path(self.temp_dir.name)
        self.csv_path = self.temp_path / "test_inventory.csv"
        self.database_path = self.temp_path / "test_inventory.db"

        patchers = [
            patch.object(service, "DATABASE_DIR", self.temp_path),
            patch.object(service, "DATABASE_PATH", self.database_path),
            patch.object(
                service,
                "SCHEMA_PATH",
                PROJECT_ROOT / "database" / "sqlite_schema.sql",
            ),
        ]

        for patcher in patchers:
            patcher.start()
            self.addCleanup(patcher.stop)

    @staticmethod
    def valid_rows():
        """Return a small valid dataset for integration testing."""

        return [
            {
                "Date": "2025-01-01",
                "Store ID": "S001",
                "Product ID": "P0001",
                "Category": "Groceries",
                "Region": "North",
                "Inventory Level": 10,
                "Units Sold": 2,
                "Units Ordered": 5,
                "Demand Forecast": -1.25,
                "Price": 10.50,
                "Discount": 5,
                "Weather Condition": "Sunny",
                "Holiday/Promotion": 0,
                "Competitor Pricing": 9.99,
                "Seasonality": "Summer",
            },
            {
                "Date": "2025-01-02",
                "Store ID": "S002",
                "Product ID": "P0002",
                "Category": "Toys",
                "Region": "South",
                "Inventory Level": 20,
                "Units Sold": 3,
                "Units Ordered": 4,
                "Demand Forecast": 4.50,
                "Price": 15.00,
                "Discount": 10,
                "Weather Condition": "Rainy",
                "Holiday/Promotion": 1,
                "Competitor Pricing": 14.50,
                "Seasonality": "Winter",
            },
        ]

    def write_dataset(self, rows=None, columns=None):
        """Write a test CSV file."""

        if rows is None:
            rows = self.valid_rows()

        if columns is None:
            columns = service.EXPECTED_COLUMNS

        with self.csv_path.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=columns,
            )

            writer.writeheader()

            for row in rows:
                writer.writerow({
                    key: value
                    for key, value in row.items()
                    if key in columns
                })

        return self.csv_path

    def test_imports_records_into_sqlite(self):
        """Verify that CSV records are imported correctly."""

        self.write_dataset()

        imported = service.initialize_database(
            csv_path=self.csv_path
        )

        summary = service.get_inventory_summary()

        self.assertEqual(imported, 2)
        self.assertEqual(summary["records"], 2)
        self.assertEqual(summary["stores"], 2)
        self.assertEqual(summary["products"], 2)
        self.assertEqual(summary["categories"], 2)

        # Negative demand forecasts are allowed by the supplied dataset.
        with service.get_connection() as connection:
            forecasts = connection.execute(
                "SELECT demand_forecast FROM inventory_records"
            ).fetchall()

        self.assertIn((-1.25,), forecasts)

    def test_unchanged_dataset_does_not_require_reimport(self):
        """Verify that unchanged data uses the existing import."""

        self.write_dataset()

        first_import = service.initialize_database(
            csv_path=self.csv_path
        )

        # If the second call attempts to read the CSV again,
        # the test fails.
        with patch.object(
            service.pd,
            "read_csv",
            side_effect=AssertionError(
                "Unchanged dataset should not be reimported."
            ),
        ):
            second_import = service.initialize_database(
                csv_path=self.csv_path
            )

        self.assertEqual(first_import, 2)
        self.assertEqual(second_import, 2)

    def test_missing_required_column_is_rejected(self):
        """Verify that CSV files missing required columns are rejected."""

        columns = [
            column
            for column in service.EXPECTED_COLUMNS
            if column != "Seasonality"
        ]

        self.write_dataset(columns=columns)

        with self.assertRaisesRegex(
            ValueError,
            "missing required columns",
        ):
            service.initialize_database(
                csv_path=self.csv_path
            )

    def test_invalid_inventory_does_not_replace_existing_records(self):
        """Verify that an invalid reload preserves existing database data."""

        self.write_dataset()

        service.initialize_database(
            csv_path=self.csv_path
        )

        invalid_rows = self.valid_rows()
        invalid_rows[0]["Inventory Level"] = -5

        self.write_dataset(rows=invalid_rows)

        with self.assertRaisesRegex(
            ValueError,
            "non-negative whole numbers",
        ):
            service.initialize_database(
                force_reload=True,
                csv_path=self.csv_path,
            )

        # The original two records must still exist.
        summary = service.get_inventory_summary()

        self.assertEqual(summary["records"], 2)


if __name__ == "__main__":
    unittest.main()
