"""M11-03: Evaluate candidate retail demand forecasting models."""

from pathlib import Path
import time

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error

from feature_engineering import (
    DEMAND_HISTORY_COLUMNS,
    prepare_forecasting_train_validation_test,
)
from models import get_candidate_models


REPO_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = REPO_ROOT / "dataset" / "processed"
FORECASTING_DIR = REPO_ROOT / "python-ai" / "forecasting"

RAW_DATA_FILE = PROCESSED_DIR / "retail_store_inventory_clean.csv"

TRAIN_FILE = PROCESSED_DIR / "retail_forecasting_train_m11_03.csv"
VALIDATION_FILE = (
    PROCESSED_DIR / "retail_forecasting_validation_m11_03.csv"
)
TEST_FILE = PROCESSED_DIR / "retail_forecasting_test_m11_03.csv"

COMPARISON_FILE = (
    PROCESSED_DIR / "retail_forecasting_model_comparison_m11_03.csv"
)
PREDICTIONS_FILE = (
    PROCESSED_DIR / "retail_forecasting_model_predictions_m11_03.csv"
)
REPORT_FILE = FORECASTING_DIR / "M11-03-model-comparison-results.md"

TARGET_COLUMN = "Units Sold"
IDENTIFIER_COLUMNS = ["Store ID", "Product ID"]
NON_FEATURE_COLUMNS = ["Date", TARGET_COLUMN]


def decode_one_hot_identifier(df, prefix):
    """Recover store or product IDs from one-hot encoded columns."""

    columns = [
        column for column in df.columns
        if column.startswith(prefix)
    ]

    if not columns:
        raise ValueError(
            f"No one-hot encoded columns found for {prefix!r}."
        )

    encoded = (
        df[columns]
        .apply(pd.to_numeric, errors="coerce")
        .fillna(0)
    )

    row_totals = encoded.sum(axis=1)
    identifiers = encoded.idxmax(axis=1).str[len(prefix):]

    # Unseen categories are handled by the global-mean fallback.
    return identifiers.where(row_totals.eq(1), "__UNKNOWN__")


def calculate_metrics(actual, predicted):
    """Calculate standard regression metrics."""

    errors = actual - predicted

    return {
        "MAE": float(mean_absolute_error(actual, predicted)),
        "RMSE": float(np.sqrt(mean_squared_error(actual, predicted))),
    }


def validate_features(train_df, validation_df):
    """Prepare numeric model inputs and verify M11-02 features exist."""

    missing_history = [
        column for column in DEMAND_HISTORY_COLUMNS
        if column not in train_df.columns
    ]

    if missing_history:
        raise ValueError(
            "The M11-02 demand-history features are missing: "
            f"{missing_history}"
        )

    feature_columns = [
        column for column in train_df.columns
        if column not in NON_FEATURE_COLUMNS
    ]

    if not feature_columns:
        raise ValueError("No model features were found.")

    X_train = train_df[feature_columns].copy()
    X_validation = validation_df.reindex(
        columns=feature_columns
    ).copy()

    for column in feature_columns:
        X_train[column] = pd.to_numeric(
            X_train[column], errors="coerce"
        )
        X_validation[column] = pd.to_numeric(
            X_validation[column], errors="coerce"
        )

    if X_train.isna().any().any():
        raise ValueError(
            "Training features contain missing values. "
            "Check the feature-engineering output."
        )

    if X_validation.isna().any().any():
        raise ValueError(
            "Validation features contain missing values. "
            "Check the feature-engineering output."
        )

    if not np.isfinite(X_train.to_numpy(dtype=float)).all():
        raise ValueError("Training features contain non-finite values.")

    if not np.isfinite(X_validation.to_numpy(dtype=float)).all():
        raise ValueError(
            "Validation features contain non-finite values."
        )

    return X_train, X_validation, feature_columns


def main():
    """Prepare the data, compare models and write evidence."""

    print("=" * 65)
    print("RETAILAI - M11-03 FORECASTING MODEL EVALUATION")
    print("=" * 65)

    if not RAW_DATA_FILE.exists():
        raise FileNotFoundError(
            f"Required dataset not found: {RAW_DATA_FILE}"
        )

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    FORECASTING_DIR.mkdir(parents=True, exist_ok=True)

    # Generate chronological splits using the M11-02 features.
    raw_df = pd.read_csv(RAW_DATA_FILE)

    (
        train_df,
        validation_df,
        test_df,
        _,
        metadata,
    ) = prepare_forecasting_train_validation_test(
        raw_df,
        train_fraction=0.70,
        validation_fraction=0.15,
    )

    if train_df.empty or validation_df.empty or test_df.empty:
        raise ValueError("Train, validation and test splits must be non-empty.")

    if train_df["Date"].max() >= validation_df["Date"].min():
        raise ValueError(
            "Training and validation dates overlap or are out of order."
        )

    if validation_df["Date"].max() >= test_df["Date"].min():
        raise ValueError(
            "Validation and test dates overlap or are out of order."
        )

    # Save reproducible splits. The test split is saved but not evaluated.
    train_df.to_csv(TRAIN_FILE, index=False, date_format="%Y-%m-%d")
    validation_df.to_csv(
        VALIDATION_FILE, index=False, date_format="%Y-%m-%d"
    )
    test_df.to_csv(TEST_FILE, index=False, date_format="%Y-%m-%d")

    X_train, X_validation, feature_columns = validate_features(
        train_df, validation_df
    )

    y_train = train_df[TARGET_COLUMN].to_numpy(dtype=float)
    y_validation = validation_df[TARGET_COLUMN].to_numpy(dtype=float)

    result_rows = []
    prediction_frames = []

    def record_result(name, predicted, fit_seconds, predict_seconds):
        """Store metrics and row-level predictions for one method."""

        predicted = np.asarray(predicted, dtype=float)

        if len(predicted) != len(y_validation):
            raise ValueError(
                f"{name} returned the wrong number of predictions."
            )

        if not np.isfinite(predicted).all():
            raise ValueError(
                f"{name} produced non-finite predictions."
            )

        metrics = calculate_metrics(y_validation, predicted)

        result_rows.append({
            "Model": name,
            "MAE": metrics["MAE"],
            "RMSE": metrics["RMSE"],
            "Fit Seconds": round(fit_seconds, 3),
            "Prediction Seconds": round(predict_seconds, 3),
            "Training Rows": len(train_df),
            "Validation Rows": len(validation_df),
            "Feature Count": len(feature_columns),
        })

        validation_ids = pd.DataFrame({
            "Store ID": decode_one_hot_identifier(
                validation_df, "Store ID_"
            ),
            "Product ID": decode_one_hot_identifier(
                validation_df, "Product ID_"
            ),
        })

        prediction_frames.append(pd.DataFrame({
            "Date": validation_df["Date"].to_numpy(),
            "Store ID": validation_ids["Store ID"].to_numpy(),
            "Product ID": validation_ids["Product ID"].to_numpy(),
            "Actual Units Sold": y_validation,
            "Predicted Units Sold": predicted,
            "Absolute Error": np.abs(y_validation - predicted),
            "Forecast Method": name,
        }))

        print(
            f"{name}: MAE={metrics['MAE']:.4f}, "
            f"RMSE={metrics['RMSE']:.4f}"
        )

    # Historical-average baseline, calculated from training data only.
    start_fit = time.perf_counter()

    train_with_ids = train_df.copy()
    validation_with_ids = validation_df.copy()

    for prefix, column in [
        ("Store ID_", "Store ID"),
        ("Product ID_", "Product ID"),
    ]:
        train_with_ids[column] = decode_one_hot_identifier(
            train_df, prefix
        )
        validation_with_ids[column] = decode_one_hot_identifier(
            validation_df, prefix
        )

    series_means = (
        train_with_ids.groupby(IDENTIFIER_COLUMNS, as_index=False)[
            TARGET_COLUMN
        ]
        .mean()
        .rename(columns={TARGET_COLUMN: "Baseline Prediction"})
    )

    global_mean = float(y_train.mean())
    baseline_fit_seconds = time.perf_counter() - start_fit

    start_predict = time.perf_counter()

    baseline_rows = validation_with_ids.merge(
        series_means,
        on=IDENTIFIER_COLUMNS,
        how="left",
        validate="many_to_one",
    )

    baseline_predictions = (
        baseline_rows["Baseline Prediction"]
        .fillna(global_mean)
        .to_numpy(dtype=float)
    )

    baseline_predict_seconds = time.perf_counter() - start_predict

    record_result(
        "Store-Product Historical Mean",
        baseline_predictions,
        baseline_fit_seconds,
        baseline_predict_seconds,
    )

    # Evaluate all candidate models on exactly the same validation period.
    for model_name, model in get_candidate_models().items():
        print(f"\nTraining {model_name}...")

        start_fit = time.perf_counter()
        model.fit(X_train, y_train)
        fit_seconds = time.perf_counter() - start_fit

        start_predict = time.perf_counter()
        predictions = model.predict(X_validation)
        predict_seconds = time.perf_counter() - start_predict

        record_result(
            model_name,
            predictions,
            fit_seconds,
            predict_seconds,
        )

    # Save the comparison and row-level prediction evidence.
    comparison_df = pd.DataFrame(result_rows).sort_values(
        "MAE", ascending=True
    ).reset_index(drop=True)

    comparison_df.to_csv(COMPARISON_FILE, index=False)

    all_predictions = pd.concat(
        prediction_frames, ignore_index=True
    )
    all_predictions.to_csv(
        PREDICTIONS_FILE, index=False, date_format="%Y-%m-%d"
    )

    best = comparison_df.iloc[0]

    def format_date(value):
        return pd.Timestamp(value).strftime("%Y-%m-%d")

    table_lines = [
        "| Model | MAE | RMSE | Fit seconds | Prediction seconds |",
        "|---|---:|---:|---:|---:|",
    ]

    for _, row in comparison_df.iterrows():
        table_lines.append(
            f"| {row['Model']} "
            f"| {row['MAE']:.4f} "
            f"| {row['RMSE']:.4f} "
            f"| {row['Fit Seconds']:.3f} "
            f"| {row['Prediction Seconds']:.3f} |"
        )

    comparison_table = "\n".join(table_lines)

    report = f"""# M11-03 — Candidate Forecasting Model Evaluation

## Objective

Compare candidate regression models against a historical-average
baseline using the same chronological validation period.

## Data and evaluation approach

| Item | Result |
|---|---|
| Raw dataset | `dataset/processed/retail_store_inventory_clean.csv` |
| Training rows | {len(train_df):,} |
| Training date range | {format_date(train_df["Date"].min())} to {format_date(train_df["Date"].max())} |
| Validation rows | {len(validation_df):,} |
| Validation date range | {format_date(validation_df["Date"].min())} to {format_date(validation_df["Date"].max())} |
| Test rows | {len(test_df):,} |
| Test split used for model selection | No |
| Number of model features | {len(feature_columns)} |
| Demand-history features included | {", ".join(DEMAND_HISTORY_COLUMNS)} |

All candidate models use the same training rows, validation rows,
feature columns and target (`Units Sold`).

Demand-history features are evaluated for rolling one-step-ahead
forecasting, where previously observed demand is available when making
the next prediction.

## Metrics

- **MAE (Mean Absolute Error):** average absolute prediction error.
- **RMSE (Root Mean Squared Error):** penalizes larger errors more strongly.

Lower values indicate better validation performance.

## Validation comparison

{comparison_table}

## Best validation result

The lowest-MAE result is **{best["Model"]}**, with MAE
**{best["MAE"]:.4f}** and RMSE **{best["RMSE"]:.4f}**.

This identifies the best result on the validation period only. The
test split remains untouched and should be reserved for a later,
final evaluation.

## Reproducible evidence

- Candidate models: `python-ai/forecasting/models.py`
- Evaluation script: `python-ai/forecasting/evaluation.py`
- Training split: `dataset/processed/retail_forecasting_train_m11_03.csv`
- Validation split: `dataset/processed/retail_forecasting_validation_m11_03.csv`
- Saved test split: `dataset/processed/retail_forecasting_test_m11_03.csv`
- Comparison metrics: `dataset/processed/retail_forecasting_model_comparison_m11_03.csv`
- Row-level predictions: `dataset/processed/retail_forecasting_model_predictions_m11_03.csv`

## Limitations

Results apply to this dataset and validation period. The best validation
model is not guaranteed to perform best on unseen test data.
"""

    REPORT_FILE.write_text(report, encoding="utf-8")

    print("\n" + "=" * 65)
    print("MODEL COMPARISON COMPLETED")
    print("=" * 65)
    print(comparison_df[["Model", "MAE", "RMSE"]].to_string(index=False))
    print(f"\nBest validation result: {best['Model']}")
    print(f"Comparison CSV: {COMPARISON_FILE}")
    print(f"Predictions CSV: {PREDICTIONS_FILE}")
    print(f"Evidence report: {REPORT_FILE}")
    print("\nThe test split was not used to select a model.")


if __name__ == "__main__":
    main()