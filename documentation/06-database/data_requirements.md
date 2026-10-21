# Data Requirements — Retail-X-AI

**Task:** M07-01
**Author:** @KhanyisileSkhulile614
**Date:** 2026-10-12
**Based on:** M02-04 Data Dictionary, `dataset/raw/retail_store_inventory.csv`

---

## 1. Data Source

| Attribute | Value |
|-----------|-------|
| Source file | `dataset/raw/retail_store_inventory.csv` |
| Rows | 73,100 |
| Columns | 15 |
| Granularity | One row per (Date, Store ID, Product ID) |
| Date range | 2022-01-01 to 2022-09-30 (731 unique days) |
| Nature | Synthetic (Kaggle source, see DATASET-SOURCE.md) |

---

## 2. Entities and Row Counts

| # | Entity | Purpose | Rows |
|---|--------|---------|------|
| 1 | Category | Product groups | 5 |
| 2 | Region | Geographic territories | 4 |
| 3 | Store | Retail locations | 5 |
| 4 | Product | Products sold | 20 |
| 5 | Date_Dim | Daily calendar dimension | 731 |
| 6 | Inventory_Record | Daily fact table | 73,100 |

---

## 3. Field-Level Requirements

### 3.1 Category
| Field | Type | Constraints |
|-------|------|-------------|
| Category_ID | INT | PK, auto |
| Category_Name | VARCHAR(50) | UNIQUE, NOT NULL |

### 3.2 Region
| Field | Type | Constraints |
|-------|------|-------------|
| Region_ID | INT | PK, auto |
| Region_Name | VARCHAR(50) | UNIQUE, NOT NULL |

### 3.3 Store
| Field | Type | Constraints |
|-------|------|-------------|
| Store_ID | VARCHAR(10) | PK |
| Region_ID | INT | FK to Region |
| Store_Name | VARCHAR(100) | NOT NULL |

### 3.4 Product
| Field | Type | Constraints |
|-------|------|-------------|
| Product_ID | VARCHAR(10) | PK |
| Category_ID | INT | FK to Category |
| Product_Name | VARCHAR(100) | NOT NULL |
| Unit_Price | DECIMAL(10,2) | > 0 |
| Discount | DECIMAL(5,2) | 0 to 100, default 0 |

### 3.5 Date_Dim
| Field | Type | Constraints |
|-------|------|-------------|
| Date_ID | INT | PK, auto |
| Full_Date | DATE | UNIQUE, NOT NULL |
| Day | INT | 1 to 31 |
| Month | INT | 1 to 12 |
| Year | INT | > 0 |
| Season | VARCHAR(20) | IN (Spring, Summer, Autumn, Winter) |

### 3.6 Inventory_Record (fact table)
| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| Record_ID | BIGINT | PK, auto | |
| Date_ID | INT | FK to Date_Dim | |
| Store_ID | VARCHAR(10) | FK to Store | |
| Product_ID | VARCHAR(10) | FK to Product | |
| Inventory_Level | INT | >= 0 | Observed 50 to 500 |
| Units_Sold | INT | >= 0 | Observed 0 to 499 |
| Units_Ordered | INT | >= 0 | Observed 20 to 200 |
| Demand_Forecast | DECIMAL(10,2) | >= 0 | 673 negatives in CSV - clean first |
| Competitor_Pricing | DECIMAL(10,2) | > 0 | Observed 5.03 to 104.94 |
| Weather_Condition | VARCHAR(20) | IN (Rainy, Sunny, Cloudy, Snowy) | |
| Holiday_Promotion | BOOLEAN | 0 or 1 | |
| Seasonality | VARCHAR(20) | IN (Spring, Summer, Autumn, Winter) | |

### 3.7 Feature Columns for Modelling - PENDING M04-01

To be finalised once M04-01 (AI model design) is available.
Placeholder based on M02-05 findings:

- **Target variable:** [Demand_Forecast OR Units_Sold - confirm from M02-05]
- **Leakage column (exclude from inputs):** [the other one]

**Candidate input features:**
- Inventory_Level
- Units_Ordered
- Price
- Discount
- Weather_Condition
- Holiday_Promotion
- Competitor_Pricing
- Seasonality

**Derived features (to confirm):**
- lag_7_Units_Sold, lag_30_Units_Sold
- rolling_avg_7_Units_Sold, rolling_avg_30_Units_Sold

**Split strategy:** temporal (earlier months train, later months test)

---

## 4. Data Quality Rules

| # | Rule | Field(s) | Action if Violated |
|---|------|----------|--------------------|
| 1 | No missing values | All | Reject row |
| 2 | Non-negative stock | Inventory_Level | Clamp to 0 |
| 3 | Non-negative sales | Units_Sold | Reject row |
| 4 | Non-negative demand | Demand_Forecast | Replace 673 negatives with 0 before load |
| 5 | Positive price | Unit_Price, Competitor_Pricing | Reject row |
| 6 | Discount range | Discount | Clamp to [0, 100] |
| 7 | Valid categories | Category, Region, Weather, Seasonality | Reject row |
| 8 | Unique composite | (Date_ID, Store_ID, Product_ID) | Reject duplicate |
| 9 | FK integrity | All FKs | Reject row if parent missing |

---

## 5. Data Volume and Retention

- Daily load: 100 rows (5 stores x 20 products)
- Yearly load: ~36,500 rows
- Retention: minimum 24 months
- Backup: nightly snapshot to cloud storage

---

## 6. Indexing Strategy

| Index | Table | Column(s) | Purpose |
|-------|-------|-----------|---------|
| idx_inv_date | Inventory_Record | Date_ID | Time-series queries |
| idx_inv_store | Inventory_Record | Store_ID | Store-level analysis |
| idx_inv_product | Inventory_Record | Product_ID | Product-level analysis |
| idx_inv_weather | Inventory_Record | Weather_Condition | Weather impact |
| idx_inv_season | Inventory_Record | Seasonality | Seasonal analysis |
| idx_inv_promo | Inventory_Record | Holiday_Promotion | Promotion impact |

---

## 7. Dependencies

- M02-04 - Data Dictionary: column types, ranges, quality issues confirmed
- M02-05 - Forecasting target and leakage: identifies target variable
- M04-01 - AI model design: feature columns will be confirmed once available

---

## 8. Known Issues

1. Demand Forecast has 673 negative values (min = -9.99). Must be cleaned to >= 0
   before ingestion. Enforced by CHECK constraint in schema.sql.
2. Dataset is synthetic (not real business data).
3. Holiday/Promotion corresponds to Promotion in the original Kaggle source.
