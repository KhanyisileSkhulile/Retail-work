
"""M10-03: Prepare model-ready forecasting datasets and evidence."""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FORECASTING_DIR = REPO_ROOT / "python-ai" / "forecasting"

sys.path.insert(0, str(FORECASTING_DIR))

from clean_data import clean_and_validate
from feature_engineering import prepare_forecasting_data


OUTPUT_DIR = REPO_ROOT / "dataset" / "processed"

TRAIN_FILE = OUTPUT_DIR / "retail_forecasting_train.csv"
TEST_FILE = OUTPUT_DIR / "retail_forecasting_test.csv"
PREPARED_FILE = OUTPUT_DIR / "retail_forecasting_features.csv"

REPORT_FILE = (
    Path(__file__).resolve().parent
    / "M10-03-feature-preparation-report.md"
)


def main():
    print("\n" + "=" * 60)
    print("RETAILAI - FORECASTING FEATURE PREPARATION")
    print("=" * 60)

    # Rebuild the cleaned dataset from the approved raw source.
    cleaned = clean_and_validate()

    train_df, test_df, prepared_df, metadata = (
        prepare_forecasting_data(cleaned)
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    train_df.to_csv(
        TRAIN_FILE, index=False, date_format="%Y-%m-%d"
    )
    test_df.to_csv(
        TEST_FILE, index=False, date_format="%Y-%m-%d"
    )
    prepared_df.to_csv(
        PREPARED_FILE, index=False, date_format="%Y-%m-%d"
    )

    feature_columns = metadata["feature_columns"]

    report = [
        "# M10-03 — Forecasting Feature Preparation",
        "",
        "- **Source:** `dataset/raw/retail_store_inventory.csv`",
        "- **Cleaning stage:** `python-ai/data/clean_data.py`",
        "- **Feature engineering:** "
        "`python-ai/forecasting/feature_engineering.py`",
        f"- **Target:** `{metadata['target_column']}`",
        f"- **Input rows:** {metadata['input_rows']:,}",
        f"- **Usable rows:** {metadata['usable_rows']:,}",
        f"- **Rows dropped for invalid Date/target:** "
        f"{metadata['dropped_rows']:,}",
        f"- **Unique dates:** {metadata['unique_dates']:,}",
        f"- **Training rows:** {metadata['train_rows']:,}",
        f"- **Testing rows:** {metadata['test_rows']:,}",
        f"- **Feature count:** {len(feature_columns):,}",
        f"- **Training date range:** "
        f"{metadata['train_start'].date()} to "
        f"{metadata['train_end'].date()}",
        f"- **Testing date range:** "
        f"{metadata['test_start'].date()} to "
        f"{metadata['test_end'].date()}",
        f"- **First test date (cutoff):** "
        f"{metadata['cutoff_date'].date()}",
        "",
        "## Excluded columns",
        "",
        "These fields are excluded from model inputs because of "
        "potential target leakage or uncertain measurement timing:",
        "",
    ]

    report.extend(
        f"- `{column}`"
        for column in metadata["excluded_columns"]
    )

    report.extend([
        "",
        "## Engineered calendar features",
        "",
        "- `day_of_week`",
        "- `day_of_month`",
        "- `month`",
        "- `quarter`",
        "- `day_of_year`",
        "- `week_of_year`",
        "- `is_weekend`",
        "",
        "Categorical variables are one-hot encoded. Numeric missing "
        "values are imputed using training-period medians. Test "
        "categories not seen in training are ignored so that training "
        "and testing have identical feature columns.",
        "",
        "## Model feature columns",
        "",
    ])

    report.extend(f"- `{column}`" for column in feature_columns)

    report.extend([
        "",
        "## Generated outputs",
        "",
        f"- `{TRAIN_FILE.relative_to(REPO_ROOT)}`",
        f"- `{TEST_FILE.relative_to(REPO_ROOT)}`",
        f"- `{PREPARED_FILE.relative_to(REPO_ROOT)}`",
        "",
        "Generated CSV files are local processed artifacts and are "
        "not committed. This report and the scripts provide "
        "reproducible evidence.",
        "",
    ])

    REPORT_FILE.write_text(
        "\n".join(report),
        encoding="utf-8",
    )

    print(f"\nTarget: {metadata['target_column']}")
    print(f"Training rows: {metadata['train_rows']:,}")
    print(f"Testing rows: {metadata['test_rows']:,}")
    print(f"Features: {len(feature_columns):,}")

    print(
        "Train date range: "
        f"{metadata['train_start'].date()} to "
        f"{metadata['train_end'].date()}"
    )
    print(
        "Test date range: "
        f"{metadata['test_start'].date()} to "
        f"{metadata['test_end'].date()}"
    )

    print(f"\nTrain data: {TRAIN_FILE}")
    print(f"Test data: {TEST_FILE}")
    print(f"Prepared data: {PREPARED_FILE}")
    print(f"Evidence report: {REPORT_FILE}")


if __name__ == "__main__":
    main()
