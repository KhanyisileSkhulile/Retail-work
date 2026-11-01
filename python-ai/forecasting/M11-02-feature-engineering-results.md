# M11-02 — Forecasting Feature Engineering Evidence

## Objective

Extend the existing M10-03 feature preparation with leakage-safe historical demand features for each store-product series.

## Features added

- `demand_lag_1`: previous observed demand
- `demand_lag_7`: demand seven observations earlier
- `demand_lag_14`: demand fourteen observations earlier
- `demand_rolling_mean_7`: mean of up to the previous seven observations
- `demand_rolling_mean_28`: mean of up to the previous twenty-eight observations

Every lag and rolling mean is shifted so the current row's `Units Sold` value is not used to construct that row's history features. Features are calculated independently for each store-product pair. Missing initial history is imputed using medians calculated from the training period only. Existing chronological split logic and one-hot category alignment are retained. `Demand Forecast`, `Units Ordered`, and `Inventory Level` remain excluded from model features.

## Verification

Run from the repository root:

```bash
python -m unittest discover -s python-ai/tests -p "test_feature_engineering.py" -v
python -m py_compile python-ai/forecasting/feature_engineering.py python-ai/tests/test_feature_engineering.py
```

The regression tests cover lag and rolling calculations, separation between store-product series, current-target leakage, finite prepared features, excluded columns, and chronological three-way splitting. Record the actual test output in the pull request before merging.

## Forecasting assumption

Lag features support rolling one-step-ahead forecasting: prior observed demand is available when each next-day prediction is made. A multi-day forecast made all at once must instead recursively feed predictions into later lag features or use a horizon-specific strategy.
