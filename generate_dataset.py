import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# ============================================================
# RetailAI - Synthetic Spaza Shop Dataset Generator
# ============================================================

# Make results reproducible
np.random.seed(42)

# ------------------------------------------------------------
# 1. Dataset settings
# ------------------------------------------------------------

START_DATE = "2025-09-01"
END_DATE = "2026-08-31"

dates = pd.date_range(
    start=START_DATE,
    end=END_DATE,
    freq="D"
)

# ------------------------------------------------------------
# 2. Product information
# ------------------------------------------------------------

products = [
    {
        "Product_Name": "Bread",
        "Category": "Bakery",
        "Base_Demand": 28,
        "Price": 18.50,
        "Shelf_Life": 4,
        "Reorder_Days": 2,
        "Supplier": "Local Bakery"
    },
    {
        "Product_Name": "Maize Meal",
        "Category": "Staples",
        "Base_Demand": 15,
        "Price": 45.00,
        "Shelf_Life": 180,
        "Reorder_Days": 7,
        "Supplier": "Grain Supplier"
    },
    {
        "Product_Name": "Milk",
        "Category": "Dairy",
        "Base_Demand": 20,
        "Price": 19.99,
        "Shelf_Life": 10,
        "Reorder_Days": 3,
        "Supplier": "Fresh Dairy"
    },
    {
        "Product_Name": "Cooking Oil",
        "Category": "Groceries",
        "Base_Demand": 10,
        "Price": 39.99,
        "Shelf_Life": 365,
        "Reorder_Days": 7,
        "Supplier": "Wholesale Foods"
    },
    {
        "Product_Name": "Sugar",
        "Category": "Groceries",
        "Base_Demand": 12,
        "Price": 29.99,
        "Shelf_Life": 365,
        "Reorder_Days": 7,
        "Supplier": "Wholesale Foods"
    },
    {
        "Product_Name": "Rice",
        "Category": "Staples",
        "Base_Demand": 11,
        "Price": 34.99,
        "Shelf_Life": 365,
        "Reorder_Days": 7,
        "Supplier": "Grain Supplier"
    },
    {
        "Product_Name": "Eggs",
        "Category": "Dairy & Eggs",
        "Base_Demand": 18,
        "Price": 39.99,
        "Shelf_Life": 21,
        "Reorder_Days": 4,
        "Supplier": "Local Farm"
    },
    {
        "Product_Name": "Soft Drinks",
        "Category": "Beverages",
        "Base_Demand": 25,
        "Price": 15.00,
        "Shelf_Life": 180,
        "Reorder_Days": 5,
        "Supplier": "Beverage Distributor"
    },
    {
        "Product_Name": "Bottled Water",
        "Category": "Beverages",
        "Base_Demand": 22,
        "Price": 12.00,
        "Shelf_Life": 365,
        "Reorder_Days": 5,
        "Supplier": "Beverage Distributor"
    },
    {
        "Product_Name": "Canned Beans",
        "Category": "Canned Food",
        "Base_Demand": 8,
        "Price": 18.99,
        "Shelf_Life": 730,
        "Reorder_Days": 10,
        "Supplier": "Wholesale Foods"
    },
    {
        "Product_Name": "Soap",
        "Category": "Household",
        "Base_Demand": 7,
        "Price": 14.99,
        "Shelf_Life": 730,
        "Reorder_Days": 14,
        "Supplier": "Household Supplier"
    },
    {
        "Product_Name": "Toilet Paper",
        "Category": "Household",
        "Base_Demand": 6,
        "Price": 32.99,
        "Shelf_Life": 730,
        "Reorder_Days": 14,
        "Supplier": "Household Supplier"
    },
    {
        "Product_Name": "Chips",
        "Category": "Snacks",
        "Base_Demand": 20,
        "Price": 13.99,
        "Shelf_Life": 120,
        "Reorder_Days": 5,
        "Supplier": "Snack Distributor"
    },
    {
        "Product_Name": "Biscuits",
        "Category": "Snacks",
        "Base_Demand": 13,
        "Price": 11.99,
        "Shelf_Life": 180,
        "Reorder_Days": 7,
        "Supplier": "Snack Distributor"
    },
    {
        "Product_Name": "Instant Noodles",
        "Category": "Convenience Food",
        "Base_Demand": 16,
        "Price": 8.99,
        "Shelf_Life": 365,
        "Reorder_Days": 7,
        "Supplier": "Wholesale Foods"
    }
]

# ------------------------------------------------------------
# 3. Helper functions
# ------------------------------------------------------------

def seasonal_multiplier(date, product_name):
    """
    Creates realistic demand changes based on:
    - Day of week
    - Month
    - Summer weather
    - Holidays
    - Product type
    """

    multiplier = 1.0

    # Weekend effect
    if date.weekday() in [5, 6]:
        multiplier *= 1.15

    # Friday effect - customers often shop before weekend
    if date.weekday() == 4:
        multiplier *= 1.10

    # Beginning/end of month
    if date.day <= 5:
        multiplier *= 1.12

    if date.day >= 25:
        multiplier *= 1.08

    # December demand
    if date.month == 12:
        multiplier *= 1.25

    # January tends to have lower demand
    if date.month == 1:
        multiplier *= 0.90

    # Summer beverage demand
    if date.month in [11, 12, 1, 2]:
        if product_name in ["Soft Drinks", "Bottled Water", "Chips"]:
            multiplier *= 1.25

    # Winter demand
    if date.month in [6, 7]:
        if product_name in ["Maize Meal", "Instant Noodles", "Bread"]:
            multiplier *= 1.10

    # Easter period
    if date.month == 4:
        multiplier *= 1.08

    return multiplier


def calculate_reorder_point(base_demand, reorder_days):
    """
    Reorder point = expected demand during supplier lead time
    + safety stock.
    """

    safety_stock = base_demand * 2

    reorder_point = (
        base_demand * reorder_days
        + safety_stock
    )

    return int(round(reorder_point))


# ------------------------------------------------------------
# 4. Generate dataset
# ------------------------------------------------------------

records = []

for product in products:

    # Initial inventory
    reorder_point = calculate_reorder_point(
        product["Base_Demand"],
        product["Reorder_Days"]
    )

    current_stock = reorder_point * 2

    # Track when product stock was replenished
    last_restock_date = dates[0]

    for date in dates:

        # ----------------------------------------------------
        # Calculate demand
        # ----------------------------------------------------

        seasonal_factor = seasonal_multiplier(
            date,
            product["Product_Name"]
        )

        # Random daily variation
        random_factor = np.random.normal(
            loc=1.0,
            scale=0.18
        )

        expected_demand = (
            product["Base_Demand"]
            * seasonal_factor
            * random_factor
        )

        # Prevent negative demand
        expected_demand = max(
            expected_demand,
            0
        )

        units_sold = int(
            round(expected_demand)
        )

        # ----------------------------------------------------
        # Occasional unusual demand
        # ----------------------------------------------------

        # Around 3% of days have unusually high demand
        if np.random.random() < 0.03:
            units_sold = int(
                units_sold * np.random.uniform(
                    1.3,
                    1.8
                )
            )

        # ----------------------------------------------------
        # Stock availability
        # ----------------------------------------------------

        actual_units_sold = min(
            units_sold,
            current_stock
        )

        stockout = actual_units_sold < units_sold

        lost_sales = max(
            units_sold - actual_units_sold,
            0
        )

        # Reduce stock
        current_stock -= actual_units_sold

        # ----------------------------------------------------
        # Restocking
        # ----------------------------------------------------

        restocked = 0

        if current_stock <= reorder_point:

            # Order enough stock for several days
            restocked = int(
                product["Base_Demand"]
                * np.random.uniform(
                    5,
                    9
                )
            )

            current_stock += restocked

            last_restock_date = date

        # ----------------------------------------------------
        # Expiry date
        # ----------------------------------------------------

        # For long-life products, use a distant expiry date
        expiry_date = (
            date
            + timedelta(
                days=product["Shelf_Life"]
            )
        )

        # ----------------------------------------------------
        # Revenue
        # ----------------------------------------------------

        revenue = (
            actual_units_sold
            * product["Price"]
        )

        # ----------------------------------------------------
        # Inventory value
        # ----------------------------------------------------

        inventory_value = (
            current_stock
            * product["Price"]
        )

        # ----------------------------------------------------
        # Low stock indicator
        # ----------------------------------------------------

        low_stock = current_stock <= reorder_point

        # ----------------------------------------------------
        # Record
        # ----------------------------------------------------

        records.append({

            "Date": date.strftime("%Y-%m-%d"),

            "Product_Name":
                product["Product_Name"],

            "Category":
                product["Category"],

            "Units_Sold":
                actual_units_sold,

            "Current_Stock":
                current_stock,

            "Reorder_Point":
                reorder_point,

            "Expiry_Date":
                expiry_date.strftime("%Y-%m-%d"),

            "Unit_Price":
                product["Price"],

            "Supplier":
                product["Supplier"],

            "Restocked_Units":
                restocked,

            "Stockout":
                int(stockout),

            "Lost_Sales":
                lost_sales,

            "Revenue":
                round(revenue, 2),

            "Inventory_Value":
                round(inventory_value, 2),

            "Low_Stock":
                int(low_stock)
        })


# ------------------------------------------------------------
# 5. Create DataFrame
# ------------------------------------------------------------

df = pd.DataFrame(records)

# Sort the dataset
df = df.sort_values(
    by=["Date", "Product_Name"]
)

# ------------------------------------------------------------
# 6. Save CSV
# ------------------------------------------------------------

output_file = "retailai_sales_data.csv"

df.to_csv(
    output_file,
    index=False
)

# ------------------------------------------------------------
# 7. Display information
# ------------------------------------------------------------

print("=" * 60)
print("RetailAI Dataset Generated Successfully")
print("=" * 60)

print(f"File: {output_file}")

print(f"Rows: {len(df):,}")

print(f"Products: {df['Product_Name'].nunique()}")

print(
    f"Date Range: "
    f"{df['Date'].min()} "
    f"to "
    f"{df['Date'].max()}"
)

print(
    f"Total Units Sold: "
    f"{df['Units_Sold'].sum():,}"
)

print(
    f"Total Revenue: "
    f"R{df['Revenue'].sum():,.2f}"
)

print(
    f"Stockout Events: "
    f"{df['Stockout'].sum():,}"
)

print("=" * 60)

print("\nFirst 10 rows:")
print(df.head(10))

print("\nProducts:")
print(df["Product_Name"].unique())
