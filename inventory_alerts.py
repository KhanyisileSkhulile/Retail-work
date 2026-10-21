import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# RETAILAI - INVENTORY ALERT SYSTEM
# Lecturer Dataset Version
# ============================================================

DATA_FILE = "retail_store_inventory.csv"
RESTOCK_FILE = "retailai_restocking_recommendations.csv"
OUTPUT_FILE = "retailai_inventory_alerts.csv"

RECENT_DAYS = 30


# ============================================================
# CHECK FILES
# ============================================================

if not Path(DATA_FILE).exists():

    raise FileNotFoundError(
        f"{DATA_FILE} was not found.\n"
        "Make sure the lecturer dataset is in the project folder."
    )


if not Path(RESTOCK_FILE).exists():

    raise FileNotFoundError(
        f"{RESTOCK_FILE} was not found.\n"
        "Run smart_restocking.py first."
    )


# ============================================================
# LOAD DATA
# ============================================================

print("\n" + "=" * 70)

print("RETAILAI - INVENTORY ALERT SYSTEM")

print("=" * 70)

print("\nLoading data...")


df = pd.read_csv(DATA_FILE)

restock_df = pd.read_csv(
    RESTOCK_FILE
)


print(
    f"Dataset records loaded: "
    f"{len(df):,}"
)

print(
    f"Restocking records loaded: "
    f"{len(restock_df):,}"
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

    if column in df.columns:

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
        "Units Sold"
    ]
)


# ============================================================
# RECENT SALES PERIOD
# ============================================================

latest_date = df[
    "Date"
].max()


recent_start_date = (
    latest_date
    - pd.Timedelta(
        days=RECENT_DAYS - 1
    )
)


recent_df = df[
    df["Date"]
    >= recent_start_date
].copy()


print(
    f"\nAnalysing recent period: "
    f"{recent_start_date.date()} "
    f"to {latest_date.date()}"
)


# ============================================================
# RECENT SALES ANALYSIS
# ============================================================

recent_summary = (
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
        )
    )
    .reset_index()
)


recent_summary[
    "Sales_Std_Dev"
] = recent_summary[
    "Sales_Std_Dev"
].fillna(0)


# ============================================================
# GLOBAL SALES BENCHMARKS
# ============================================================

median_daily_sales = (
    recent_summary[
        "Average_Daily_Sales"
    ].median()
)


slow_moving_threshold = (
    median_daily_sales
    * 0.50
)


high_demand_threshold = (
    recent_summary[
        "Average_Demand_Forecast"
    ].quantile(0.75)
)


print(
    f"Median daily sales: "
    f"{median_daily_sales:.2f}"
)


print(
    f"Slow-moving threshold: "
    f"{slow_moving_threshold:.2f}"
)


print(
    f"High-demand threshold: "
    f"{high_demand_threshold:.2f}"
)


# ============================================================
# MERGE WITH RESTOCKING RESULTS
# ============================================================

alerts_df = restock_df.merge(
    recent_summary[
        [
            "Store ID",
            "Product ID",
            "Recent_Units_Sold",
            "Average_Daily_Sales",
            "Average_Demand_Forecast"
        ]
    ],
    on=[
        "Store ID",
        "Product ID"
    ],
    how="left",
    suffixes=(
        "",
        "_Recent"
    )
)


# ============================================================
# MOVEMENT STATUS
# ============================================================

def classify_movement(row):

    avg_sales = row[
        "Average_Daily_Sales"
    ]


    if pd.isna(
        avg_sales
    ):

        return "UNKNOWN"


    if avg_sales <= 0:

        return "NO SALES"


    elif avg_sales <= slow_moving_threshold:

        return "SLOW MOVING"


    else:

        return "NORMAL MOVING"


alerts_df[
    "Movement_Status"
] = alerts_df.apply(
    classify_movement,
    axis=1
)


# ============================================================
# DEMAND STATUS
# ============================================================

def classify_demand(row):

    demand = row[
        "Average_Demand_Forecast"
    ]


    if pd.isna(
        demand
    ):

        return "UNKNOWN"


    if demand >= high_demand_threshold:

        return "HIGH DEMAND"


    elif demand <= slow_moving_threshold:

        return "LOW DEMAND"


    else:

        return "NORMAL DEMAND"


alerts_df[
    "Demand_Status"
] = alerts_df.apply(
    classify_demand,
    axis=1
)


# ============================================================
# OVERSTOCK DETECTION
# ============================================================

def detect_overstock(row):

    current_inventory = row[
        "Current_Inventory"
    ]

    daily_demand = row[
        "Daily_Forecast_Demand"
    ]

    if daily_demand <= 0:
        return "UNKNOWN"

    days_of_stock = (
        current_inventory
        / daily_demand
    )

    if days_of_stock >= 7:
        return "OVERSTOCKED"

    elif days_of_stock >= 5:
        return "HIGH STOCK"

    else:
        return "NORMAL STOCK"

    if forecast_demand <= 0:

        return "UNKNOWN"


    ratio = (
        current_inventory
        / forecast_demand
    )


    if ratio >= 2.5:

        return "OVERSTOCKED"


    elif ratio >= 1.5:

        return "HIGH STOCK"


    else:

        return "NORMAL STOCK"


alerts_df[
    "Inventory_Position"
] = alerts_df.apply(
    detect_overstock,
    axis=1
)


# ============================================================
# CREATE ALERT MESSAGES
# ============================================================

def create_alert_message(row):

    messages = []


    store = row[
        "Store ID"
    ]

    product = row[
        "Product ID"
    ]

    risk = str(
        row[
            "Stockout_Risk"
        ]
    ).upper()


    movement = str(
        row[
            "Movement_Status"
        ]
    ).upper()


    demand = str(
        row[
            "Demand_Status"
        ]
    ).upper()


    inventory_position = str(
        row[
            "Inventory_Position"
        ]
    ).upper()


    order_quantity = row[
        "Recommended_Order_Quantity"
    ]


    # --------------------------------------------------------
    # STOCKOUT ALERTS
    # --------------------------------------------------------

    if risk == "CRITICAL":

        messages.append(
            f"CRITICAL STOCKOUT RISK: "
            f"{product} at {store} requires urgent attention."
        )


    elif risk == "HIGH":

        messages.append(
            f"LOW STOCK: {product} at {store} "
            f"may run out soon. "
            f"Recommended order: "
            f"{int(order_quantity)} units."
        )


    elif risk == "MEDIUM":

        messages.append(
            f"REORDER WARNING: "
            f"{product} at {store} "
            f"is close to its reorder level."
        )


    # --------------------------------------------------------
    # SLOW MOVING
    # --------------------------------------------------------

    if movement == "NO SALES":

        messages.append(
            f"NO SALES: {product} at {store} "
            f"recorded no recent sales."
        )


    elif movement == "SLOW MOVING":

        messages.append(
            f"SLOW MOVING: {product} at {store} "
            f"is selling below the normal sales level."
        )


    # --------------------------------------------------------
    # HIGH DEMAND
    # --------------------------------------------------------

    if demand == "HIGH DEMAND":

        messages.append(
            f"HIGH DEMAND: {product} at {store} "
            f"is experiencing strong forecast demand."
        )


    # --------------------------------------------------------
    # OVERSTOCK
    # --------------------------------------------------------

    if inventory_position == "OVERSTOCKED":

        messages.append(
            f"OVERSTOCK WARNING: "
            f"{product} at {store} has significantly "
            f"more stock than expected demand."
        )


    elif inventory_position == "HIGH STOCK":

        messages.append(
            f"HIGH STOCK: {product} at {store} "
            f"has more inventory than expected demand."
        )


    if not messages:

        return "NO ALERT"


    return " | ".join(
        messages
    )


alerts_df[
    "Alert_Message"
] = alerts_df.apply(
    create_alert_message,
    axis=1
)


# ============================================================
# ALERT SEVERITY
# ============================================================

def calculate_severity(row):

    risk = str(
        row[
            "Stockout_Risk"
        ]
    ).upper()


    movement = str(
        row[
            "Movement_Status"
        ]
    ).upper()


    demand = str(
        row[
            "Demand_Status"
        ]
    ).upper()


    inventory_position = str(
        row[
            "Inventory_Position"
        ]
    ).upper()


    if risk == "CRITICAL":

        return "CRITICAL"


    elif risk == "HIGH":

        return "HIGH"


    elif risk == "MEDIUM":

        return "MEDIUM"


    elif (
        movement == "NO SALES"
        or inventory_position == "OVERSTOCKED"
    ):

        return "MEDIUM"


    elif (
        movement == "SLOW MOVING"
        or demand == "HIGH DEMAND"
        or inventory_position == "HIGH STOCK"
    ):

        return "LOW"


    else:

        return "NORMAL"


alerts_df[
    "Alert_Severity"
] = alerts_df.apply(
    calculate_severity,
    axis=1
)


# ============================================================
# PRIORITY
# ============================================================

priority_map = {

    "CRITICAL": 1,

    "HIGH": 2,

    "MEDIUM": 3,

    "LOW": 4,

    "NORMAL": 5
}


alerts_df[
    "Alert_Priority"
] = alerts_df[
    "Alert_Severity"
].map(
    priority_map
)


# ============================================================
# ROUND NUMBERS
# ============================================================

round_columns = [
    "Current_Inventory",
    "Average_Daily_Sales",
    "Average_Demand_Forecast",
    "Daily_Forecast_Demand",
    "Safety_Stock",
    "Reorder_Point",
    "Recommended_Stock_Level",
    "Estimated_Days_Remaining"
]


for column in round_columns:

    if column in alerts_df.columns:

        alerts_df[
            column
        ] = alerts_df[
            column
        ].round(2)


# ============================================================
# SORT RESULTS
# ============================================================

alerts_df = alerts_df.sort_values(
    by=[
        "Alert_Priority",
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
    "Recommended_Order_Quantity",
    "Estimated_Days_Remaining",
    "Stockout_Risk",
    "Movement_Status",
    "Demand_Status",
    "Inventory_Position",
    "Status",
    "Alert_Severity",
    "Alert_Message"
]


alerts_output = alerts_df[
    output_columns
].copy()


# ============================================================
# SAVE CSV
# ============================================================

alerts_output.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# DISPLAY RESULTS
# ============================================================

print("\n" + "=" * 70)

print("INVENTORY ALERT RESULTS")

print("=" * 70)


display_columns = [
    "Store ID",
    "Product ID",
    "Current_Inventory",
    "Stockout_Risk",
    "Movement_Status",
    "Demand_Status",
    "Inventory_Position",
    "Alert_Severity"
]


print(
    alerts_output[
        display_columns
    ].to_string(
        index=False
    )
)


# ============================================================
# SUMMARY
# ============================================================

critical_count = (
    alerts_output[
        "Alert_Severity"
    ] == "CRITICAL"
).sum()


high_count = (
    alerts_output[
        "Alert_Severity"
    ] == "HIGH"
).sum()


medium_count = (
    alerts_output[
        "Alert_Severity"
    ] == "MEDIUM"
).sum()


low_count = (
    alerts_output[
        "Alert_Severity"
    ] == "LOW"
).sum()


normal_count = (
    alerts_output[
        "Alert_Severity"
    ] == "NORMAL"
).sum()


slow_count = (
    alerts_output[
        "Movement_Status"
    ] == "SLOW MOVING"
).sum()


overstock_count = (
    alerts_output[
        "Inventory_Position"
    ] == "OVERSTOCKED"
).sum()


high_demand_count = (
    alerts_output[
        "Demand_Status"
    ] == "HIGH DEMAND"
).sum()


print("\n" + "=" * 70)

print("ALERT SUMMARY")

print("=" * 70)


print(
    f"Store-product combinations analysed: "
    f"{len(alerts_output)}"
)


print(
    f"Critical alerts: {critical_count}"
)


print(
    f"High alerts: {high_count}"
)


print(
    f"Medium alerts: {medium_count}"
)


print(
    f"Low alerts: {low_count}"
)


print(
    f"Normal inventory positions: "
    f"{normal_count}"
)


print(
    f"Slow-moving combinations: "
    f"{slow_count}"
)


print(
    f"Overstocked combinations: "
    f"{overstock_count}"
)


print(
    f"High-demand combinations: "
    f"{high_demand_count}"
)


# ============================================================
# ACTIVE ALERTS
# ============================================================

active_alerts = alerts_output[
    alerts_output[
        "Alert_Message"
    ] != "NO ALERT"
]


print("\n" + "=" * 70)

print("ACTIVE INVENTORY ALERTS")

print("=" * 70)


if active_alerts.empty:

    print(
        "No active inventory alerts."
    )


else:

    for _, row in active_alerts.head(30).iterrows():

        print(
            f"\n[{row['Alert_Severity']}] "
            f"{row['Store ID']} - "
            f"{row['Product ID']}"
        )

        print(
            row[
                "Alert_Message"
            ]
        )


    if len(active_alerts) > 30:

        print(
            f"\n... plus "
            f"{len(active_alerts) - 30} "
            f"more alerts saved in the CSV file."
        )


print("\n" + "=" * 70)

print(
    "Inventory alerts saved successfully to:"
)

print(
    OUTPUT_FILE
)

print("=" * 70)