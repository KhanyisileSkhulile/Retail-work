# M12-04 — Inventory Validation Evidence

## 1. Objective
Validate the integrity, accuracy, and completeness of the inventory data prior to generating restocking recommendations and stockout alerts. This ensures that the algorithms in M12-02 and M12-03 are fed with clean data.

## 2. Validation Scope
The validation covers the `INVENTORY_RECORD` fact table and its relationships with the `STORE`, `PRODUCT`, and `DATE_DIM` dimension tables.

## 3. Validation Checks and Results

### 3.1 Negative Inventory
- **Rule:** Inventory Level must be >= 0.
- **Query:** `SELECT * FROM INVENTORY_RECORD WHERE Inventory_Level < 0;`
- **Result:** 0 records found. (Data is clean).

### 3.2 Negative Sales/Orders
- **Rule:** Units Sold and Units Ordered must be >= 0.
- **Query:** `SELECT * FROM INVENTORY_RECORD WHERE Units_Sold < 0 OR Units_Ordered < 0;`
- **Result:** 0 records found. (Data is clean).

### 3.3 Referential Integrity
- **Rule:** Every Store ID and Product ID in the fact table must exist in their respective dimension tables.
- **Query:** See `database/inventory_validation.sql` (Query 3).
- **Result:** 0 orphaned records found. Foreign key constraints are working correctly.

### 3.4 Forecast Outliers
- **Rule:** Flag records where the `Demand_Forecast` is wildly higher than the actual `Units_Sold` (e.g., > 5x).
- **Query:** See `database/inventory_validation.sql` (Query 4).
- **Result:** Several extreme outliers were identified. These will be handled by the normalization rules in M12-01 (e.g., flooring negative values and capping excessive forecasts during model training).

## 4. Conclusion
The dataset is structurally sound and ready for the Smart Restocking & Alerts pipeline. The implementation of `CHECK` constraints in `schema.sql` (from M07-05) prevents future invalid data from being inserted.