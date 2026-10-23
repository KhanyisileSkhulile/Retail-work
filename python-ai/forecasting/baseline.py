
"""M11-01: Establish a historical-average demand forecasting baseline."""

from pathlib import Path

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = REPO_ROOT / "dataset" / "processed"
FORECASTING_DIR = REPO_ROOT / "python-ai" / "forecasting"

TRAIN_FILE = PROCESSED_DIR / "retail_forecasting_train_m10_04.csv"
VALIDATION_FILE = PROCESSED_DIR / "retail_forecasting_validation_m10_04.csv"

PREDICTIONS_FILE = (
    PROCESSED_DIR / "retail_forecasting_baseline_validation_m11_01.csv"
)
REPORT_FILE = FORECASTING_DIR / "M11-01-baseline-results.md"

TARGET_COLUMN = "Units Sold"
GROUP_COLUMNS = ["Store ID", "Product ID"]


def decode_one_hot_identifier(df, prefix):
    """Recover an identifier from its one-hot encoded columns."""

    columns = [column for column in df.columns if column.startswith(prefix)]

    if not columns:
        raise ValueError(
            f"No one-hot encoded columns found for prefix {prefix!r}."
        )

    encoded = df[columns].apply(pd.to_numeric, errors="coerce").fillna(0)
    row_totals = encoded.sum(axis=1)

    if not row_totals.eq(1).all():
        raise ValueError(
            f"Expected exactly one active {prefix!r} column per row."
        )

    return encoded.idxmax(axis=1).str[len(prefix):]


def load_split(file_path):
    """Load and validate one prepared temporal split."""

    if not file_path.exists():
        raise FileNotFoundError(
            f"Required split file not found: {file_path}\n"
            "Run python-ai/data/prepare_temporal_splits.py first."
        )

    df = pd.read_csv(file_path)

    required = ["Date", TARGET_COLUMN]
    missing = [column for column in required if column not in df.columns]

    if missing:
        raise ValueError(f"{file_path.name} is missing columns: {missing}")

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df[TARGET_COLUMN] = pd.to_numeric(
        df[TARGET_COLUMN], errors="coerce"
    )

    if df["Date"].isna().any():
        raise ValueError(f"{file_path.name} contains invalid dates.")

    if df[TARGET_COLUMN].isna().any():
        raise ValueError(f"{file_path.name} contains missing demand targets.")

    if not np.isfinite(df[TARGET_COLUMN].to_numpy(dtype=float)).all():
        raise ValueError(f"{file_path.name} contains non-finite targets.")

    df["Store ID"] = decode_one_hot_identifier(df, "Store ID_")
    df["Product ID"] = decode_one_hot_identifier(df, "Product ID_")

    return df


def main():
    """Fit the baseline on training data and evaluate on validation data."""

    print("=" * 60)
    print("RETAILAI - M11-01 FORECASTING BASELINE")
    print("=" * 60)

    train_df = load_split(TRAIN_FILE)
    validation_df = load_split(VALIDATION_FILE)

    if train_df.empty or validation_df.empty:
        raise ValueError("Training and validation splits must not be empty.")

    # Ensure the validation period comes strictly after the training period.
    if train_df["Date"].max() >= validation_df["Date"].min():
        raise ValueError(
            "Temporal leakage risk: training dates overlap with or "
            "come after validation dates."
        )

    # Fit historical averages using training data only.
    series_means = (
        train_df.groupby(GROUP_COLUMNS, as_index=False)[TARGET_COLUMN]
        .mean()
        .rename(columns={TARGET_COLUMN: "Baseline Prediction"})
    )

    global_mean = float(train_df[TARGET_COLUMN].mean())

    # Apply each training-period mean to the matching validation series.
    predictions = validation_df.merge(
        series_means,
        on=GROUP_COLUMNS,
        how="left",
        validate="many_to_one",
    )

    # If an unseen series appears, use the training-set global mean.
    fallback_count = int(predictions["Baseline Prediction"].isna().sum())
    predictions["Baseline Prediction"] = predictions[
        "Baseline Prediction"
    ].fillna(global_mean)

    actual = predictions[TARGET_COLUMN].to_numpy(dtype=float)
    predicted = predictions["Baseline Prediction"].to_numpy(dtype=float)

    errors = actual - predicted
    mae = float(np.mean(np.abs(errors)))
    rmse = float(np.sqrt(np.mean(np.square(errors))))

    # Save row-level validation predictions as reproducible evidence.
    results = predictions[
        ["Date", *GROUP_COLUMNS, TARGET_COLUMN, "Baseline Prediction"]
    ].copy()

    results = results.rename(columns={TARGET_COLUMN: "Actual Units Sold"})
    results["Absolute Error"] = np.abs(errors)
    results["Squared Error"] = np.square(errors)
    results["Forecast Method"] = "Training-period store-product mean"

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    results.to_csv(PREDICTIONS_FILE, index=False, date_format="%Y-%m-%d")

    train_start = train_df["Date"].min().strftime("%Y-%m-%d")
    train_end = train_df["Date"].max().strftime("%Y-%m-%d")
    validation_start = validation_df["Date"].min().strftime("%Y-%m-%d")
    validation_end = validation_df["Date"].max().strftime("%Y-%m-%d")

    report = f"""# M11-01 — Forecasting Baseline Results

## Objective

Establish a simple, reproducible benchmark for retail demand forecasting.

## Baseline method

For each store-product combination, predict demand using the mean
`Units Sold` observed for that combination in the training split.
The mean is calculated from training data only.

If a validation row belongs to a combination not present in training,
the overall training-set mean is used instead.

## Data used

| Item | Result |
|---|---|
| Training rows | {len(train_df):,} |
| Training date range | {train_start} to {train_end} |
| Validation rows | {len(validation_df):,} |
| Validation date range | {validation_start} to {validation_end} |
| Store-product combinations learned | {len(series_means):,} |
| Global-mean fallbacks | {fallback_count:,} |
| Test split used | No |

## Validation results

| Metric | Result |
|---|---:|
| Mean Absolute Error (MAE) | {mae:.4f} |
| Root Mean Squared Error (RMSE) | {rmse:.4f} |

MAE measures the average absolute prediction error in units sold.
RMSE penalizes larger errors more strongly. Lower values indicate better
predictions, and these results provide a benchmark for later models.

## Reproducible evidence

- Script: `python-ai/forecasting/baseline.py`
- Row-level predictions: `dataset/processed/retail_forecasting_baseline_validation_m11_01.csv`
- Training source: `dataset/processed/retail_forecasting_train_m10_04.csv`
- Validation source: `dataset/processed/retail_forecasting_validation_m10_04.csv`

The holdout test split was not used. Later model comparisons should use
the same validation period and metrics for a fair comparison.
"""

    REPORT_FILE.write_text(report, encoding="utf-8")

    print("\nValidation results")
    print("-" * 60)
    print(f"Training rows:             {len(train_df):,}")
    print(f"Validation rows:           {len(validation_df):,}")
    print(f"Store-product series:      {len(series_means):,}")
    print(f"Global-mean fallbacks:     {fallback_count:,}")
    print(f"MAE:                       {mae:.4f}")
    print(f"RMSE:                      {rmse:.4f}")
    print("\nBaseline completed successfully.")
    print(f"Predictions: {PREDICTIONS_FILE}")
    print(f"Evidence report: {REPORT_FILE}")


if __name__ == "__main__":
    main()
