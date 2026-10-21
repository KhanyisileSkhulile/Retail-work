import pandas as pd
from pathlib import Path

# ============================================================
# RETAILAI - DATA ANALYSIS
# Lecturer Dataset Version
# ============================================================

DATA_FILE = "retail_store_inventory.csv"
SUMMARY_FILE = "retailai_product_summary.csv"


# ------------------------------------------------------------
# CHECK FILE
# ------------------------------------------------------------

if not Path(DATA_FILE).exists():
    raise FileNotFoundError(
        f"{DATA_FILE} was not found.\n"
        "Make sure it is in the same folder as analyze_data.py"
    )


# ------------------------------------------------------------
# LOAD DATA
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("RETAILAI - DATA ANALYSIS")
print("=" * 70)

print("\nLoading lecturer dataset...")

df = pd.read_csv(DATA_FILE)

print(f"Records loaded: {len(df):,}")
print(f"Columns loaded: {len(df.columns)}")


# ------------------------------------------------------------
# SHOW COLUMNS
# ------------------------------------------------------------

print("\nDataset columns:")

for column in df.columns:
    print(f"- {column}")


# ------------------------------------------------------------
# CHECK REQUIRED COLUMNS
# ------------------------------------------------------------

required_columns = [
    "Date",
    "Store ID",
    "Product ID",
    "Category",
    "Region",
    "Inventory Level",
    "Units Sold",
    "Units Ordered",
    "Demand Forecast",
    "Price",
    "Discount",
    "Weather Condition",
    "Holiday/Promotion",
    "Competitor Pricing",
    "Seasonality"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:

    raise ValueError(
        "\nMissing required columns:\n"
        + "\n".join(missing_columns)
    )


# ------------------------------------------------------------
# CLEAN DATA
# ------------------------------------------------------------

df["Date"] = pd.to_datetime(
    df["Date"],
    errors="coerce"
)

numeric_columns = [
    "Inventory Level",
    "Units Sold",
    "Units Ordered",
    "Demand Forecast",
    "Price",
    "Discount",
    "Holiday/Promotion",
    "Competitor Pricing"
]

for column in numeric_columns:

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


# Remove rows with missing important information
df = df.dropna(
    subset=[
        "Date",
        "Product ID",
        "Units Sold",
        "Inventory Level"
    ]
)


# ------------------------------------------------------------
# BASIC DATA INFORMATION
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("DATASET OVERVIEW")
print("=" * 70)

print(
    f"Date range: "
    f"{df['Date'].min().date()} "
    f"to {df['Date'].max().date()}"
)

print(
    f"Number of stores: "
    f"{df['Store ID'].nunique()}"
)

print(
    f"Number of products: "
    f"{df['Product ID'].nunique()}"
)

print(
    f"Number of categories: "
    f"{df['Category'].nunique()}"
)

print(
    f"Number of regions: "
    f"{df['Region'].nunique()}"
)


# ------------------------------------------------------------
# SALES CALCULATIONS
# ------------------------------------------------------------

total_units_sold = df[
    "Units Sold"
].sum()

total_units_ordered = df[
    "Units Ordered"
].sum()

average_inventory = df[
    "Inventory Level"
].mean()

average_demand_forecast = df[
    "Demand Forecast"
].mean()


# Revenue before discount
df["Gross Revenue"] = (
    df["Units Sold"]
    * df["Price"]
)


# Discount is stored as percentages such as 0, 5, 10, 20
df["Discount Amount"] = (
    df["Gross Revenue"]
    * (df["Discount"] / 100)
)


# Estimated revenue after discount
df["Net Revenue"] = (
    df["Gross Revenue"]
    - df["Discount Amount"]
)


total_gross_revenue = df[
    "Gross Revenue"
].sum()

total_net_revenue = df[
    "Net Revenue"
].sum()


print("\n" + "=" * 70)
print("SALES SUMMARY")
print("=" * 70)

print(
    f"Total units sold: "
    f"{total_units_sold:,.0f}"
)

print(
    f"Total units ordered: "
    f"{total_units_ordered:,.0f}"
)

print(
    f"Average inventory level: "
    f"{average_inventory:,.2f}"
)

print(
    f"Average demand forecast: "
    f"{average_demand_forecast:,.2f}"
)

print(
    f"Estimated gross revenue: "
    f"R {total_gross_revenue:,.2f}"
)

print(
    f"Estimated net revenue after discounts: "
    f"R {total_net_revenue:,.2f}"
)


# ------------------------------------------------------------
# PRODUCT SUMMARY
# ------------------------------------------------------------

product_summary = (
    df.groupby("Product ID")
    .agg(
        Total_Units_Sold=(
            "Units Sold",
            "sum"
        ),

        Average_Daily_Units_Sold=(
            "Units Sold",
            "mean"
        ),

        Average_Inventory_Level=(
            "Inventory Level",
            "mean"
        ),

        Total_Units_Ordered=(
            "Units Ordered",
            "sum"
        ),

        Average_Demand_Forecast=(
            "Demand Forecast",
            "mean"
        ),

        Average_Price=(
            "Price",
            "mean"
        ),

        Total_Gross_Revenue=(
            "Gross Revenue",
            "sum"
        ),

        Total_Net_Revenue=(
            "Net Revenue",
            "sum"
        )
    )
    .reset_index()
)


# Add category
product_category = (
    df.groupby("Product ID")[
        "Category"
    ]
    .agg(
        lambda x: x.mode().iloc[0]
        if not x.mode().empty
        else x.iloc[0]
    )
    .reset_index()
)


product_summary = product_summary.merge(
    product_category,
    on="Product ID",
    how="left"
)


# Reorder columns
product_summary = product_summary[
    [
        "Product ID",
        "Category",
        "Total_Units_Sold",
        "Average_Daily_Units_Sold",
        "Average_Inventory_Level",
        "Total_Units_Ordered",
        "Average_Demand_Forecast",
        "Average_Price",
        "Total_Gross_Revenue",
        "Total_Net_Revenue"
    ]
]


# ------------------------------------------------------------
# TOP SELLING PRODUCTS
# ------------------------------------------------------------

top_products = (
    product_summary
    .sort_values(
        "Total_Units_Sold",
        ascending=False
    )
    .head(10)
)


print("\n" + "=" * 70)
print("TOP 10 SELLING PRODUCTS")
print("=" * 70)

print(
    top_products[
        [
            "Product ID",
            "Category",
            "Total_Units_Sold"
        ]
    ].to_string(index=False)
)


# ------------------------------------------------------------
# CATEGORY ANALYSIS
# ------------------------------------------------------------

category_summary = (
    df.groupby("Category")
    .agg(
        Total_Units_Sold=(
            "Units Sold",
            "sum"
        ),

        Average_Inventory=(
            "Inventory Level",
            "mean"
        ),

        Total_Revenue=(
            "Net Revenue",
            "sum"
        )
    )
    .sort_values(
        "Total_Units_Sold",
        ascending=False
    )
    .reset_index()
)


print("\n" + "=" * 70)
print("CATEGORY PERFORMANCE")
print("=" * 70)

print(
    category_summary.to_string(
        index=False
    )
)


# ------------------------------------------------------------
# REGION ANALYSIS
# ------------------------------------------------------------

region_summary = (
    df.groupby("Region")
    .agg(
        Total_Units_Sold=(
            "Units Sold",
            "sum"
        ),

        Average_Inventory=(
            "Inventory Level",
            "mean"
        ),

        Total_Revenue=(
            "Net Revenue",
            "sum"
        )
    )
    .sort_values(
        "Total_Units_Sold",
        ascending=False
    )
    .reset_index()
)


print("\n" + "=" * 70)
print("REGIONAL PERFORMANCE")
print("=" * 70)

print(
    region_summary.to_string(
        index=False
    )
)


# ------------------------------------------------------------
# STORE ANALYSIS
# ------------------------------------------------------------

store_summary = (
    df.groupby("Store ID")
    .agg(
        Total_Units_Sold=(
            "Units Sold",
            "sum"
        ),

        Average_Inventory=(
            "Inventory Level",
            "mean"
        ),

        Total_Revenue=(
            "Net Revenue",
            "sum"
        )
    )
    .sort_values(
        "Total_Units_Sold",
        ascending=False
    )
    .reset_index()
)


print("\n" + "=" * 70)
print("STORE PERFORMANCE")
print("=" * 70)

print(
    store_summary.to_string(
        index=False
    )
)


# ------------------------------------------------------------
# PROMOTION ANALYSIS
# ------------------------------------------------------------

promotion_summary = (
    df.groupby("Holiday/Promotion")
    .agg(
        Average_Units_Sold=(
            "Units Sold",
            "mean"
        ),

        Total_Units_Sold=(
            "Units Sold",
            "sum"
        )
    )
    .reset_index()
)


promotion_summary[
    "Promotion_Status"
] = promotion_summary[
    "Holiday/Promotion"
].map(
    {
        0: "No Promotion",
        1: "Promotion/Holiday"
    }
)


print("\n" + "=" * 70)
print("PROMOTION ANALYSIS")
print("=" * 70)

print(
    promotion_summary[
        [
            "Promotion_Status",
            "Average_Units_Sold",
            "Total_Units_Sold"
        ]
    ].to_string(
        index=False
    )
)


# ------------------------------------------------------------
# WEATHER ANALYSIS
# ------------------------------------------------------------

weather_summary = (
    df.groupby("Weather Condition")
    .agg(
        Average_Units_Sold=(
            "Units Sold",
            "mean"
        ),

        Total_Units_Sold=(
            "Units Sold",
            "sum"
        )
    )
    .sort_values(
        "Total_Units_Sold",
        ascending=False
    )
    .reset_index()
)


print("\n" + "=" * 70)
print("WEATHER AND SALES")
print("=" * 70)

print(
    weather_summary.to_string(
        index=False
    )
)


# ------------------------------------------------------------
# SEASONALITY ANALYSIS
# ------------------------------------------------------------

season_summary = (
    df.groupby("Seasonality")
    .agg(
        Average_Units_Sold=(
            "Units Sold",
            "mean"
        ),

        Total_Units_Sold=(
            "Units Sold",
            "sum"
        )
    )
    .sort_values(
        "Total_Units_Sold",
        ascending=False
    )
    .reset_index()
)


print("\n" + "=" * 70)
print("SEASONAL SALES")
print("=" * 70)

print(
    season_summary.to_string(
        index=False
    )
)


# ------------------------------------------------------------
# FORECAST ERROR ANALYSIS
# ------------------------------------------------------------

df["Forecast Error"] = (
    df["Units Sold"]
    - df["Demand Forecast"]
)

df["Absolute Forecast Error"] = (
    df["Forecast Error"].abs()
)

mae = df[
    "Absolute Forecast Error"
].mean()


print("\n" + "=" * 70)
print("EXISTING DATASET FORECAST PERFORMANCE")
print("=" * 70)

print(
    f"Average forecast error (MAE): "
    f"{mae:.2f} units"
)


# ------------------------------------------------------------
# POSSIBLE LOW STOCK RECORDS
# ------------------------------------------------------------

# A simple stock-risk indicator:
# inventory lower than the supplied demand forecast

df["Potential Stock Risk"] = (
    df["Inventory Level"]
    < df["Demand Forecast"]
)


stock_risk_count = (
    df["Potential Stock Risk"]
    .sum()
)


print("\n" + "=" * 70)
print("INVENTORY RISK")
print("=" * 70)

print(
    f"Records where inventory is below "
    f"forecast demand: {stock_risk_count:,}"
)


# ------------------------------------------------------------
# SAVE PRODUCT SUMMARY
# ------------------------------------------------------------

product_summary.to_csv(
    SUMMARY_FILE,
    index=False
)


print("\n" + "=" * 70)

print(
    f"Product summary saved successfully to:\n"
    f"{SUMMARY_FILE}"
)

print("=" * 70)