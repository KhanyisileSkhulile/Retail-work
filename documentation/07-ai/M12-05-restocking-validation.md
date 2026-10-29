# M12-05 — Validate Restocking Scenarios

## 1. Objective
To verify that the restocking recommendations and stockout detection logic align exactly with the baseline assumptions and business rules defined in M12-01.

## 2. Scope of Validation
The validation covers:
- The reorder recommendation calculation (`reorder.py`).
- The stockout detection logic (`stockout.py`).
- Edge case handling (negative values, missing data, and multi-store products).

## 3. Verification Scenarios and Results

| Scenario ID | Scenario Description | Expected Result | Status |
|---|---|---|---|
| **1** | Stock is above reorder point. | No order; Status is `WATCH` or `HEALTHY`. |  PASS |
| **2** | Stock equals reorder point. | `REORDER_NOW`; Order up to target stock. |  PASS |
| **3** | Stock is below reorder point. | `REORDER_NOW`; Positive quantity to reach target. |  PASS |
| **4** | Forecast is negative. | Use zero demand and record the normalized input. |  PASS |
| **5** | Stock is missing or invalid. | `DATA_REQUIRED`; No numeric order recommendation. |  PASS |
| **6** | Forecast missing but no fallback. | `INSUFFICIENT_HISTORY`; No guessed quantity. |  PASS |
| **7** | The same product appears in two stores. | Calculated independently for each store-product pair. |  PASS |
| **8** | On-hand inventory is exactly zero. | `STOCKOUT` flagged immediately. |  PASS |

## 4. How to Run the Tests
To reproduce these results, run the following command from the repository root:

```powershell
python -m unittest discover -s testing/ai -p "test_restocking_scenarios.py"