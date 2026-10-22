
"""M10-03: Prepare leakage-safe features for retail demand forecasting."""

import pandas as pd


TARGET_COLUMN = "Units Sold"

# Exclude these columns because they may reveal information from
# after the day's sales or directly encode the forecasting outcome.
EXCLUDED_COLUMNS = [
    "Demand Forecast",
    "Units Ordered",
    "Inventory Level",
]

CATEGORICAL_COLUMNS = [
    "Store ID",
    "Product ID",
    "Category",
    "Region",
    "Weather Condition",
    "Seasonality",
]

NUMERIC_COLUMNS = [
    "Price",
    "Discount",
    "Competitor Pricing",
    "Holiday/Promotion",
]

REQUIRED_COLUMNS = [
    "Date",
    TARGET_COLUMN,
    *CATEGORICAL_COLUMNS,
    *NUMERIC_COLUMNS,
]


def prepare_forecasting_data(df, train_fraction=0.8):
    """Create numeric forecasting features and a chronological split."""

    if not 0 < train_fraction < 1:
        raise ValueError("train_fraction must be between 0 and 1.")

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    data = df.copy()
    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
    data[TARGET_COLUMN] = pd.to_numeric(
        data[TARGET_COLUMN], errors="coerce"
    )

    # Rows without a valid date or target cannot be used for forecasting.
    before = len(data)
    data = data.dropna(subset=["Date", TARGET_COLUMN]).copy()
    dropped_rows = before - len(data)

    data["Date"] = data["Date"].dt.normalize()
    data = data.sort_values(
        ["Date", "Store ID", "Product ID"]
    ).reset_index(drop=True)

    unique_dates = data["Date"].drop_duplicates().tolist()
    if len(unique_dates) < 2:
        raise ValueError(
            "At least two different dates are required for a "
            "chronological train/test split."
        )

    # Split by date so observations from the same day are not split
    # between training and testing.
    split_index = int(len(unique_dates) * train_fraction)
    split_index = max(1, min(split_index, len(unique_dates) - 1))
    cutoff_date = unique_dates[split_index]

    train_mask = data["Date"] < cutoff_date
    test_mask = data["Date"] >= cutoff_date

    # Create calendar features using information from Date.
    data["day_of_week"] = data["Date"].dt.dayofweek
    data["day_of_month"] = data["Date"].dt.day
    data["month"] = data["Date"].dt.month
    data["quarter"] = data["Date"].dt.quarter
    data["day_of_year"] = data["Date"].dt.dayofyear
    data["week_of_year"] = (
        data["Date"].dt.isocalendar().week.astype(int)
    )
    data["is_weekend"] = (
        data["Date"].dt.dayofweek >= 5
    ).astype(int)

    calendar_columns = [
        "day_of_week",
        "day_of_month",
        "month",
        "quarter",
        "day_of_year",
        "week_of_year",
        "is_weekend",
    ]

    numeric_features = NUMERIC_COLUMNS + calendar_columns

    # Convert numeric fields and learn missing-value replacements
    # from the training period only.
    for col in NUMERIC_COLUMNS:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    train_numeric = data.loc[train_mask, numeric_features].copy()
    test_numeric = data.loc[test_mask, numeric_features].copy()

    medians = train_numeric.median().fillna(0)
    train_numeric = train_numeric.fillna(medians)
    test_numeric = test_numeric.fillna(medians)

    # One-hot encode categories. Align test columns to training columns
    # so the model receives the same feature layout in both datasets.
    train_categories = data.loc[
        train_mask, CATEGORICAL_COLUMNS
    ].fillna("Unknown").astype(str)

    test_categories = data.loc[
        test_mask, CATEGORICAL_COLUMNS
    ].fillna("Unknown").astype(str)

    train_encoded = pd.get_dummies(
        train_categories, dtype=int
    )
    test_encoded = pd.get_dummies(
        test_categories, dtype=int
    )

    test_encoded = test_encoded.reindex(
        columns=train_encoded.columns,
        fill_value=0,
    )

    train_features = pd.concat(
        [
            train_numeric.reset_index(drop=True),
            train_encoded.reset_index(drop=True),
        ],
        axis=1,
    )

    test_features = pd.concat(
        [
            test_numeric.reset_index(drop=True),
            test_encoded.reset_index(drop=True),
        ],
        axis=1,
    )

    def assemble_output(mask, features):
        output = data.loc[
            mask, ["Date", TARGET_COLUMN]
        ].reset_index(drop=True)

        return pd.concat(
            [output, features.reset_index(drop=True)],
            axis=1,
        )

    train_output = assemble_output(train_mask, train_features)
    test_output = assemble_output(test_mask, test_features)

    prepared_output = pd.concat(
        [train_output, test_output], ignore_index=True
    ).sort_values("Date").reset_index(drop=True)

    metadata = {
        "input_rows": before,
        "usable_rows": len(data),
        "dropped_rows": dropped_rows,
        "unique_dates": len(unique_dates),
        "cutoff_date": cutoff_date,
        "train_rows": len(train_output),
        "test_rows": len(test_output),
        "train_start": train_output["Date"].min(),
        "train_end": train_output["Date"].max(),
        "test_start": test_output["Date"].min(),
        "test_end": test_output["Date"].max(),
        "feature_columns": train_features.columns.tolist(),
        "excluded_columns": EXCLUDED_COLUMNS,
        "target_column": TARGET_COLUMN,
    }

    return train_output, test_output, prepared_output, metadata
