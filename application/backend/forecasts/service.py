"""Application-facing service for M11-06 demand forecast outputs.

The source file contains rolling one-step-ahead forecasts from the chronological
holdout period. These records are historical evaluation results, not future
multi-day predictions.
"""

import json
import math
from pathlib import Path
from typing import Optional

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[3]
FORECAST_FILE = (
    REPO_ROOT
    / "python-ai"
    / "forecasting"
    / "outputs"
    / "retail_demand_forecasts_m11_06.csv"
)
METADATA_FILE = (
    REPO_ROOT
    / "python-ai"
    / "forecasting"
    / "outputs"
    / "retail_demand_forecast_summary_m11_06.json"
)

REQUIRED_COLUMNS = [
    "Date",
    "Store ID",
    "Product ID",
    "Actual Units Sold",
    "Forecast Units Sold",
    "Absolute Error",
]
NUMERIC_COLUMNS = [
    "Actual Units Sold",
    "Forecast Units Sold",
    "Absolute Error",
]
DAILY_SUMMARY_COLUMNS = [
    "Date",
    "Actual Demand Total",
    "Forecast Demand Total",
    "Mean Absolute Error",
    "Forecast Rows",
]


def _resolve_path(path: Optional[str | Path], default: Path) -> Path:
    """Resolve a supplied path or use the repository default."""
    resolved = Path(path) if path is not None else default
    if not resolved.is_absolute():
        resolved = REPO_ROOT / resolved
    return resolved.resolve()


def load_forecasts(csv_path: Optional[str | Path] = None) -> pd.DataFrame:
    """Load and validate the row-level forecast CSV."""
    source = _resolve_path(csv_path, FORECAST_FILE)
    if not source.is_file():
        raise FileNotFoundError(f"Forecast results CSV not found: {source}")

    frame = pd.read_csv(source)
    missing = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(
            "Forecast results are missing required columns: "
            + ", ".join(missing)
        )
    if frame.empty:
        raise ValueError("Forecast results CSV contains no records.")

    frame = frame[REQUIRED_COLUMNS].copy()
    if frame.isna().any().any():
        raise ValueError("Forecast results contain missing required values.")

    frame["Date"] = pd.to_datetime(frame["Date"], errors="coerce")
    if frame["Date"].isna().any():
        raise ValueError("Forecast results contain invalid dates.")

    for column in ("Store ID", "Product ID"):
        frame[column] = frame[column].astype(str).str.strip()
        if frame[column].eq("").any():
            raise ValueError(f"Forecast results contain blank {column} values.")

    for column in NUMERIC_COLUMNS:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
        if frame[column].isna().any():
            raise ValueError(f"{column} must contain numeric values.")
        if not frame[column].map(math.isfinite).all():
            raise ValueError(f"{column} contains non-finite values.")

    if (frame["Absolute Error"] < 0).any():
        raise ValueError("Absolute Error cannot contain negative values.")

    calculated_error = (
        frame["Actual Units Sold"] - frame["Forecast Units Sold"]
    ).abs()
    if not (
        (frame["Absolute Error"] - calculated_error).abs() <= 1e-6
    ).all():
        raise ValueError(
            "Absolute Error values do not match actual-versus-forecast differences."
        )

    duplicate_keys = frame.duplicated(
        subset=["Date", "Store ID", "Product ID"],
        keep=False,
    )
    if duplicate_keys.any():
        raise ValueError(
            "Forecast results contain duplicate Date/Store ID/Product ID records."
        )

    return frame.sort_values(
        ["Date", "Store ID", "Product ID"]
    ).reset_index(drop=True)


def load_forecast_metadata(
    metadata_path: Optional[str | Path] = None,
) -> dict:
    """Load the JSON summary generated alongside the forecast CSV."""
    source = _resolve_path(metadata_path, METADATA_FILE)
    if not source.is_file():
        raise FileNotFoundError(f"Forecast metadata JSON not found: {source}")

    try:
        with source.open("r", encoding="utf-8") as metadata_file:
            metadata = json.load(metadata_file)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Forecast metadata is not valid JSON: {source}") from exc

    if not isinstance(metadata, dict):
        raise ValueError("Forecast metadata must contain a JSON object.")
    return metadata


def summarize_forecasts(frame: pd.DataFrame) -> dict:
    """Return totals and error metrics for the supplied forecast records."""
    if frame.empty:
        return {
            "records": 0,
            "stores": 0,
            "products": 0,
            "start_date": None,
            "end_date": None,
            "actual_demand_total": 0.0,
            "forecast_demand_total": 0.0,
            "mae": None,
            "rmse": None,
        }

    errors = frame["Actual Units Sold"] - frame["Forecast Units Sold"]
    return {
        "records": int(len(frame)),
        "stores": int(frame["Store ID"].nunique()),
        "products": int(frame["Product ID"].nunique()),
        "start_date": pd.Timestamp(frame["Date"].min()).strftime("%Y-%m-%d"),
        "end_date": pd.Timestamp(frame["Date"].max()).strftime("%Y-%m-%d"),
        "actual_demand_total": float(frame["Actual Units Sold"].sum()),
        "forecast_demand_total": float(frame["Forecast Units Sold"].sum()),
        "mae": float(frame["Absolute Error"].mean()),
        "rmse": float(math.sqrt((errors ** 2).mean())),
    }


def validate_forecast_metadata(
    frame: pd.DataFrame,
    metadata: dict,
) -> None:
    """Check that JSON metadata describes the loaded forecast CSV."""
    required = [
        "model_name",
        "forecast_rows",
        "unique_forecast_dates",
        "forecast_start_date",
        "forecast_end_date",
        "mae",
        "rmse",
    ]
    missing = [key for key in required if key not in metadata]
    if missing:
        raise ValueError(
            "Forecast metadata is missing required fields: "
            + ", ".join(missing)
        )

    summary = summarize_forecasts(frame)
    if int(metadata["forecast_rows"]) != summary["records"]:
        raise ValueError("Forecast metadata row count does not match the CSV.")
    if int(metadata["unique_forecast_dates"]) != int(frame["Date"].nunique()):
        raise ValueError("Forecast metadata date count does not match the CSV.")
    if str(metadata["forecast_start_date"]) != summary["start_date"]:
        raise ValueError("Forecast metadata start date does not match the CSV.")
    if str(metadata["forecast_end_date"]) != summary["end_date"]:
        raise ValueError("Forecast metadata end date does not match the CSV.")

    for key in ("mae", "rmse"):
        try:
            expected = float(metadata[key])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Forecast metadata {key} must be numeric.") from exc
        if not math.isfinite(expected) or not math.isclose(
            expected,
            summary[key],
            rel_tol=1e-6,
            abs_tol=1e-6,
        ):
            raise ValueError(f"Forecast metadata {key} does not match the CSV.")


def filter_forecasts(
    frame: pd.DataFrame,
    store_id: Optional[str] = None,
    product_id: Optional[str] = None,
    start_date=None,
    end_date=None,
) -> pd.DataFrame:
    """Filter forecast records by store, product and inclusive date range."""
    filtered = frame.copy()

    if store_id is not None:
        filtered = filtered[filtered["Store ID"] == str(store_id)]
    if product_id is not None:
        filtered = filtered[filtered["Product ID"] == str(product_id)]

    try:
        start = pd.Timestamp(start_date) if start_date is not None else None
        end = pd.Timestamp(end_date) if end_date is not None else None
    except (TypeError, ValueError) as exc:
        raise ValueError("Forecast date filters must be valid dates.") from exc

    if start is not None and end is not None and start > end:
        raise ValueError("Start date cannot be later than end date.")
    if start is not None:
        filtered = filtered[filtered["Date"] >= start]
    if end is not None:
        filtered = filtered[filtered["Date"] <= end]

    return filtered.sort_values(
        ["Date", "Store ID", "Product ID"]
    ).reset_index(drop=True)


def build_daily_summary(frame: pd.DataFrame) -> pd.DataFrame:
    """Aggregate actual demand and forecast demand by date."""
    if frame.empty:
        return pd.DataFrame(columns=DAILY_SUMMARY_COLUMNS)

    daily = (
        frame.groupby("Date", as_index=False)
        .agg(
            **{
                "Actual Demand Total": ("Actual Units Sold", "sum"),
                "Forecast Demand Total": ("Forecast Units Sold", "sum"),
                "Mean Absolute Error": ("Absolute Error", "mean"),
                "Forecast Rows": ("Product ID", "size"),
            }
        )
        .sort_values("Date")
        .reset_index(drop=True)
    )
    return daily


__all__ = [
    "FORECAST_FILE",
    "METADATA_FILE",
    "load_forecasts",
    "load_forecast_metadata",
    "summarize_forecasts",
    "validate_forecast_metadata",
    "filter_forecasts",
    "build_daily_summary",
]
