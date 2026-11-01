"""M14-03: Validate and report application demand forecast integration."""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SERVICE_DIR = REPO_ROOT / "application" / "backend" / "forecasts"

if str(SERVICE_DIR) not in sys.path:
    sys.path.insert(0, str(SERVICE_DIR))

from service import (  # noqa: E402
    build_daily_summary,
    load_forecast_metadata,
    load_forecasts,
    summarize_forecasts,
    validate_forecast_metadata,
)


REPORT_FILE = (
    REPO_ROOT
    / "python-ai"
    / "forecasting"
    / "M14-03-forecast-integration-report.md"
)


def main():
    """Load, validate and summarize the M11-06 forecast artifacts."""
    forecasts = load_forecasts()
    metadata = load_forecast_metadata()
    validate_forecast_metadata(forecasts, metadata)

    summary = summarize_forecasts(forecasts)
    daily = build_daily_summary(forecasts)

    if len(daily) != metadata["unique_forecast_dates"]:
        raise RuntimeError(
            "Daily summary row count does not match forecast metadata."
        )

    report = f"""# M14-03 — Demand Forecast Integration Evidence

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
| Model | {metadata['model_name']} |
| Target | `{metadata.get('target_column', 'Not supplied')}` |
| Method | {metadata.get('forecasting_method', 'Not supplied')} |
| Forecast period | {summary['start_date']} to {summary['end_date']} |
| Model fitting period ends | {metadata.get('fit_end_date', 'Not supplied')} |
| Forecast records | {summary['records']:,} |
| Unique dates | {len(daily):,} |
| Stores represented | {summary['stores']:,} |
| Products represented | {summary['products']:,} |
| Mean Absolute Error (MAE) | {summary['mae']:.6f} |
| Root Mean Squared Error (RMSE) | {summary['rmse']:.6f} |

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
{summary['start_date']} to {summary['end_date']}; it is **not** a new
seven-day future forecast. The application labels it accordingly and
shows actual demand alongside predicted demand.

## Verification

Run from the repository root:

```powershell
python .\\python-ai\\forecasting\\integrate_forecasts.py
python -m unittest discover -s python-ai/tests -v
```

The integration script completed successfully when this report was generated.
"""

    REPORT_FILE.write_text(report, encoding="utf-8")

    print("M14-03 demand forecast integration verified.")
    print(f"Model: {metadata['model_name']}")
    print(f"Forecast records: {summary['records']:,}")
    print(f"Forecast dates: {summary['start_date']} to {summary['end_date']}")
    print(f"Stores: {summary['stores']}, products: {summary['products']}")
    print(f"MAE: {summary['mae']:.6f}")
    print(f"RMSE: {summary['rmse']:.6f}")
    print(f"Daily summary rows: {len(daily):,}")
    print(f"Evidence report: {REPORT_FILE}")


if __name__ == "__main__":
    main()
