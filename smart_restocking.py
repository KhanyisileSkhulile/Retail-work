import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# RETAILAI - SMART RESTOCKING SYSTEM
# Lecturer Dataset Version
# ============================================================

DATA_FILE = "retail_store_inventory.csv"
OUTPUT_FILE = "retailai_restocking_recommendations.csv"

RECENT_DAYS = 30
LEAD_TIME_DAYS = 1
TARGET_STOCK_DAYS = 3
SAFETY_STOCK_FACTOR = 1.0


# ============================================================
# CHECK FILE
# ============================================================

if not Path(DATA_FILE).exists():

    raise FileNotFoundError(
        f"{DATA_FILE} was not found.\n"
        "Make sure it is in the same folder as smart_restocking.py"
    )


# ============================================================
# LOAD DATA
# ============================================================

print("\n" + "=" * 70)
print("RETAILAI - SMART RESTOCKING SYSTEM")
print("=" * 70)

print("\nLoading lecturer dataset...")

df = pd.read_csv(DATA_FILE)

print(f"Records loaded: {len(df):,}")


# ============================================================
# CHECK REQUIRED COLUMNS
# ============================================================

required_columns = [
    "Date",
    "Store ID",
    "Product ID",
    "Category",
    "Inventory Level",
    "Units Sold",
    "Units Ordered",
    "Demand Forecast"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:

    raise ValueError(
        "Missing required columns:\n"
        + "\n".join(missing_columns)
    )


# ============================================================
# CLEAN DATA
# ============================================================

df["Date"] = pd.to_datetime(
    df["Date"],
    errors="coerce"
)

numeric_columns = [
    "Inventory Level",
    "Units Sold",
    "Units Ordered",
    "Demand Forecast"
]

for column in numeric_columns:

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


df = df.dropna(
    subset=[
        "Date",
        "Store ID",
        "Product ID",
        "Inventory Level",
        "Units Sold",
        "Demand Forecast"
    ]
)


# ============================================================
# LATEST DATE
# ============================================================

latest_date = df["Date"].max()

recent_start_date = (
    latest_date
    - pd.Timedelta(days=RECENT_DAYS - 1)
)

print(
    f"Latest dataset date: {latest_date.date()}"
)

print(
    f"Recent analysis period: "
    f"{recent_start_date.date()} to {latest_date.date()}"
)


# ============================================================
# CURRENT INVENTORY
# ============================================================

latest_records = (
    df.sort_values("Date")
    .groupby(
        [
            "Store ID",
            "Product ID"
        ]
    )
    .tail(1)
    .copy()
)


current_inventory = latest_records[
    [
        "Store ID",
        "Product ID",
        "Category",
        "Inventory Level",
        "Units Ordered",
        "Demand Forecast"
    ]
].copy()


current_inventory = current_inventory.rename(
    columns={
        "Inventory Level":
            "Current_Inventory",

        "Units Ordered":
            "Latest_Units_Ordered",

        "Demand Forecast":
            "Current_Demand_Forecast"
    }
)


# ============================================================
# RECENT SALES HISTORY
# ============================================================

recent_df = df[
    df["Date"] >= recent_start_date
].copy()


recent_sales = (
    recent_df
    .groupby(
        [
            "Store ID",
            "Product ID"
        ]
    )
    .agg(
        Recent_Units_Sold=(
            "Units Sold",
            "sum"
        ),

        Average_Daily_Sales=(
            "Units Sold",
            "mean"
        ),

        Sales_Std_Dev=(
            "Units Sold",
            "std"
        ),

        Average_Demand_Forecast=(
            "Demand Forecast",
            "mean"
        ),

        Average_Units_Ordered=(
            "Units Ordered",
            "mean"
        )
    )
    .reset_index()
)


recent_sales["Sales_Std_Dev"] = (
    recent_sales[
        "Sales_Std_Dev"
    ].fillna(0)
)


# ============================================================
# MERGE CURRENT + RECENT DATA
# ============================================================

restock_df = current_inventory.merge(
    recent_sales,
    on=[
        "Store ID",
        "Product ID"
    ],
    how="left"
)


# ============================================================
# SAFETY STOCK
# ============================================================

restock_df["Safety_Stock"] = (

    restock_df[
        "Sales_Std_Dev"
    ]

    * SAFETY_STOCK_FACTOR

    * np.sqrt(
        LEAD_TIME_DAYS
    )
)


# ============================================================
# REORDER POINT
# ============================================================

restock_df["Reorder_Point"] = (

    restock_df[
        "Average_Demand_Forecast"
    ]

    * LEAD_TIME_DAYS

    + restock_df[
        "Safety_Stock"
    ]
)


# ============================================================
# DAILY DEMAND ESTIMATE
# ============================================================

restock_df[
    "Daily_Forecast_Demand"
] = restock_df[
    "Average_Demand_Forecast"
]

# ============================================================
# TARGET STOCK LEVEL
# Keep approximately 3 days of expected demand
# ============================================================

restock_df[
    "Recommended_Stock_Level"
] = (

    restock_df[
        "Daily_Forecast_Demand"
    ]
    * TARGET_STOCK_DAYS

    + restock_df[
        "Safety_Stock"
    ]
)

# ============================================================
# RECOMMENDED ORDER QUANTITY
# ============================================================

restock_df[
    "Recommended_Order_Quantity"
] = (

    restock_df[
        "Recommended_Stock_Level"
    ]

    - restock_df[
        "Current_Inventory"
    ]
)


restock_df[
    "Recommended_Order_Quantity"
] = (

    restock_df[
        "Recommended_Order_Quantity"
    ]

    .clip(lower=0)

    .apply(np.ceil)

    .astype(int)
)


# ============================================================
# DAYS OF STOCK COVER
# ============================================================

restock_df[
    "Estimated_Days_Remaining"
] = np.where(

    restock_df[
        "Daily_Forecast_Demand"
    ] > 0,

    restock_df[
        "Current_Inventory"
    ]
    /
    restock_df[
        "Daily_Forecast_Demand"
    ],

    np.inf
)

# ============================================================
# DAYS OF STOCK REMAINING
# ============================================================

restock_df[
    "Estimated_Days_Remaining"
] = np.where(

    restock_df[
        "Average_Demand_Forecast"
    ] > 0,

    restock_df[
        "Current_Inventory"
    ]
    /
    restock_df[
        "Average_Demand_Forecast"
    ],

    np.inf
)


# ============================================================
# STOCKOUT RISK
# ============================================================

def calculate_stockout_risk(row):

    current_stock = row[
        "Current_Inventory"
    ]

    days_remaining = row[
        "Estimated_Days_Remaining"
    ]


    if current_stock <= 0:

        return "CRITICAL"


    elif days_remaining <= 0.5:

        return "CRITICAL"


    elif days_remaining <= 1:

        return "HIGH"


    elif days_remaining <= 2:

        return "MEDIUM"


    else:

        return "LOW"


restock_df[
    "Stockout_Risk"
] = restock_df.apply(
    calculate_stockout_risk,
    axis=1
)


# ============================================================
# DEMAND TREND
# ============================================================

# Compare recent actual average sales with
# average forecast demand

def calculate_demand_trend(row):

    actual = row[
        "Average_Daily_Sales"
    ]

    forecast = row[
        "Average_Demand_Forecast"
    ]


    if actual == 0:

        return "STABLE"


    difference = (
        forecast - actual
    ) / actual


    if difference > 0.10:

        return "INCREASING"


    elif difference < -0.10:

        return "DECREASING"


    else:

        return "STABLE"


restock_df[
    "Demand_Trend"
] = restock_df.apply(
    calculate_demand_trend,
    axis=1
)


# ============================================================
# STATUS
# ============================================================

def calculate_status(row):

    risk = row[
        "Stockout_Risk"
    ]

    order_qty = row[
        "Recommended_Order_Quantity"
    ]


    if risk == "CRITICAL":

        return "URGENT RESTOCK"


    elif risk == "HIGH":

        return "ORDER IMMEDIATELY"


    elif risk == "MEDIUM":

        return "REORDER SOON"


    elif order_qty > 0:

        return "RESTOCK RECOMMENDED"


    else:

        return "STOCK HEALTHY"


restock_df[
    "Status"
] = restock_df.apply(
    calculate_status,
    axis=1
)


# ============================================================
# PRIORITY
# ============================================================

priority_map = {
    "CRITICAL": 1,
    "HIGH": 2,
    "MEDIUM": 3,
    "LOW": 4
}


restock_df[
    "Priority"
] = restock_df[
    "Stockout_Risk"
].map(
    priority_map
)


# ============================================================
# ROUND VALUES
# ============================================================

round_columns = [
    "Average_Daily_Sales",
    "Sales_Std_Dev",
    "Average_Demand_Forecast",
    "Daily_Forecast_Demand",
    "Safety_Stock",
    "Reorder_Point",
    "Recommended_Stock_Level",
    "Estimated_Days_Remaining",
    "Average_Units_Ordered"
]

for column in round_columns:

    if column in restock_df.columns:

        restock_df[column] = (
            restock_df[column]
            .round(2)
        )


# ============================================================
# SORT
# ============================================================

restock_df = restock_df.sort_values(
    by=[
        "Priority",
        "Recommended_Order_Quantity"
    ],
    ascending=[
        True,
        False
    ]
)


# ============================================================
# SELECT OUTPUT COLUMNS
# ============================================================

output_columns = [
    "Store ID",
    "Product ID",
    "Category",
    "Current_Inventory",
    "Recent_Units_Sold",
    "Average_Daily_Sales",
    "Average_Demand_Forecast",
    "Daily_Forecast_Demand",
    "Safety_Stock",
    "Reorder_Point",
    "Recommended_Stock_Level",
    "Recommended_Order_Quantity",
    "Estimated_Days_Remaining",
    "Stockout_Risk",
    "Demand_Trend",
    "Status"
]


restock_df = restock_df[
    output_columns
]

# ============================================================
# SAVE CSV
# ============================================================

restock_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# DISPLAY RESULTS
# ============================================================

print("\n" + "=" * 70)
print("SMART RESTOCKING RESULTS")
print("=" * 70)


display_columns = [
    "Store ID",
    "Product ID",
    "Current_Inventory",
    "Daily_Forecast_Demand",
    "Estimated_Days_Remaining",
    "Recommended_Order_Quantity",
    "Stockout_Risk",
    "Status"
]

print(
    restock_df[
        display_columns
    ].to_string(
        index=False
    )
)


# ============================================================
# SUMMARY
# ============================================================

critical_count = (
    restock_df[
        "Stockout_Risk"
    ] == "CRITICAL"
).sum()


high_count = (
    restock_df[
        "Stockout_Risk"
    ] == "HIGH"
).sum()


medium_count = (
    restock_df[
        "Stockout_Risk"
    ] == "MEDIUM"
).sum()


low_count = (
    restock_df[
        "Stockout_Risk"
    ] == "LOW"
).sum()


total_order_qty = (
    restock_df[
        "Recommended_Order_Quantity"
    ].sum()
)


products_to_order = (
    restock_df[
        "Recommended_Order_Quantity"
    ] > 0
).sum()


print("\n" + "=" * 70)
print("RESTOCKING SUMMARY")
print("=" * 70)


print(
    f"Store-product combinations analysed: "
    f"{len(restock_df)}"
)


print(
    f"Critical risk: {critical_count}"
)


print(
    f"High risk: {high_count}"
)


print(
    f"Medium risk: {medium_count}"
)


print(
    f"Low risk: {low_count}"
)


print(
    f"Combinations requiring stock orders: "
    f"{products_to_order}"
)


print(
    f"Total recommended units to order: "
    f"{total_order_qty:,}"
)


# ============================================================
# URGENT RESTOCKING
# ============================================================

urgent = restock_df[
    restock_df[
        "Stockout_Risk"
    ].isin(
        [
            "CRITICAL",
            "HIGH"
        ]
    )
]


print("\n" + "=" * 70)
print("URGENT RESTOCKING ALERTS")
print("=" * 70)


if urgent.empty:

    print(
        "No urgent restocking alerts."
    )

else:

    for _, row in urgent.iterrows():

        print(
            f"\nStore: {row['Store ID']}"
        )

        print(
            f"Product: {row['Product ID']}"
        )

        print(
            f"Current Inventory: "
            f"{row['Current_Inventory']:.0f}"
        )

        print(
    f"Expected Daily Demand: "
    f"{row['Daily_Forecast_Demand']:.0f}"
        )

        print(
            f"Estimated Days of Stock: "
            f"{row['Estimated_Days_Remaining']:.2f}"
        )

        print(
            f"Recommended Order: "
            f"{row['Recommended_Order_Quantity']} units"
        )

        print(
            f"Risk: "
            f"{row['Stockout_Risk']}"
        )


print("\n" + "=" * 70)

print(
    f"Restocking recommendations saved to:"
)

print(
    OUTPUT_FILE
)

print("=" * 70)