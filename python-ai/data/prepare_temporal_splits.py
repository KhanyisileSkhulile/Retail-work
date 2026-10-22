
"""M10-04: Create chronological train, validation, and test splits."""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "python-ai" / "data"
FORECASTING_DIR = REPO_ROOT / "python-ai" / "forecasting"
OUTPUT_DIR = REPO_ROOT / "dataset" / "processed"

sys.path.insert(0, str(FORECASTING_DIR))
sys.path.insert(0, str(DATA_DIR))

from clean_data import clean_and_validate
from feature_engineering import (
    prepare_forecasting_train_validation_test,
)

TRAIN_FILE = OUTPUT_DIR / "retail_forecasting_train_m10_04.csv"
VALIDATION_FILE = OUTPUT_DIR / "retail_forecasting_validation_m10_04.csv"
TEST_FILE = OUTPUT_DIR / "retail_forecasting_test_m10_04.csv"
PREPARED_FILE = OUTPUT_DIR / "retail_forecasting_features_m10_04.csv"

REPORT_FILE = DATA_DIR / "M10-04-temporal-split-report.md"


def main():
    print("\n" + "=" * 60)
    print("RETAILAI - TEMPORAL TRAIN/VALIDATION/TEST SPLITS")
    print("=" * 60)

    # Rebuild the cleaned data from the approved raw source.
    cleaned = clean_and_validate()

    train_df, validation_df, test_df, prepared_df, metadata = (
        prepare_forecasting_train_validation_test(
            cleaned,
            train_fraction=0.70,
            validation_fraction=0.15,
        )
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Save each split separately.
    train_df.to_csv(
        TRAIN_FILE, index=False, date_format="%Y-%m-%d"
    )
    validation_df.to_csv(
        VALIDATION_FILE, index=False, date_format="%Y-%m-%d"
    )
    test_df.to_csv(
        TEST_FILE, index=False, date_format="%Y-%m-%d"
    )
    prepared_df.to_csv(
        PREPARED_FILE, index=False, date_format="%Y-%m-%d"
    )
    # Verify chronology and structural consistency.
    chronological = (
        train_df["Date"].max() < validation_df["Date"].min()
        and validation_df["Date"].max() < test_df["Date"].min()
    )

    same_columns = (
        list(train_df.columns)
        == list(validation_df.columns)
        == list(test_df.columns)
    )

    dates_disjoint = (
        set(train_df["Date"]).isdisjoint(set(validation_df["Date"]))
        and set(train_df["Date"]).isdisjoint(set(test_df["Date"]))
        and set(validation_df["Date"]).isdisjoint(set(test_df["Date"]))
    )

    total_rows = len(train_df) + len(validation_df) + len(test_df)

    split_rows_match_combined = total_rows == len(prepared_df)
    all_usable_rows_retained = (
        len(prepared_df) == metadata["usable_rows"]
    )

    target_column = metadata["target_column"]
    missing_targets = {
        "Training": int(train_df[target_column].isna().sum()),
        "Validation": int(validation_df[target_column].isna().sum()),
        "Test": int(test_df[target_column].isna().sum()),
    }


    checks = {
        "Chronological ordering": chronological,
        "Identical columns": same_columns,
        "No dates shared between splits": dates_disjoint,
        "Split rows match combined dataset": split_rows_match_combined,
        "All usable rows retained": all_usable_rows_retained,
        "No missing target values": all(
            count == 0 for count in missing_targets.values()
        ),
    }

    print("\nValidation results:")
    for check_name, passed in checks.items():
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {check_name}")

    if not all(checks.values()):
        raise RuntimeError("Temporal split validation failed.")

    print("\nSplit summary:")
    print(f"Training rows: {len(train_df):,}")
    print(f"Validation rows: {len(validation_df):,}")
    print(f"Test rows: {len(test_df):,}")
    print(f"Report: {REPORT_FILE}")


if __name__ == "__main__":
    main()
