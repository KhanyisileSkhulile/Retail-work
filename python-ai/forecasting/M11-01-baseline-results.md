# M11-01 — Forecasting Baseline Results

## Objective

Establish a simple, reproducible benchmark for retail demand forecasting.

## Baseline method

For each store-product combination, predict demand using the mean
`Units Sold` observed for that combination in the training split.
The mean is calculated from training data only.

If a validation row belongs to a combination not present in training,
the overall training-set mean is used instead.

## Data used

| Item | Result |
|---|---|
| Training rows | 51,100 |
| Training date range | 2022-01-01 to 2023-05-26 |
| Validation rows | 11,000 |
| Validation date range | 2023-05-27 to 2023-09-13 |
| Store-product combinations learned | 100 |
| Global-mean fallbacks | 0 |
| Test split used | No |

## Validation results

| Metric | Result |
|---|---:|
| Mean Absolute Error (MAE) | 89.7934 |
| Root Mean Squared Error (RMSE) | 109.8169 |

MAE measures the average absolute prediction error in units sold.
RMSE penalizes larger errors more strongly. Lower values indicate better
predictions, and these results provide a benchmark for later models.

## Reproducible evidence

- Script: `python-ai/forecasting/baseline.py`
- Row-level predictions: `dataset/processed/retail_forecasting_baseline_validation_m11_01.csv`
- Training source: `dataset/processed/retail_forecasting_train_m10_04.csv`
- Validation source: `dataset/processed/retail_forecasting_validation_m10_04.csv`

The holdout test split was not used. Later model comparisons should use
the same validation period and metrics for a fair comparison.
