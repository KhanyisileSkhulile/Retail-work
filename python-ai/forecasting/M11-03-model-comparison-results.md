# M11-03 — Candidate Forecasting Model Evaluation

## Objective

Compare candidate regression models against a historical-average
baseline using the same chronological validation period.

## Data and evaluation approach

| Item | Result |
|---|---|
| Raw dataset | `dataset/processed/retail_store_inventory_clean.csv` |
| Training rows | 51,100 |
| Training date range | 2022-01-01 to 2023-05-26 |
| Validation rows | 11,000 |
| Validation date range | 2023-05-27 to 2023-09-13 |
| Test rows | 11,000 |
| Test split used for model selection | No |
| Number of model features | 58 |
| Demand-history features included | demand_lag_1, demand_lag_7, demand_lag_14, demand_rolling_mean_7, demand_rolling_mean_28 |

All candidate models use the same training rows, validation rows,
feature columns and target (`Units Sold`).

Demand-history features are evaluated for rolling one-step-ahead
forecasting, where previously observed demand is available when making
the next prediction.

## Metrics

- **MAE (Mean Absolute Error):** average absolute prediction error.
- **RMSE (Root Mean Squared Error):** penalizes larger errors more strongly.

Lower values indicate better validation performance.

## Validation comparison

| Model | MAE | RMSE | Fit seconds | Prediction seconds |
|---|---:|---:|---:|---:|
| Ridge Regression | 89.7752 | 109.7737 | 1.271 | 0.011 |
| Store-Product Historical Mean | 89.7934 | 109.8169 | 0.687 | 0.370 |
| HistGradientBoosting | 89.8343 | 109.8009 | 0.307 | 0.005 |
| Random Forest | 90.1691 | 110.0959 | 6.155 | 0.031 |

## Best validation result

The lowest-MAE result is **Ridge Regression**, with MAE
**89.7752** and RMSE **109.7737**.

This identifies the best result on the validation period only. The
test split remains untouched and should be reserved for a later,
final evaluation.

## Reproducible evidence

- Candidate models: `python-ai/forecasting/models.py`
- Evaluation script: `python-ai/forecasting/evaluation.py`
- Training split: `dataset/processed/retail_forecasting_train_m11_03.csv`
- Validation split: `dataset/processed/retail_forecasting_validation_m11_03.csv`
- Saved test split: `dataset/processed/retail_forecasting_test_m11_03.csv`
- Comparison metrics: `dataset/processed/retail_forecasting_model_comparison_m11_03.csv`
- Row-level predictions: `dataset/processed/retail_forecasting_model_predictions_m11_03.csv`

## Limitations

Results apply to this dataset and validation period. The best validation
model is not guaranteed to perform best on unseen test data.
