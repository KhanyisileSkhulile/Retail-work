"""M11-06: Generate rolling one-step-ahead forecast outputs and charts."""

import json
from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error

from feature_engineering import prepare_forecasting_train_validation_test
from train_selected_model import prepare_model_inputs


FORECASTING_DIR = Path(__file__).resolve().parent
REPO_ROOT = FORECASTING_DIR.parents[1]
DATA_FILE = REPO_ROOT / "dataset" / "processed" / "retail_store_inventory_clean.csv"
ARTIFACT_DIR = FORECASTING_DIR / "artifacts"
MODEL_FILE = ARTIFACT_DIR / "retail_demand_ridge_model.joblib"
METADATA_FILE = ARTIFACT_DIR / "retail_demand_ridge_model_metadata.json"
OUTPUT_DIR = FORECASTING_DIR / "outputs"
DOCS_DIR = REPO_ROOT / "documentation" / "07-ai"

MODEL_NAME = "Ridge Regression"
TARGET_COLUMN = "Units Sold"


def decode_one_hot_identifier(df, prefix):
    """Recover IDs from the one-hot encoded store/product feature columns."""
    columns = [column for column in df.columns if column.startswith(prefix)]
    if not columns:
        raise ValueError(f"No one-hot encoded columns found for {prefix!r}.")

    encoded = df[columns].apply(pd.to_numeric, errors="coerce").fillna(0)
    row_totals = encoded.sum(axis=1)
    identifiers = encoded.idxmax(axis=1).str[len(prefix):]
    return identifiers.where(row_totals.eq(1), "__UNKNOWN__")


def main():
    print("=" * 65)
    print("RETAILAI - M11-06 FORECAST OUTPUTS AND VISUALIZATIONS")
    print("=" * 65)

    for path, label in [
        (DATA_FILE, "Processed dataset"),
        (MODEL_FILE, "Trained model"),
        (METADATA_FILE, "Model metadata"),
    ]:
        if not path.is_file():
            raise FileNotFoundError(f"{label} not found: {path}")

    with METADATA_FILE.open("r", encoding="utf-8") as file:
        metadata = json.load(file)

    if metadata.get("model_name") != MODEL_NAME:
        raise ValueError("The saved model metadata does not match Ridge Regression.")
    if metadata.get("test_split_used_for_fitting") is not False:
        raise ValueError("Model metadata does not confirm an untouched test split.")

    raw_df = pd.read_csv(DATA_FILE)
    train_df, validation_df, test_df, _, _ = prepare_forecasting_train_validation_test(
        raw_df,
        train_fraction=0.70,
        validation_fraction=0.15,
    )
    if train_df.empty or validation_df.empty or test_df.empty:
        raise ValueError("Training, validation, and test splits must be non-empty.")

    fit_end = pd.Timestamp(metadata["fit_end_date"])
    test_start_date = pd.Timestamp(test_df["Date"].min())
    if test_start_date <= fit_end:
        raise ValueError("Test period overlaps the model fitting period.")

    X_test, y_test, feature_columns = prepare_model_inputs(test_df)
    if feature_columns != metadata.get("feature_columns"):
        raise ValueError("Test features do not match the saved model feature list.")

    model = joblib.load(MODEL_FILE)
    predictions = np.asarray(model.predict(X_test), dtype=float)
    if len(predictions) != len(y_test):
        raise ValueError("Prediction count does not match the test target count.")
    if not np.isfinite(predictions).all():
        raise ValueError("Model predictions contain non-finite values.")

    actual = np.asarray(y_test, dtype=float)
    mae = float(mean_absolute_error(actual, predictions))
    rmse = float(np.sqrt(mean_squared_error(actual, predictions)))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    forecasts = pd.DataFrame({
        "Date": pd.to_datetime(test_df["Date"]).dt.strftime("%Y-%m-%d").to_numpy(),
        "Store ID": decode_one_hot_identifier(test_df, "Store ID_").to_numpy(),
        "Product ID": decode_one_hot_identifier(test_df, "Product ID_").to_numpy(),
        "Actual Units Sold": actual,
        "Forecast Units Sold": predictions,
        "Absolute Error": np.abs(actual - predictions),
    })
    forecasts = forecasts.sort_values(["Date", "Store ID", "Product ID"]).reset_index(drop=True)

    forecasts_path = OUTPUT_DIR / "retail_demand_forecasts_m11_06.csv"
    forecasts.to_csv(forecasts_path, index=False)

    daily = (
        forecasts.groupby("Date", as_index=False)
        .agg(
            **{
                "Actual Demand Total": ("Actual Units Sold", "sum"),
                "Forecast Demand Total": ("Forecast Units Sold", "sum"),
                "Mean Absolute Error": ("Absolute Error", "mean"),
                "Forecast Rows": ("Product ID", "size"),
            }
        )
    )
    daily_path = OUTPUT_DIR / "retail_demand_daily_summary_m11_06.csv"
    daily.to_csv(daily_path, index=False)

    # Chart 1: daily aggregate actual demand versus forecasts across all series.
    daily_dates = pd.to_datetime(daily["Date"])
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(daily_dates, daily["Actual Demand Total"], label="Actual demand", linewidth=1.8)
    ax.plot(daily_dates, daily["Forecast Demand Total"], label="Forecast demand", linewidth=1.8)
    ax.set_title("Retail Demand: Actual vs Forecast (Temporal Holdout)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Total units sold across store-product series")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    daily_chart = OUTPUT_DIR / "daily_actual_vs_forecast_m11_06.png"
    fig.savefig(daily_chart, dpi=160, bbox_inches="tight")
    plt.close(fig)

    # Chart 2: row-level actual-versus-predicted comparison.
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.scatter(actual, predictions, alpha=0.22, s=12)
    lower = float(min(np.min(actual), np.min(predictions)))
    upper = float(max(np.max(actual), np.max(predictions)))
    ax.plot([lower, upper], [lower, upper], linestyle="--", linewidth=1.5, label="Perfect prediction")
    ax.set_title("Actual vs Forecast Units Sold")
    ax.set_xlabel("Actual units sold")
    ax.set_ylabel("Forecast units sold")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    scatter_chart = OUTPUT_DIR / "actual_vs_forecast_scatter_m11_06.png"
    fig.savefig(scatter_chart, dpi=160, bbox_inches="tight")
    plt.close(fig)

    # Chart 3: distribution of absolute row-level errors.
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(forecasts["Absolute Error"], bins=40, edgecolor="white")
    ax.set_title("Distribution of Absolute Forecast Errors")
    ax.set_xlabel("Absolute error (units sold)")
    ax.set_ylabel("Number of forecasts")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    error_chart = OUTPUT_DIR / "forecast_error_distribution_m11_06.png"
    fig.savefig(error_chart, dpi=160, bbox_inches="tight")
    plt.close(fig)

    summary = {
        "issue": "M11-06",
        "model_name": MODEL_NAME,
        "target_column": TARGET_COLUMN,
        "forecasting_method": "Rolling one-step-ahead chronological holdout",
        "fit_end_date": fit_end.strftime("%Y-%m-%d"),
        "forecast_start_date": pd.Timestamp(forecasts["Date"].min()).strftime("%Y-%m-%d"),
        "forecast_end_date": pd.Timestamp(forecasts["Date"].max()).strftime("%Y-%m-%d"),
        "forecast_rows": int(len(forecasts)),
        "unique_forecast_dates": int(forecasts["Date"].nunique()),
        "feature_count": len(feature_columns),
        "mae": mae,
        "rmse": rmse,
        "test_data_used_for_training": False,
        "model_retrained_during_forecasting": False,
        "output_files": [
            forecasts_path.relative_to(REPO_ROOT).as_posix(),
            daily_path.relative_to(REPO_ROOT).as_posix(),
            daily_chart.relative_to(REPO_ROOT).as_posix(),
            scatter_chart.relative_to(REPO_ROOT).as_posix(),
            error_chart.relative_to(REPO_ROOT).as_posix(),
        ],
    }
    summary_path = OUTPUT_DIR / "retail_demand_forecast_summary_m11_06.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    report = f"""# M11-06 — Forecast Outputs and Visualizations

## Objective

Generate row-level forecasts from the saved Ridge Regression model, plus summary data and charts for the chronological test period.

## Forecast run

| Item | Result |
|---|---|
| Model | {MODEL_NAME} |
| Target | `{TARGET_COLUMN}` |
| Forecast approach | Rolling one-step-ahead chronological holdout |
| Model fitting period ends | {fit_end.strftime('%Y-%m-%d')} |
| Forecast period | {summary['forecast_start_date']} to {summary['forecast_end_date']} |
| Forecast rows | {len(forecasts):,} |
| Unique forecast dates | {forecasts['Date'].nunique():,} |
| Features | {len(feature_columns)} |
| MAE | {mae:.6f} |
| RMSE | {rmse:.6f} |
| Test data used for training | No |
| Model retrained during forecasting | No |

Forecasts are rolling one-step-ahead predictions: demand observed on earlier dates is used as history for later dates. They are not a fixed multi-day forecast made without any new observations.

## Generated outputs

- Row-level forecasts: `python-ai/forecasting/outputs/retail_demand_forecasts_m11_06.csv`
- Daily aggregate summary: `python-ai/forecasting/outputs/retail_demand_daily_summary_m11_06.csv`
- Metrics summary: `python-ai/forecasting/outputs/retail_demand_forecast_summary_m11_06.json`

## Generated charts

- Daily actual versus forecast: `python-ai/forecasting/outputs/daily_actual_vs_forecast_m11_06.png`
- Actual versus forecast scatter plot: `python-ai/forecasting/outputs/actual_vs_forecast_scatter_m11_06.png`
- Absolute forecast error distribution: `python-ai/forecasting/outputs/forecast_error_distribution_m11_06.png`

## Reproduce

Run from the repository root:

```powershell
python .\\python-ai\\forecasting\\forecast.py
```

The script loads the saved model and processed dataset. It does not retrain or overwrite the trained model.
"""
    report_path = DOCS_DIR / "M11-06-forecast-output-evidence.md"
    report_path.write_text(report, encoding="utf-8")

    print("\nForecast generation completed successfully.")
    print(f"Forecast period: {summary['forecast_start_date']} to {summary['forecast_end_date']}")
    print(f"Forecast rows: {len(forecasts):,}")
    print(f"MAE: {mae:.6f}")
    print(f"RMSE: {rmse:.6f}")
    print(f"Forecast CSV: {forecasts_path}")
    print(f"Daily summary CSV: {daily_path}")
    print(f"Charts: {daily_chart.name}, {scatter_chart.name}, {error_chart.name}")
    print(f"Evidence report: {report_path}")
    print("Test data used for training: NO")
    print("Model retrained during forecasting: NO")


if __name__ == "__main__":
    main()
