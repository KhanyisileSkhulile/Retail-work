from pathlib import Path
import sys
from collections import Counter

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]
RESTOCKING_PATH = PROJECT_ROOT / "python-ai" / "restocking"
BACKEND_PATH = PROJECT_ROOT / "application" / "backend"
FORECAST_PATH = (
    PROJECT_ROOT
    / "python-ai"
    / "forecasting"
    / "outputs"
    / "retail_demand_forecasts_m11_06.csv"
)

for path in (RESTOCKING_PATH, BACKEND_PATH):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import reorder
import stockout
from database import service as db_service


def _clean_value(value):
    """Convert pandas/numpy values into JSON-friendly Python values."""
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value


def get_restocking_recommendations():
    """
    Integrate saved forecasts, historical inventory and existing
    reorder/stockout engines for the latest matching dataset date.

    Results are advisory and represent historical data, not live stock.
    """
    if not FORECAST_PATH.exists():
        raise FileNotFoundError(f"Forecast file not found: {FORECAST_PATH}")

    forecasts = pd.read_csv(FORECAST_PATH)

    required_forecast_columns = [
        "Date", "Store ID", "Product ID", "Forecast Units Sold"
    ]
    missing = [
        column for column in required_forecast_columns
        if column not in forecasts.columns
    ]
    if missing:
        raise ValueError(f"Forecast file is missing columns: {missing}")

    with db_service.get_connection() as connection:
        inventory = pd.read_sql_query(
            """
            SELECT
                record_date AS "Date",
                store_id AS "Store ID",
                product_id AS "Product ID",
                inventory_level AS "Inventory Level",
                units_sold AS "Units Sold"
            FROM inventory_records
            """,
            connection,
        )

    if inventory.empty:
        raise ValueError("The inventory database contains no records.")

    inventory["Date"] = pd.to_datetime(
        inventory["Date"], errors="coerce"
    ).dt.normalize()
    forecasts["Date"] = pd.to_datetime(
        forecasts["Date"], errors="coerce"
    ).dt.normalize()

    for column in ("Store ID", "Product ID"):
        inventory[column] = inventory[column].astype(str)
        forecasts[column] = forecasts[column].astype(str)

    # Select the latest date that exists in both sources.
    keys = ["Date", "Store ID", "Product ID"]
    matching_dates = forecasts[keys].merge(
        inventory[keys].drop_duplicates(),
        on=keys,
        how="inner",
        validate="one_to_one",
    )

    if matching_dates.empty:
        raise ValueError(
            "No matching date/store/product records were found "
            "between inventory and forecasts."
        )

    source_date = matching_dates["Date"].max()
    latest_forecasts = forecasts[
        forecasts["Date"] == source_date
    ].copy()

    # Existing M12-03 logic performs the forecast/inventory join
    # and prior-seven-day fallback using historical inventory.
    stockout_results = stockout.build_stockout_detections(
        inventory,
        latest_forecasts,
    )

    if stockout_results.empty:
        raise ValueError("No stockout results were generated.")

    records = []
    for row in stockout_results.to_dict(orient="records"):
        reorder_result = reorder.calculate_reorder_recommendation(
            current_stock=row.get("Inventory Level"),
            forecast_daily_demand=row.get("Demand Used for Detection"),
            lead_time_days=stockout.DEFAULT_LEAD_TIME_DAYS,
            review_period_days=stockout.DEFAULT_REVIEW_PERIOD_DAYS,
            safety_stock_days=stockout.DEFAULT_SAFETY_STOCK_DAYS,
        )

        record = {
            key: _clean_value(value)
            for key, value in row.items()
        }
        record["reorder_recommendation"] = reorder_result
        records.append(record)

    reorder_counts = Counter(
        record["reorder_recommendation"]["recommendation_status"]
        for record in records
    )
    stockout_counts = Counter(
        record["stockout_status"]
        for record in records
    )

    return {
        "success": True,
        "source_date": source_date.strftime("%Y-%m-%d"),
        "data_classification": "HISTORICAL_DATA",
        "warning": (
            "These recommendations use the latest matching historical "
            "inventory and saved forecast data. They are not live stock "
            "levels or real-time purchasing instructions."
        ),
        "record_count": len(records),
        "summary": {
            "reorder_status_counts": dict(reorder_counts),
            "stockout_status_counts": dict(stockout_counts),
            "reorder_now_count": reorder_counts.get("REORDER_NOW", 0),
            "stockout_count": stockout_counts.get("STOCKOUT", 0),
            "stockout_risk_count": stockout_counts.get("STOCKOUT_RISK", 0),
        },
        "recommendations": records,
    }
