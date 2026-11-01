
"""M11-04: Train and save the selected retail demand forecasting model."""

import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from feature_engineering import (
    DEMAND_HISTORY_COLUMNS,
    prepare_forecasting_train_validation_test,
)
from models import get_candidate_models


FORECASTING_DIR = Path(__file__).resolve().parent
REPO_ROOT = FORECASTING_DIR.parents[1]

RAW_DATA_FILE = (
    REPO_ROOT
    / "dataset"
    / "processed"
    / "retail_store_inventory_clean.csv"
)

ARTIFACT_DIR = FORECASTING_DIR / "artifacts"
MODEL_FILE = ARTIFACT_DIR / "retail_demand_ridge_model.joblib"
METADATA_FILE = (
    ARTIFACT_DIR / "retail_demand_ridge_model_metadata.json"
)
REPORT_FILE = FORECASTING_DIR / "M11-04-trained-model-evidence.md"

TARGET_COLUMN = "Units Sold"
NON_FEATURE_COLUMNS = ["Date", TARGET_COLUMN]
SELECTED_MODEL_NAME = "Ridge Regression"


def prepare_model_inputs(df):
    """Extract numeric, finite model features and the target."""

    missing_history = [
        column
        for column in DEMAND_HISTORY_COLUMNS
        if column not in df.columns
    ]
    if missing_history:
        raise ValueError(
            f"Missing demand-history features: {missing_history}"
        )

    feature_columns = [
        column
        for column in df.columns
        if column not in NON_FEATURE_COLUMNS
    ]
    if not feature_columns:
        raise ValueError("No model features were found.")

    X = df[feature_columns].copy()

    for column in feature_columns:
        X[column] = pd.to_numeric(X[column], errors="coerce")

    y = pd.to_numeric(df[TARGET_COLUMN], errors="coerce").to_numpy(
        dtype=float
    )

    if X.isna().any().any():
        raise ValueError("Model features contain missing values.")

    if not np.isfinite(X.to_numpy(dtype=float)).all():
        raise ValueError("Model features contain non-finite values.")

    if not np.isfinite(y).all():
        raise ValueError("The target contains missing or non-finite values.")

    return X, y, feature_columns


def format_date(value):
    """Format a date consistently for the evidence report."""

    return pd.Timestamp(value).strftime("%Y-%m-%d")


def main():
    """Train the selected model, save it, and verify reloading."""

    print("=" * 65)
    print("RETAILAI - M11-04 SELECTED MODEL TRAINING")
    print("=" * 65)

    if not RAW_DATA_FILE.exists():
        raise FileNotFoundError(
            f"Required dataset not found: {RAW_DATA_FILE}"
        )

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    raw_df = pd.read_csv(RAW_DATA_FILE)

    train_df, validation_df, test_df, _, _ = (
        prepare_forecasting_train_validation_test(
            raw_df,
            train_fraction=0.70,
            validation_fraction=0.15,
        )
    )

    if train_df.empty or validation_df.empty or test_df.empty:
        raise ValueError("Train, validation, and test splits must be non-empty.")

    if train_df["Date"].max() >= validation_df["Date"].min():
        raise ValueError("Training and validation dates are not chronological.")

    if validation_df["Date"].max() >= test_df["Date"].min():
        raise ValueError("Validation and test dates are not chronological.")

    # Model selection is already complete. Fit the final model using
    # training + validation rows. Do not fit or evaluate on the test split.
    fit_df = pd.concat(
        [train_df, validation_df],
        ignore_index=True,
    )

    X_fit, y_fit, feature_columns = prepare_model_inputs(fit_df)

    model = get_candidate_models()[SELECTED_MODEL_NAME]

    print(f"Selected model: {SELECTED_MODEL_NAME}")
    print(f"Original training rows: {len(train_df):,}")
    print(f"Validation rows added to final fit: {len(validation_df):,}")
    print(f"Total rows used for fitting: {len(fit_df):,}")
    print(f"Feature count: {len(feature_columns)}")
    print("Fitting model...")

    model.fit(X_fit, y_fit)

    # Save the trained model, then reload it to verify the artifact.
    joblib.dump(model, MODEL_FILE)
    loaded_model = joblib.load(MODEL_FILE)

    # Smoke-test the reloaded model using training rows only.
    smoke_rows = min(10, len(X_fit))
    smoke_X = X_fit.iloc[:smoke_rows]
    original_predictions = np.asarray(
        model.predict(smoke_X), dtype=float
    )
    reloaded_predictions = np.asarray(
        loaded_model.predict(smoke_X), dtype=float
    )

    if len(reloaded_predictions) != smoke_rows:
        raise ValueError("The reloaded model returned the wrong prediction count.")

    if not np.isfinite(reloaded_predictions).all():
        raise ValueError("The reloaded model returned non-finite predictions.")

    if not np.allclose(original_predictions, reloaded_predictions):
        raise ValueError("Reloaded-model predictions do not match the original.")

    metadata = {
        "issue": "M11-04",
        "model_name": SELECTED_MODEL_NAME,
        "target_column": TARGET_COLUMN,
        "source_dataset": RAW_DATA_FILE.relative_to(REPO_ROOT).as_posix(),
        "selection_basis": (
            "Lowest validation MAE in the M11-03 model comparison."
        ),
        "fit_rows": len(fit_df),
        "original_training_rows": len(train_df),
        "validation_rows_in_final_fit": len(validation_df),
        "fit_start_date": format_date(fit_df["Date"].min()),
        "fit_end_date": format_date(fit_df["Date"].max()),
        "feature_count": len(feature_columns),
        "feature_columns": feature_columns,
        "model_configuration": {
            "scaler": "StandardScaler",
            "regressor": "Ridge",
            "alpha": 10.0,
        },
        "test_split_used_for_fitting": False,
        "test_split_used_for_smoke_test": False,
        "smoke_test_rows": smoke_rows,
        "predictions_finite": True,
        "saved_model_reload_verified": True,
        "trained_at_utc": datetime.now(timezone.utc).isoformat(),
        "artifact_file": MODEL_FILE.name,
    }

    METADATA_FILE.write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )

    report = f"""# M11-04 — Trained Selected Forecasting Model

## Objective

Train and save the selected model following the M11-03 comparison.

## Selected model

**{SELECTED_MODEL_NAME}**

The model was selected because it achieved the lowest validation MAE
in the M11-03 comparison. See
`M11-03-model-comparison-results.md` for the comparison evidence.

## Training details

| Item | Result |
|---|---|
| Source dataset | `dataset/processed/retail_store_inventory_clean.csv` |
| Target | `{TARGET_COLUMN}` |
| Original training rows | {len(train_df):,} |
| Validation rows included in final fit | {len(validation_df):,} |
| Total fitting rows | {len(fit_df):,} |
| Fitting date range | {format_date(fit_df["Date"].min())} to {format_date(fit_df["Date"].max())} |
| Number of features | {len(feature_columns)} |
| Scaler | StandardScaler |
| Regressor | Ridge Regression |
| Ridge alpha | 10.0 |
| Test split used for fitting | No |
| Test split used for smoke test | No |

The final model was fitted on the original training and validation
periods after model selection. The test split was excluded from fitting
and smoke testing.

## Verification

- Model saved successfully using Joblib.
- Saved model loaded back successfully.
- Reloaded model generated {smoke_rows} smoke-test predictions using
  training rows only.
- All smoke-test predictions were finite.
- Reloaded-model predictions matched the original model predictions.
- Model feature count: {len(feature_columns)}.

## Generated artifacts

- Trained model: `python-ai/forecasting/artifacts/retail_demand_ridge_model.joblib`
- Metadata: `python-ai/forecasting/artifacts/retail_demand_ridge_model_metadata.json`
- Training script: `python-ai/forecasting/train_selected_model.py`

## Limitations

The smoke test verifies model serialization and prediction behavior;
it is not an independent accuracy evaluation. The test split remains
reserved for a later final evaluation.
"""

    REPORT_FILE.write_text(report, encoding="utf-8")

    print("\nTraining completed successfully.")
    print(f"Model artifact: {MODEL_FILE}")
    print(f"Metadata: {METADATA_FILE}")
    print(f"Evidence report: {REPORT_FILE}")
    print("Reload verification: PASSED")
    print(f"Smoke-test rows: {smoke_rows}")
    print("Test split used for fitting or smoke testing: NO")


if __name__ == "__main__":
    main()
