# M17-04 — AI and Model Evidence

**Issue:** Retail-X #90
**Purpose:** Consolidate the existing AI, forecasting, chatbot, and restocking evidence.
**Scope:** Documentation and evidence verification. This task does not retrain the model or change forecasting and restocking logic.

## 1. Dataset and temporal split

The approved dataset is `dataset/raw/retail_store_inventory.csv`.

- Records: 73,100
- Columns: 15
- Forecast target: `Units Sold`

The chronological split is:

| Split | Records | Date range |
|---|---:|---|
| Training | 51,100 | 2022-01-01 to 2023-05-26 |
| Validation | 11,000 | 2023-05-27 to 2023-09-13 |
| Test | 11,000 | 2023-09-14 to 2024-01-01 |

The selected model was fitted using the 62,100 training and validation records. The 11,000 test records were kept separate for final holdout evaluation.

## 2. Forecasting model

The selected model is Ridge Regression with:

- 58 engineered features
- StandardScaler preprocessing
- Alpha: 10.0
- Demand history features including lags of 1, 7 and 14 days and rolling means of 7 and 28 days

Validation model comparison:

| Model | Validation MAE | Validation RMSE |
|---|---:|---:|
| Ridge Regression | 89.7752 | 109.7737 |
| Store-Product Historical Mean | 89.7934 | 109.8169 |
| HistGradientBoosting | 89.8343 | 109.8009 |
| Random Forest | 90.1691 | 110.0959 |

Ridge achieved the lowest validation MAE, although its improvement over the historical-mean baseline was small.

Final temporal holdout results:

| Metric | Result |
|---|---:|
| MAE | 88.453325 |
| RMSE | 107.996727 |
| Test records | 11,000 |
| Unique test dates | 110 |

The holdout results are based on historical test-period predictions. The M11-06 forecast outputs represent rolling one-step-ahead predictions over historical data; they should not be described as an unconstrained future forecast horizon.

## 3. Saved model and forecast evidence

Model artifacts:

- `python-ai/forecasting/artifacts/retail_demand_ridge_model.joblib`
- `python-ai/forecasting/artifacts/retail_demand_ridge_model_metadata.json`
- `python-ai/forecasting/artifacts/retail_demand_ridge_test_evaluation.json`

Forecast outputs:

- `python-ai/forecasting/outputs/retail_demand_forecasts_m11_06.csv`
- `python-ai/forecasting/outputs/retail_demand_daily_summary_m11_06.csv`
- `python-ai/forecasting/outputs/retail_demand_forecast_summary_m11_06.json`

Visual evidence:

- `python-ai/forecasting/outputs/actual_vs_forecast_scatter_m11_06.png`
- `python-ai/forecasting/outputs/daily_actual_vs_forecast_m11_06.png`
- `python-ai/forecasting/outputs/forecast_error_distribution_m11_06.png`

Supporting reports are available in `python-ai/forecasting/`, including the baseline, feature engineering, model comparison, trained model, temporal holdout, and M14-03 integration reports.

## 4. Restocking and stockout evidence

The existing restocking evidence covers reorder calculations, reorder recommendations, stockout detection, assumptions, and scenario validation.

The M15-03 validation run reported:

- Total checks: 27
- Passed: 25
- Warnings: 2
- Failed: 0
- Overall status: `PASS_WITH_WARNINGS`

The two warnings identify concentrated classifications in the historical replay:

- All 11,000 reorder records were classified as `REORDER_NOW`.
- All 11,000 stockout records were classified as `STOCKOUT_RISK`.

The stockout output contained zero observed stockouts. A `STOCKOUT_RISK` classification is a risk flag, not proof that a stockout occurred.

The restocking recommendations are advisory outputs and do not place purchase orders.

## 5. Validation and integration evidence

The following results were observed during this work:

| Verification | Result |
|---|---|
| M12-05 restocking test suite | 9 tests passed |
| M15-03 AI validation tests | 6 tests passed |
| AI output validation | 25 passed, 2 warnings, 0 failed |
| M14-03 forecast integration verification | Completed successfully |

Run the validator from the repository root with:

`python .\testing\ai\validate_ai_outputs.py`

The M15-03 evidence is stored in:

- `testing/results/M15-03-ai-validation-report.md`
- `testing/results/M15-03-ai-validation-results.json`

## 6. Chatbot evidence and limitations

The chatbot uses a deterministic keyword-based intent classifier and reads saved CSV data. It is not connected to an external large language model or live point-of-sale system.

Supported query areas include:

- Inventory information
- Observed sales and top-selling products
- Saved demand forecasts
- Reorder recommendations
- Stockout risk
- Sales-factor comparisons
- Data availability and help

The chatbot relies on recognized product/store identifiers and explicit dates. It should not be presented as having live supplier, inventory, or point-of-sale access.

## 7. Evidence index

The consolidated AI evidence is maintained under `documentation/07-ai/`:

- `M11-06-forecast-output-evidence.md`
- `M12-01-restocking-logic-and-assumptions.md`
- `M12-02-reorder-recommendations.md`
- `M12-03-stockout-detection.md`
- `M12-05-restocking-validation.md`
- `M13-01-chatbot-intents.md`
- `M13-02-chatbot-query-layer.md`
- `M13-03-assistant-service.md`
- `M13-04-chatbot-data-integration.md`
- `M15-03-ai-validation.md`

## 8. Evidence interpretation and limitations

The results document performance on the supplied historical dataset. They do not establish performance on live shop data or guarantee future demand accuracy.

A separate root-level `retailai_model_evaluation.csv` has been identified as containing a different set of model metrics from the canonical Ridge temporal holdout evidence. Those figures must not be combined with the M11-05/M15-03 results until their provenance is reconciled.

The saved model and forecast artifacts are evidence of the existing model run. Reproducing the forecasting run requires the processed dataset at `dataset/processed/retail_store_inventory_clean.csv`; that file was not present in this worktree during this documentation task.

## 9. M17-04 completion objective

This document provides a central entry point to the existing AI and model evidence. The supporting reports, saved artifacts, validation outputs, and charts remain in their respective locations.

No model retraining, changes to forecasting logic, or changes to restocking assumptions are included in this documentation task.
