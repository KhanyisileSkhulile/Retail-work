# M14-03 — Demand Forecast Integration Evidence

## Objective

Connect the completed M11-06 demand forecasting output to the application
backend and verify that the application can load, validate, filter and
summarize forecast results.

## Integrated source artifacts

- Forecast CSV: `python-ai/forecasting/outputs/retail_demand_forecasts_m11_06.csv`
- Forecast metadata: `python-ai/forecasting/outputs/retail_demand_forecast_summary_m11_06.json`
- Application service: `application/backend/forecasts/service.py`

## Forecast metadata

| Item | Result |
|---|---|
| Model | Ridge Regression |
| Target | `Units Sold` |
| Method | Rolling one-step-ahead chronological holdout |
| Forecast period | 2023-09-14 to 2024-01-01 |
| Model fitting period ends | 2023-09-13 |
| Forecast records | 11,000 |
| Unique dates | 110 |
| Stores represented | 5 |
| Products represented | 20 |
| Mean Absolute Error (MAE) | 88.453325 |
| Root Mean Squared Error (RMSE) | 107.996727 |

## Integration checks

- Required CSV columns are present.
- Dates and numeric forecast values are valid and finite.
- Absolute error values match the actual-versus-forecast differences.
- Each Date/Store ID/Product ID combination is unique.
- JSON metadata row count, date range and error metrics match the CSV.
- Store, product and inclusive date filters are available to the application.
- Daily actual-demand and forecast-demand summaries can be generated.

## Forecast interpretation

The supplied M11-06 artifact contains rolling one-step-ahead predictions
for a chronological holdout period. It is an evaluation dataset covering
2023-09-14 to 2024-01-01; it is **not** a new
seven-day future forecast. The application labels it accordingly and
shows actual demand alongside predicted demand.

## Verification

Run from the repository root:

```powershell
python .\python-ai\forecasting\integrate_forecasts.py
python -m unittest discover -s python-ai/tests -v
```

The integration script completed successfully when this report was generated.
