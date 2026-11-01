# M10-02 — Dataset Cleaning and Validation

- **Generated:** 2026-10-22 23:33:17
- **Source:** `dataset/raw/retail_store_inventory.csv`
- **Cleaning script:** `python-ai/data/clean_data.py`
- **Original rows:** 73,100
- **Original columns:** 15
- **Final cleaned rows:** 73,100
- **Final columns:** 15
- **Exact duplicate rows removed:** 0
- **Rows removed for missing required values:** 0
- **Invalid dates converted to missing:** 0
- **Rows with negative Units Sold retained for review:** 0
- **Rows with negative Demand Forecast retained for review:** 673
- **Rows with negative Inventory Level retained for review:** 0
- **Rows belonging to repeated date/store/product keys:** 0

## Schema validation

- **Missing expected columns:** None
- **Unexpected columns:** None

## Missing values before cleaning

| Column | Missing values |
|---|---:|
| Date | 0 |
| Store ID | 0 |
| Product ID | 0 |
| Category | 0 |
| Region | 0 |
| Inventory Level | 0 |
| Units Sold | 0 |
| Units Ordered | 0 |
| Demand Forecast | 0 |
| Price | 0 |
| Discount | 0 |
| Weather Condition | 0 |
| Holiday/Promotion | 0 |
| Competitor Pricing | 0 |
| Seasonality | 0 |

## Missing values after cleaning

| Column | Missing values |
|---|---:|
| Date | 0 |
| Store ID | 0 |
| Product ID | 0 |
| Category | 0 |
| Region | 0 |
| Inventory Level | 0 |
| Units Sold | 0 |
| Units Ordered | 0 |
| Demand Forecast | 0 |
| Price | 0 |
| Discount | 0 |
| Weather Condition | 0 |
| Holiday/Promotion | 0 |
| Competitor Pricing | 0 |
| Seasonality | 0 |

## Invalid numeric values

| Column | Values that could not be converted |
|---|---:|
| Inventory Level | 0 |
| Units Sold | 0 |
| Units Ordered | 0 |
| Demand Forecast | 0 |
| Price | 0 |
| Discount | 0 |
| Holiday/Promotion | 0 |
| Competitor Pricing | 0 |

## Cleaning decisions

- The original raw CSV is not modified.
- Blank text values are treated as missing.
- Dates and numeric columns are converted to appropriate types.
- Exact duplicate records are removed.
- Rows missing Date, Store ID, Product ID, or Units Sold are removed.
- Negative values and repeated business keys are reported for review, not silently deleted.
- Missing optional values are reported rather than automatically imputed.

**Cleaned dataset:** `dataset\processed\retail_store_inventory_clean.csv`
