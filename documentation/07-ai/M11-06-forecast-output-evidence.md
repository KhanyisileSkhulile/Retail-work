# M11-06 — Forecast Outputs and Visualizations

## Objective

Generate row-level forecasts from the saved Ridge Regression model, plus summary data and charts for the chronological test period.

## Forecast run

| Item | Result |
|---|---|
| Model | Ridge Regression |
| Target | `Units Sold` |
| Forecast approach | Rolling one-step-ahead chronological holdout |
| Model fitting period ends | 2023-09-13 |
| Forecast period | 2023-09-14 to 2024-01-01 |
| Forecast rows | 11,000 |
| Unique forecast dates | 110 |
| Features | 58 |
| MAE | 88.453325 |
| RMSE | 107.996727 |
| Test data used for training | No |
| Model retrained during forecasting | No |

Forecasts are rolling one-step-ahead predictions: demand observed on earlier dates is used as history for later dates. They are not a fixed multi-day forecast made without any new observations.

## Generated outputs

- Row-level forecasts: `python-ai/forecasting/outputs/retail_demand_forecasts_m11_06.csv`
- Daily aggregate summary: `python-ai/forecasting/outputs/retail_demand_daily_summary_m11_06.csv`
- Metrics summary: `python-ai/forecasting/outputs/retail_demand_forecast_summary_m11_06.json`

## Generated charts

- Daily actual versus forecast: `python-ai/forecasting/outputs/daily_actual_vs_forecast_m11_06.png`
- Actual versus forecast scatter plot: `python-ai/forecasting/outputs/actual_vs_forecast_scatter_m11_06.png`
- Absolute forecast error distribution: `python-ai/forecasting/outputs/forecast_error_distribution_m11_06.png`

## Reproduce

Run from the repository root:

```powershell
python .\python-ai\forecasting\forecast.py
```

The script loads the saved model and processed dataset. It does not retrain or overwrite the trained model.
