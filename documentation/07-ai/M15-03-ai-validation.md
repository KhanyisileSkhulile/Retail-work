# M15-03 — AI Forecasting and Restocking Validation

## Objective

Audit saved M11-05/M11-06 forecasting evidence and M12-02/M12-03 restocking outputs. This validation does not retrain the Ridge model or change the reorder/stockout decision rules.

## Existing evidence reviewed

| Area | Recorded result |
|---|---|
| M11-05 Ridge Regression temporal holdout | 11,000 test rows; 110 dates; 58 features |
| M11-05 MAE | 88.453325 units |
| M11-05 RMSE | 107.996727 units |
| M11-05 fitting boundary | Model fit ends 2023-09-13; test begins 2023-09-14 |
| M11-05 leakage control | Test data not used for training; model not retrained during evaluation |
| M11-06 rolling forecast | 11,000 rows, 110 dates, 2023-09-14 to 2024-01-01 |
| M12-02 recommendations | 11,000 rows, 100 store-product pairs, all 11,000 status `REORDER_NOW` |
| M12-02 suggested order units | 4,505,211 total; all rows have positive suggested quantities |
| M12-03 stockout detection | 11,000 rows, 100 store-product pairs, 0 observed stockouts |
| M12-03 risk flags | All 11,000 rows are `STOCKOUT_RISK`; no `WATCH` records |

## Validation performed by this task

The validation script checks:

- Forecast schema, finite/non-negative values, valid dates and unique date/store/product keys.
- Recomputed absolute error, MAE and RMSE against the stored M11-05/M11-06 metadata.
- Consistent chronological coverage and the recorded no-test-leakage/no-refit metadata.
- One-to-one date/store/product alignment between forecast, reorder and stockout outputs.
- Valid reorder/stockout status values and quantity semantics.
- Reconciliation of CSV status counts with M12-02/M12-03 summary JSON files.
- Concentration warnings when 95% or more of rows receive one status.

## Important interpretation

The recorded metrics show non-zero forecast error; they must not be presented as perfect predictions. More importantly, the current replay outputs are highly concentrated: 100% of rows are `REORDER_NOW` and 100% are `STOCKOUT_RISK`. This is a validation warning requiring review of demand units, stock levels and M12-01 baseline assumptions before operational use. It is not appropriate to conceal this result or modify thresholds solely to make the distribution look balanced.

M12-02/M12-03 are historical replay outputs, not live stock monitoring or purchase-order actions. A `STOCKOUT_RISK` flag is not evidence that a stockout actually occurred.

## Run

From the repository root:

```powershell
python -m unittest discover -s .\testing\ai -p "test_m15_03_ai_validation.py" -v
python .\testing\ai\validate_ai_outputs.py
```

The validation script writes machine-readable and Markdown results to `testing/results/`.
