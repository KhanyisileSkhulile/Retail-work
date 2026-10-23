"""Regression tests for M11-02 demand-history feature engineering."""
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

FORECASTING_DIR = Path(__file__).resolve().parents[1] / "forecasting"
sys.path.insert(0, str(FORECASTING_DIR))

from feature_engineering import (  # noqa: E402
    DEMAND_HISTORY_COLUMNS,
    add_demand_history_features,
    prepare_forecasting_data,
    prepare_forecasting_train_validation_test,
)


def sample_data(days=40):
    rows = []
    dates = pd.date_range("2024-01-01", periods=days, freq="D")
    for day, date in enumerate(dates):
        for store, base in (("S1", 0), ("S2", 100)):
            rows.append({
                "Date": date,
                "Store ID": store,
                "Product ID": "P1",
                "Category": "Grocery",
                "Region": "North",
                "Weather Condition": "Sunny",
                "Seasonality": "Regular",
                "Price": 10.0,
                "Discount": 0.0,
                "Competitor Pricing": 10.5,
                "Holiday/Promotion": 0,
                "Units Sold": base + day + 1,
                "Demand Forecast": 9999,
                "Units Ordered": 8888,
                "Inventory Level": 7777,
            })
    return pd.DataFrame(rows)


class DemandHistoryFeatureTests(unittest.TestCase):
    def test_lags_and_rolling_means_use_prior_observations(self):
        result = add_demand_history_features(sample_data())
        row = result.loc[
            (result["Store ID"] == "S1")
            & (result["Product ID"] == "P1")
            & (result["Date"] == pd.Timestamp("2024-01-21"))
        ].iloc[0]
        self.assertEqual(row["Units Sold"], 21)
        self.assertEqual(row["demand_lag_1"], 20)
        self.assertEqual(row["demand_lag_7"], 14)
        self.assertEqual(row["demand_lag_14"], 7)
        self.assertAlmostEqual(row["demand_rolling_mean_7"], 17.0)
        self.assertAlmostEqual(row["demand_rolling_mean_28"], 10.5)

    def test_demand_history_does_not_mix_store_product_series(self):
        result = add_demand_history_features(sample_data())
        row = result.loc[
            (result["Store ID"] == "S2")
            & (result["Product ID"] == "P1")
            & (result["Date"] == pd.Timestamp("2024-01-21"))
        ].iloc[0]
        self.assertEqual(row["demand_lag_1"], 120)
        self.assertAlmostEqual(row["demand_rolling_mean_7"], 117.0)

    def test_current_target_does_not_change_its_own_history_features(self):
        original = sample_data()
        changed = original.copy()
        target = (
            (changed["Store ID"] == "S1")
            & (changed["Date"] == pd.Timestamp("2024-01-21"))
        )
        changed.loc[target, "Units Sold"] += 5000
        before = add_demand_history_features(original)
        after = add_demand_history_features(changed)
        key = (
            (before["Store ID"] == "S1")
            & (before["Date"] == pd.Timestamp("2024-01-21"))
        )
        for column in DEMAND_HISTORY_COLUMNS:
            self.assertEqual(before.loc[key, column].iloc[0], after.loc[key, column].iloc[0])

    def test_prepared_features_are_numeric_finite_and_exclude_leakage_columns(self):
        train, test, prepared, metadata = prepare_forecasting_data(
            sample_data(), train_fraction=0.7
        )
        self.assertTrue((train["Date"].max() < test["Date"].min()))
        self.assertTrue(set(DEMAND_HISTORY_COLUMNS).issubset(metadata["feature_columns"]))
        self.assertFalse({"Demand Forecast", "Units Ordered", "Inventory Level"}.intersection(prepared.columns))
        numeric = prepared.drop(columns=["Date", "Units Sold"])
        self.assertTrue(np.isfinite(numeric.to_numpy(dtype=float)).all())

    def test_three_way_split_is_chronological(self):
        train, validation, test, prepared, metadata = (
            prepare_forecasting_train_validation_test(
                sample_data(), train_fraction=0.7, validation_fraction=0.15
            )
        )
        self.assertLess(train["Date"].max(), validation["Date"].min())
        self.assertLess(validation["Date"].max(), test["Date"].min())
        self.assertEqual(len(prepared), len(sample_data()))
        self.assertEqual(
            len(train) + len(validation) + len(test), len(sample_data())
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
