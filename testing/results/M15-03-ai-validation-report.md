# M15-03 — AI Forecasting and Restocking Validation

## Overall result: PASS_WITH_WARNINGS

This validation audits the saved M11-05/M11-06 forecasting outputs and M12-02/M12-03 restocking outputs. It does not retrain the model or change reorder/stockout thresholds.

## Forecasting summary

- MAE: 88.45332508286131
- RMSE: 107.99672727067626
- Forecast rows: 11000
- Date coverage: 2023-09-14 to 2024-01-01
- Model: Ridge Regression (M11-05/M11-06 saved evidence)

## Restocking summary

- Reorder rows: 11000
- Reorder status counts: `{'REORDER_NOW': 11000}`
- REORDER_NOW share: 100.0%
- Total suggested order units: 4505211
- Stockout rows: 11000
- Stockout status counts: `{'STOCKOUT_RISK': 11000}`
- STOCKOUT_RISK share: 100.0%
- Observed stockout records: 0

## Validation checks

| Check | Result | Detail |
|---|---|---|
| forecast_schema | **PASS** | All required forecast columns are present. |
| forecast_numeric_values | **PASS** | Actuals, forecasts and absolute errors are finite numeric values. |
| forecast_non_negative | **PASS** | Actual demand and predicted demand are non-negative. |
| forecast_dates_valid | **PASS** | All forecast dates parse successfully. |
| forecast_business_keys_unique | **PASS** | Duplicate Date/Store/Product keys: 0. |
| forecast_absolute_error_consistent | **PASS** | Absolute Error matches |Actual Units Sold - Forecast Units Sold|. |
| forecast_metrics_recomputed | **PASS** | CSV MAE=88.453325, RMSE=107.996727; M11-06 summary MAE=88.453325, RMSE=107.996727. |
| m11_05_and_m11_06_metrics_agree | **PASS** | Recomputed rolling-output metrics agree with the M11-05 temporal holdout evaluation. |
| forecast_no_test_leakage | **PASS** | M11-05/M11-06 metadata explicitly reports no test-data fitting or model refitting. |
| forecast_date_coverage | **PASS** | CSV covers 2023-09-14 to 2024-01-01 across 110 unique dates. |
| forecast_row_count | **PASS** | Forecast CSV rows=11000, M11-06 summary=11000, M11-05 test rows=11000. |
| reorder_schema | **PASS** | All required reorder columns are present. |
| stockout_schema | **PASS** | All required stockout columns are present. |
| reorder_forecast_key_alignment | **PASS** | Forecast keys=11000, reorder keys=11000, missing=0, extra=0. |
| stockout_forecast_key_alignment | **PASS** | Forecast keys=11000, stockout keys=11000, missing=0, extra=0. |
| reorder_key_uniqueness | **PASS** | Duplicate reorder keys: 0. |
| stockout_key_uniqueness | **PASS** | Duplicate stockout keys: 0. |
| reorder_quantities_valid | **PASS** | Suggested order quantities are finite, present and non-negative. |
| reorder_status_values | **PASS** | Observed statuses: ['REORDER_NOW']. |
| reorder_now_has_positive_quantity | **PASS** | REORDER_NOW rows=11000; all have positive suggested quantities. |
| stockout_status_values | **PASS** | Observed statuses: ['STOCKOUT_RISK']. |
| observed_stockout_zero_stock | **PASS** | Rows labelled STOCKOUT have zero recorded inventory. |
| stockout_risk_positive_stock | **PASS** | Rows labelled STOCKOUT_RISK have positive recorded stock. |
| reorder_summary_matches_csv | **PASS** | CSV status counts={'REORDER_NOW': 11000}; summary counts={'REORDER_NOW': 11000}. |
| stockout_summary_matches_csv | **PASS** | CSV status counts={'STOCKOUT_RISK': 11000}; summary counts={'STOCKOUT_RISK': 11000}. |
| reorder_status_distribution | **WARN** | 100.0% of rows are REORDER_NOW; review demand/stock scaling and baseline assumptions before operational use. |
| stockout_status_distribution | **WARN** | 100.0% of rows are STOCKOUT_RISK; this is a concentrated risk signal and should be reviewed before operational use. |

## Interpretation and limitations

- Forecast MAE/RMSE are error measures on the saved historical evaluation period; they are not guarantees of future accuracy.
- The M11-05 metadata must confirm that the test data was not used for training and the evaluation did not refit the saved model.
- Reorder recommendations and stockout flags are historical replay outputs based on M12-01 assumptions. They do not represent live inventory, supplier orders or current alerts.
- A very high share of one status is reported as a warning, not silently accepted as balanced performance. Review the assumptions, demand units and inventory scale before operational use.

## Reproduction

From the repository root:

```powershell
python testing\ai\validate_ai_outputs.py
```

Outputs:

- `testing/results/M15-03-ai-validation-results.json`
- `testing/results/M15-03-ai-validation-report.md`
