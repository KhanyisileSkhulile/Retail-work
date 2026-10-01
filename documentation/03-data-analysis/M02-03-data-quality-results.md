# M02-03 - Data Quality Validation Results

**Issue:** M02-03  
**Analyst:** Khanyisile Skhulile  
**Generated:** 2026-10-01 20:16  
**Source file:** `dataset/raw/retail_store_inventory.csv`

---

## 1. Dataset Shape

- **Rows:** 73,100
- **Columns:** 15

## 2. Missing Values - Summary

- **Total cells:** 1,096,500
- **Missing cells:** 0
- **Missing %:** 0.0000%

**No missing values detected anywhere in the dataset.**

## 3. Missing Values - Per Column

| Column | Non-Null | Null | Null % |
|--------|----------|------|--------|
| `Date` | 73,100 | 0 | 0.00% |
| `Store ID` | 73,100 | 0 | 0.00% |
| `Product ID` | 73,100 | 0 | 0.00% |
| `Category` | 73,100 | 0 | 0.00% |
| `Region` | 73,100 | 0 | 0.00% |
| `Inventory Level` | 73,100 | 0 | 0.00% |
| `Units Sold` | 73,100 | 0 | 0.00% |
| `Units Ordered` | 73,100 | 0 | 0.00% |
| `Demand Forecast` | 73,100 | 0 | 0.00% |
| `Price` | 73,100 | 0 | 0.00% |
| `Discount` | 73,100 | 0 | 0.00% |
| `Weather Condition` | 73,100 | 0 | 0.00% |
| `Holiday/Promotion` | 73,100 | 0 | 0.00% |
| `Competitor Pricing` | 73,100 | 0 | 0.00% |
| `Seasonality` | 73,100 | 0 | 0.00% |

## 4. Duplicate Rows

- **Exact duplicate rows (all columns):** 0

**No duplicate rows detected.**

## 5. Duplicate Check on Key Columns

- On `Date + Store ID + Product ID`: **0** duplicate rows
- On `Store ID + Product ID`: **73,000** duplicate rows

## 6. Constant Columns (only one unique value)

No constant columns detected.

## 7. Whitespace / Empty-String Check

No empty or whitespace-only string values detected.

## 8. Verdict

**Dataset passes all M02-03 quality checks.**
- No missing values
- No duplicate rows
- No constant columns
