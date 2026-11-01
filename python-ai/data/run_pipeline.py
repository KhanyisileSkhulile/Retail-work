
"""M14-02: Integrate the Python data pipeline with SQLite."""

import argparse
import sys
from pathlib import Path

import pandas as pd


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "python-ai" / "data"
FORECASTING_DIR = PROJECT_ROOT / "python-ai" / "forecasting"
DATABASE_SERVICE_DIR = (
    PROJECT_ROOT / "application" / "backend" / "database"
)

RAW_FILE = (
    PROJECT_ROOT / "dataset" / "raw" / "retail_store_inventory.csv"
)
PROCESSED_DIR = PROJECT_ROOT / "dataset" / "processed"

CLEANED_FILE = PROCESSED_DIR / "retail_store_inventory_clean.csv"
TRAIN_FILE = PROCESSED_DIR / "retail_forecasting_train_m10_04.csv"
VALIDATION_FILE = (
    PROCESSED_DIR / "retail_forecasting_validation_m10_04.csv"
)
TEST_FILE = PROCESSED_DIR / "retail_forecasting_test_m10_04.csv"
PREPARED_FILE = (
    PROCESSED_DIR / "retail_forecasting_features_m10_04.csv"
)

REPORT_FILE = DATA_DIR / "M14-02-pipeline-integration-report.md"


# Make existing project modules available.
for directory in (
    DATA_DIR,
    FORECASTING_DIR,
    DATABASE_SERVICE_DIR,
):
    directory_string = str(directory)
    if directory_string not in sys.path:
        sys.path.insert(0, directory_string)


from prepare_temporal_splits import main as prepare_temporal_splits
from service import initialize_database, get_inventory_summary


def count_csv_rows(file_path: Path) -> int:
    """Count records in a CSV file."""
    if not file_path.is_file():
        raise FileNotFoundError(
            f"Required pipeline output not found: {file_path}"
        )

    return len(pd.read_csv(file_path))


def relative_path(file_path: Path) -> str:
    """Return a project-relative path for reporting."""
    return file_path.relative_to(PROJECT_ROOT).as_posix()


def run_pipeline(force_reload: bool = False) -> dict:
    """Run data preparation, temporal splitting and SQLite integration."""

    print("\n" + "=" * 65)
    print("RETAILAI - M14-02 PYTHON DATA PIPELINE INTEGRATION")
    print("=" * 65)

    if not RAW_FILE.is_file():
        raise FileNotFoundError(
            f"Lecturer dataset not found: {RAW_FILE}"
        )

    # ---------------------------------------------------------
    # STEP 1: Run the existing cleaning and temporal split flow.
    # ---------------------------------------------------------
    print("\nSTEP 1: Preparing and validating the dataset...")

    prepare_temporal_splits()

    cleaned_rows = count_csv_rows(CLEANED_FILE)
    train_rows = count_csv_rows(TRAIN_FILE)
    validation_rows = count_csv_rows(VALIDATION_FILE)
    test_rows = count_csv_rows(TEST_FILE)
    prepared_rows = count_csv_rows(PREPARED_FILE)

    split_rows = train_rows + validation_rows + test_rows

    preparation_checks = {
        "Cleaned dataset generated": cleaned_rows > 0,
        "Training split generated": train_rows > 0,
        "Validation split generated": validation_rows > 0,
        "Test split generated": test_rows > 0,
        "Split rows match prepared dataset": (
            split_rows == prepared_rows
        ),
    }

    print("\nData preparation checks:")
    for name, passed in preparation_checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")

    if not all(preparation_checks.values()):
        raise RuntimeError(
            "Data preparation integration checks failed."
        )

    # ---------------------------------------------------------
    # STEP 2: Import the cleaned data into SQLite.
    # ---------------------------------------------------------
    print("\nSTEP 2: Integrating the cleaned dataset with SQLite...")

    imported_rows = initialize_database(
        force_reload=force_reload,
        csv_path=CLEANED_FILE,
    )

    database_summary = get_inventory_summary()

    database_checks = {
        "SQLite import matches cleaned dataset": (
            imported_rows == cleaned_rows
        ),
        "Database record count matches cleaned dataset": (
            database_summary["records"] == cleaned_rows
        ),
    }

    print("\nDatabase integration checks:")
    for name, passed in database_checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")

    if not all(database_checks.values()):
        raise RuntimeError(
            "SQLite integration checks failed."
        )

    # ---------------------------------------------------------
    # STEP 3: Generate M14-02 integration evidence.
    # ---------------------------------------------------------
    all_checks = {
        **preparation_checks,
        **database_checks,
    }

    report = f"""# M14-02 - Python Data Pipeline Integration Report

## Integration overview

The existing Python data preparation pipeline was connected to the
SQLite inventory database.

The integration uses the lecturer-provided dataset and the existing
cleaning and chronological train/validation/test split process.

## Dataset information

- Raw dataset: `{relative_path(RAW_FILE)}`
- Cleaned dataset: `{relative_path(CLEANED_FILE)}`
- Raw dataset records: {count_csv_rows(RAW_FILE):,}
- Cleaned dataset records: {cleaned_rows:,}

## Temporal split results

| Dataset | Records |
|---|---:|
| Training | {train_rows:,} |
| Validation | {validation_rows:,} |
| Test | {test_rows:,} |
| Combined splits | {split_rows:,} |
| Prepared dataset | {prepared_rows:,} |

## SQLite integration

- Imported records: {imported_rows:,}
- Database records: {database_summary['records']:,}
- Distinct stores: {database_summary['stores']:,}
- Distinct products: {database_summary['products']:,}
- Distinct categories: {database_summary['categories']:,}
- Forced reload: {force_reload}

## Validation evidence

| Check | Result |
|---|---|
"""

    for name, passed in all_checks.items():
        report += (
            f"| {name} | {'PASS' if passed else 'FAIL'} |\n"
        )

    report += """
## Result

All M14-02 pipeline integration checks passed.

The cleaned inventory dataset was successfully imported into SQLite,
and the database record count was verified against the cleaned dataset.
"""

    REPORT_FILE.write_text(report, encoding="utf-8")

    # ---------------------------------------------------------
    # STEP 4: Display final results.
    # ---------------------------------------------------------
    print("\n" + "=" * 65)
    print("M14-02 PIPELINE INTEGRATION COMPLETED")
    print("=" * 65)

    print(f"Cleaned records: {cleaned_rows:,}")
    print(f"Training records: {train_rows:,}")
    print(f"Validation records: {validation_rows:,}")
    print(f"Test records: {test_rows:,}")
    print(f"SQLite records: {database_summary['records']:,}")

    print("\nDatabase summary:")
    for key, value in database_summary.items():
        print(f"{key.capitalize()}: {value:,}")

    print(f"\nIntegration report: {REPORT_FILE}")

    return {
        "cleaned_rows": cleaned_rows,
        "split_rows": split_rows,
        "imported_rows": imported_rows,
        "database_summary": database_summary,
        "checks": all_checks,
        "report": REPORT_FILE,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Run the RetailAI M14-02 integrated data pipeline."
    )

    parser.add_argument(
        "--force-reload",
        action="store_true",
        help="Force the SQLite database to reload the cleaned dataset.",
    )

    args = parser.parse_args()

    run_pipeline(force_reload=args.force_reload)


if __name__ == "__main__":
    main()
