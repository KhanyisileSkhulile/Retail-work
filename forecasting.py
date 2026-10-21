import pandas as pd
import numpy as np
from pathlib import Path

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error
)

import warnings

warnings.filterwarnings("ignore")


# ============================================================
# RETAILAI - AI DEMAND FORECASTING
# Lecturer Dataset Version
#
# Model:
# Random Forest Regressor
#
# Forecast level:
# Store ID + Product ID
# ============================================================


DATA_FILE = "retail_store_inventory.csv"

FORECAST_OUTPUT = "retailai_forecasts.csv"

MODEL_OUTPUT = "retailai_model_evaluation.csv"

FORECAST_DAYS = 7

TEST_DAYS = 30

RANDOM_STATE = 42


# ============================================================
# CHECK DATASET
# ============================================================

if not Path(DATA_FILE).exists():

    raise FileNotFoundError(
        f"{DATA_FILE} was not found.\n"
        "Place the lecturer dataset in the same folder."
    )


# ============================================================
# LOAD DATA
# ============================================================

print("\n" + "=" * 70)

print("RETAILAI - MACHINE LEARNING DEMAND FORECASTING")

print("=" * 70)

print("\nLoading lecturer dataset...")


df = pd.read_csv(DATA_FILE)


print(
    f"Records loaded: {len(df):,}"
)


# ============================================================
# CHECK REQUIRED COLUMNS
# ============================================================

required_columns = [
    "Date",
    "Store ID",
    "Product ID",
    "Units Sold",
    "Demand Forecast"
]


missing = [
    column
    for column in required_columns
    if column not in df.columns
]


if missing:

    raise ValueError(
        "Missing columns:\n"
        + "\n".join(missing)
    )


# ============================================================
# CLEAN DATA
# ============================================================

df["Date"] = pd.to_datetime(
    df["Date"],
    errors="coerce"
)


df["Units Sold"] = pd.to_numeric(
    df["Units Sold"],
    errors="coerce"
)


df["Demand Forecast"] = pd.to_numeric(
    df["Demand Forecast"],
    errors="coerce"
)


df = df.dropna(
    subset=[
        "Date",
        "Store ID",
        "Product ID",
        "Units Sold"
    ]
)


df = df.sort_values(
    [
        "Store ID",
        "Product ID",
        "Date"
    ]
).reset_index(drop=True)


print(
    f"Stores: {df['Store ID'].nunique()}"
)

print(
    f"Products: {df['Product ID'].nunique()}"
)


combinations = (
    df[
        [
            "Store ID",
            "Product ID"
        ]
    ]
    .drop_duplicates()
)


print(
    f"Store-product combinations: "
    f"{len(combinations)}"
)


# ============================================================
# CREATE MACHINE LEARNING FEATURES
# ============================================================

print("\nCreating machine learning features...")


# ------------------------------------------------------------
# Calendar features
# ------------------------------------------------------------

df["DayOfWeek"] = (
    df["Date"].dt.dayofweek
)

df["DayOfMonth"] = (
    df["Date"].dt.day
)

df["Month"] = (
    df["Date"].dt.month
)

df["DayOfYear"] = (
    df["Date"].dt.dayofyear
)


# ------------------------------------------------------------
# Historical sales features
# ------------------------------------------------------------

group = df.groupby(
    [
        "Store ID",
        "Product ID"
    ]
)["Units Sold"]


# Yesterday's sales
df["Lag_1"] = group.shift(1)


# Sales one week ago
df["Lag_7"] = group.shift(7)


# Sales two weeks ago
df["Lag_14"] = group.shift(14)


# ------------------------------------------------------------
# Rolling average
# shift(1) prevents using today's actual sales
# ------------------------------------------------------------

df["Rolling_Mean_7"] = (
    group
    .transform(
        lambda x:
        x.shift(1)
        .rolling(7)
        .mean()
    )
)


df["Rolling_Mean_14"] = (
    group
    .transform(
        lambda x:
        x.shift(1)
        .rolling(14)
        .mean()
    )
)


# ------------------------------------------------------------
# Rolling standard deviation
# ------------------------------------------------------------

df["Rolling_Std_7"] = (
    group
    .transform(
        lambda x:
        x.shift(1)
        .rolling(7)
        .std()
    )
)


# ============================================================
# ENCODE STORE AND PRODUCT
# ============================================================

store_categories = sorted(
    df["Store ID"].unique()
)

product_categories = sorted(
    df["Product ID"].unique()
)


store_mapping = {
    store: number
    for number, store
    in enumerate(store_categories)
}


product_mapping = {
    product: number
    for number, product
    in enumerate(product_categories)
}


df["Store_Code"] = (
    df["Store ID"]
    .map(store_mapping)
)


df["Product_Code"] = (
    df["Product ID"]
    .map(product_mapping)
)


# ============================================================
# FEATURE LIST
# ============================================================

feature_columns = [

    "Store_Code",

    "Product_Code",

    "DayOfWeek",

    "DayOfMonth",

    "Month",

    "DayOfYear",

    "Lag_1",

    "Lag_7",

    "Lag_14",

    "Rolling_Mean_7",

    "Rolling_Mean_14",

    "Rolling_Std_7"
]


# Remove rows without enough historical information

model_df = df.dropna(
    subset=feature_columns
).copy()


print(
    f"Usable ML records: "
    f"{len(model_df):,}"
)


# ============================================================
# TIME-BASED TRAIN TEST SPLIT
# ============================================================

latest_date = model_df[
    "Date"
].max()


test_start_date = (
    latest_date
    - pd.Timedelta(
        days=TEST_DAYS - 1
    )
)


train_df = model_df[
    model_df["Date"]
    < test_start_date
].copy()


test_df = model_df[
    model_df["Date"]
    >= test_start_date
].copy()


print("\n" + "=" * 70)

print("TRAIN / TEST SPLIT")

print("=" * 70)


print(
    f"Training records: "
    f"{len(train_df):,}"
)


print(
    f"Testing records: "
    f"{len(test_df):,}"
)


print(
    f"Testing period: "
    f"{test_start_date.date()} "
    f"to {latest_date.date()}"
)


# ============================================================
# TRAIN RANDOM FOREST
# ============================================================

print("\n" + "=" * 70)

print("TRAINING RANDOM FOREST MODEL")

print("=" * 70)


X_train = train_df[
    feature_columns
]


y_train = train_df[
    "Units Sold"
]


X_test = test_df[
    feature_columns
]


y_test = test_df[
    "Units Sold"
]


model = RandomForestRegressor(

    n_estimators=200,

    max_depth=18,

    min_samples_split=4,

    min_samples_leaf=2,

    random_state=RANDOM_STATE,

    n_jobs=-1
)


print(
    "\nTraining AI model..."
)


model.fit(
    X_train,
    y_train
)


print(
    "Training completed."
)


# ============================================================
# TEST OUR AI MODEL
# ============================================================

print(
    "\nEvaluating AI model..."
)


ai_predictions = model.predict(
    X_test
)


# Prevent negative demand
ai_predictions = np.maximum(
    ai_predictions,
    0
)


test_df["AI_Prediction"] = (
    ai_predictions
)


# ============================================================
# OUR MODEL PERFORMANCE
# ============================================================

our_mae = mean_absolute_error(
    y_test,
    ai_predictions
)


our_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        ai_predictions
    )
)


# ============================================================
# DATASET FORECAST PERFORMANCE
# ============================================================

dataset_test = test_df.dropna(
    subset=[
        "Demand Forecast"
    ]
)


dataset_mae = mean_absolute_error(

    dataset_test[
        "Units Sold"
    ],

    dataset_test[
        "Demand Forecast"
    ]
)


dataset_rmse = np.sqrt(

    mean_squared_error(

        dataset_test[
            "Units Sold"
        ],

        dataset_test[
            "Demand Forecast"
        ]
    )
)


# ============================================================
# DISPLAY OVERALL RESULTS
# ============================================================

print("\n" + "=" * 70)

print("OVERALL MODEL PERFORMANCE")

print("=" * 70)


print(
    f"Our Random Forest MAE: "
    f"{our_mae:.2f}"
)


print(
    f"Our Random Forest RMSE: "
    f"{our_rmse:.2f}"
)


print(
    f"Dataset Forecast MAE: "
    f"{dataset_mae:.2f}"
)


print(
    f"Dataset Forecast RMSE: "
    f"{dataset_rmse:.2f}"
)


# ============================================================
# PERFORMANCE BY PRODUCT
# ============================================================

evaluation_results = []


for product in sorted(
    test_df["Product ID"].unique()
):

    product_test = test_df[
        test_df[
            "Product ID"
        ] == product
    ]


    if product_test.empty:
        continue


    # Our model
    product_our_mae = (
        mean_absolute_error(

            product_test[
                "Units Sold"
            ],

            product_test[
                "AI_Prediction"
            ]
        )
    )


    product_our_rmse = np.sqrt(

        mean_squared_error(

            product_test[
                "Units Sold"
            ],

            product_test[
                "AI_Prediction"
            ]
        )
    )


    # Dataset forecast
    valid_dataset = (
        product_test
        .dropna(
            subset=[
                "Demand Forecast"
            ]
        )
    )


    if not valid_dataset.empty:

        product_dataset_mae = (
            mean_absolute_error(

                valid_dataset[
                    "Units Sold"
                ],

                valid_dataset[
                    "Demand Forecast"
                ]
            )
        )


        product_dataset_rmse = np.sqrt(

            mean_squared_error(

                valid_dataset[
                    "Units Sold"
                ],

                valid_dataset[
                    "Demand Forecast"
                ]
            )
        )

    else:

        product_dataset_mae = np.nan

        product_dataset_rmse = np.nan


    evaluation_results.append(

        {
            "Product_ID":
                product,

            "Our_Model_MAE":
                round(
                    product_our_mae,
                    2
                ),

            "Our_Model_RMSE":
                round(
                    product_our_rmse,
                    2
                ),

            "Dataset_Forecast_MAE":
                round(
                    product_dataset_mae,
                    2
                ),

            "Dataset_Forecast_RMSE":
                round(
                    product_dataset_rmse,
                    2
                )
        }

    )


evaluation_df = pd.DataFrame(
    evaluation_results
)


# ============================================================
# ADD OVERALL PERFORMANCE ROW
# ============================================================

overall_row = pd.DataFrame(

    [
        {
            "Product_ID":
                "OVERALL",

            "Our_Model_MAE":
                round(
                    our_mae,
                    2
                ),

            "Our_Model_RMSE":
                round(
                    our_rmse,
                    2
                ),

            "Dataset_Forecast_MAE":
                round(
                    dataset_mae,
                    2
                ),

            "Dataset_Forecast_RMSE":
                round(
                    dataset_rmse,
                    2
                )
        }
    ]

)


evaluation_df = pd.concat(

    [
        evaluation_df,
        overall_row
    ],

    ignore_index=True

)


# ============================================================
# DISPLAY PRODUCT PERFORMANCE
# ============================================================

print("\n" + "=" * 70)

print("MODEL PERFORMANCE BY PRODUCT")

print("=" * 70)


print(
    evaluation_df.to_string(
        index=False
    )
)


# ============================================================
# FUTURE 7-DAY FORECAST
# ============================================================

print("\n" + "=" * 70)

print("CREATING FUTURE 7-DAY FORECAST")

print("=" * 70)


forecast_results = []


# ============================================================
# FORECAST STORE + PRODUCT COMBINATIONS
# ============================================================

for _, combination in combinations.iterrows():

    store = combination[
        "Store ID"
    ]

    product = combination[
        "Product ID"
    ]


    historical = df[
        (
            df["Store ID"]
            == store
        )
        &
        (
            df["Product ID"]
            == product
        )
    ].sort_values(
        "Date"
    ).copy()


    # Need enough history
    if len(historical) < 14:

        continue


    sales_history = (
        historical[
            "Units Sold"
        ]
        .astype(float)
        .tolist()
    )


    last_date = (
        historical[
            "Date"
        ].max()
    )


    # --------------------------------------------------------
    # Recursive 7-day forecasting
    # --------------------------------------------------------

    for day in range(
        1,
        FORECAST_DAYS + 1
    ):

        future_date = (
            last_date
            + pd.Timedelta(
                days=day
            )
        )


        # ----------------------------------------------
        # Lag calculations
        # ----------------------------------------------

        lag_1 = (
            sales_history[-1]
        )


        lag_7 = (
            sales_history[-7]
        )


        lag_14 = (
            sales_history[-14]
        )


        rolling_mean_7 = (
            np.mean(
                sales_history[-7:]
            )
        )


        rolling_mean_14 = (
            np.mean(
                sales_history[-14:]
            )
        )


        rolling_std_7 = (
            np.std(
                sales_history[-7:],
                ddof=1
            )
        )


        # Prevent NaN std
        if np.isnan(
            rolling_std_7
        ):

            rolling_std_7 = 0


        # ----------------------------------------------
        # Future feature row
        # ----------------------------------------------

        future_features = pd.DataFrame(

            [
                {
                    "Store_Code":
                        store_mapping[
                            store
                        ],

                    "Product_Code":
                        product_mapping[
                            product
                        ],

                    "DayOfWeek":
                        future_date.dayofweek,

                    "DayOfMonth":
                        future_date.day,

                    "Month":
                        future_date.month,

                    "DayOfYear":
                        future_date.dayofyear,

                    "Lag_1":
                        lag_1,

                    "Lag_7":
                        lag_7,

                    "Lag_14":
                        lag_14,

                    "Rolling_Mean_7":
                        rolling_mean_7,

                    "Rolling_Mean_14":
                        rolling_mean_14,

                    "Rolling_Std_7":
                        rolling_std_7
                }
            ]

        )


        prediction = model.predict(
            future_features[
                feature_columns
            ]
        )[0]


        prediction = max(
            prediction,
            0
        )


        # Add predicted value so it becomes
        # part of the history for the next day
        sales_history.append(
            prediction
        )


        forecast_results.append(

            {
                "Date":
                    future_date,

                "Store_ID":
                    store,

                "Product_ID":
                    product,

                "Predicted_Units_Sold":
                    round(
                        float(
                            prediction
                        ),
                        2
                    )
            }

        )


# ============================================================
# SAVE FUTURE FORECAST
# ============================================================

forecast_df = pd.DataFrame(
    forecast_results
)


forecast_df.to_csv(
    FORECAST_OUTPUT,
    index=False
)


evaluation_df.to_csv(
    MODEL_OUTPUT,
    index=False
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)

print("FORECASTING COMPLETE")

print("=" * 70)


print(
    f"Store-product combinations: "
    f"{len(combinations)}"
)


print(
    f"Forecast horizon: "
    f"{FORECAST_DAYS} days"
)


print(
    f"Forecast records created: "
    f"{len(forecast_df):,}"
)


print(
    f"\nExpected maximum records: "
    f"{len(combinations) * FORECAST_DAYS:,}"
)


print("\nFiles created:")


print(
    f"- {FORECAST_OUTPUT}"
)


print(
    f"- {MODEL_OUTPUT}"
)


print("\n" + "=" * 70)

print("FINAL PERFORMANCE")

print("=" * 70)


print(
    f"Our AI Model MAE: "
    f"{our_mae:.2f}"
)


print(
    f"Our AI Model RMSE: "
    f"{our_rmse:.2f}"
)


print(
    f"Dataset Forecast MAE: "
    f"{dataset_mae:.2f}"
)


print(
    f"Dataset Forecast RMSE: "
    f"{dataset_rmse:.2f}"
)


print("=" * 70)