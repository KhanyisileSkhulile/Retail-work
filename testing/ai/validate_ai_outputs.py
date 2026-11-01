"""M15-03 validation of saved forecasting, reorder and stockout outputs.

Audits existing artefacts only; it does not retrain models or alter decision rules.
Run from the repository root:
    python testing/ai/validate_ai_outputs.py
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

KEYS = ["Date", "Store ID", "Product ID"]
FORECAST_REQUIRED = set(KEYS + [
    "Actual Units Sold", "Forecast Units Sold", "Absolute Error"
])
REORDER_REQUIRED = set(KEYS + [
    "Inventory Level", "Forecast Units Sold", "Demand Used for Recommendation",
    "recommendation_status", "suggested_order_quantity"
])
STOCKOUT_REQUIRED = set(KEYS + [
    "Inventory Level", "Forecast Units Sold", "Demand Used for Detection",
    "stockout_status", "days_of_cover"
])
REORDER_STATUSES = {"REORDER_NOW", "WATCH", "HEALTHY", "DATA_REQUIRED", "INSUFFICIENT_HISTORY"}
STOCKOUT_STATUSES = {
    "STOCKOUT", "STOCKOUT_RISK", "WATCH", "NO_STOCKOUT_RISK",
    "DATA_REQUIRED", "INSUFFICIENT_HISTORY",
}


def _check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str,
           severity: str = "FAIL") -> None:
    checks.append({"check": name, "status": "PASS" if passed else severity, "detail": detail})


def _read_json(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(f"Required validation input is missing: {path}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _keys(frame: pd.DataFrame) -> set[tuple[str, str, str]]:
    dates = pd.to_datetime(frame["Date"], errors="coerce").dt.strftime("%Y-%m-%d")
    return set(zip(dates, frame["Store ID"].astype(str), frame["Product ID"].astype(str)))


def validate_frames(
    forecasts: pd.DataFrame,
    reorder: pd.DataFrame,
    stockout: pd.DataFrame,
    evaluation: dict,
    forecast_summary: dict,
    reorder_summary: dict,
    stockout_summary: dict,
) -> dict:
    """Validate artefact schemas, temporal/evaluation metadata, alignment and status quality."""
    checks: list[dict[str, Any]] = []

    # Forecast schema, values, key integrity and recomputed error metrics.
    missing = FORECAST_REQUIRED - set(forecasts.columns)
    _check(checks, "forecast_schema", not missing,
           "All required forecast columns are present." if not missing else f"Missing columns: {sorted(missing)}")
    if missing:
        return _result(checks, {})

    f = forecasts.copy()
    f["Date"] = pd.to_datetime(f["Date"], errors="coerce")
    for column in ("Actual Units Sold", "Forecast Units Sold", "Absolute Error"):
        f[column] = pd.to_numeric(f[column], errors="coerce")
    valid_numeric = np.isfinite(f[["Actual Units Sold", "Forecast Units Sold", "Absolute Error"]].to_numpy()).all()
    _check(checks, "forecast_numeric_values", bool(valid_numeric),
           "Actuals, forecasts and absolute errors are finite numeric values.")
    _check(checks, "forecast_non_negative", bool((f[["Actual Units Sold", "Forecast Units Sold"]] >= 0).all().all()),
           "Actual demand and predicted demand are non-negative.")
    _check(checks, "forecast_dates_valid", bool(f["Date"].notna().all()),
           "All forecast dates parse successfully.")
    duplicates = int(f.duplicated(KEYS).sum())
    _check(checks, "forecast_business_keys_unique", duplicates == 0,
           f"Duplicate Date/Store/Product keys: {duplicates}.")

    computed_abs = (f["Actual Units Sold"] - f["Forecast Units Sold"]).abs()
    error_consistent = bool(np.allclose(computed_abs, f["Absolute Error"], rtol=1e-5, atol=1e-5))
    _check(checks, "forecast_absolute_error_consistent", error_consistent,
           "Absolute Error matches |Actual Units Sold - Forecast Units Sold|.")

    mae = float(computed_abs.mean()) if len(f) else float("nan")
    rmse = float(np.sqrt(np.mean((f["Actual Units Sold"] - f["Forecast Units Sold"]) ** 2))) if len(f) else float("nan")
    expected_mae = float(forecast_summary.get("mae", float("nan")))
    expected_rmse = float(forecast_summary.get("rmse", float("nan")))
    metric_match = bool(np.isfinite([mae, rmse, expected_mae, expected_rmse]).all()
                        and np.isclose(mae, expected_mae, rtol=1e-5, atol=1e-5)
                        and np.isclose(rmse, expected_rmse, rtol=1e-5, atol=1e-5))
    _check(checks, "forecast_metrics_recomputed", metric_match,
           f"CSV MAE={mae:.6f}, RMSE={rmse:.6f}; M11-06 summary MAE={expected_mae:.6f}, RMSE={expected_rmse:.6f}.")

    eval_match = bool(
        np.isclose(mae, float(evaluation.get("mae", float("nan"))), rtol=1e-5, atol=1e-5)
        and np.isclose(rmse, float(evaluation.get("rmse", float("nan"))), rtol=1e-5, atol=1e-5)
    )
    _check(checks, "m11_05_and_m11_06_metrics_agree", eval_match,
           "Recomputed rolling-output metrics agree with the M11-05 temporal holdout evaluation.")
    no_leakage = (evaluation.get("test_data_used_for_training") is False
                  and evaluation.get("model_retrained_during_evaluation") is False
                  and forecast_summary.get("test_data_used_for_training") is False
                  and forecast_summary.get("model_retrained_during_forecasting") is False)
    _check(checks, "forecast_no_test_leakage", no_leakage,
           "M11-05/M11-06 metadata explicitly reports no test-data fitting or model refitting.")
    date_range_match = (
        str(f["Date"].min().date()) == forecast_summary.get("forecast_start_date")
        and str(f["Date"].max().date()) == forecast_summary.get("forecast_end_date")
        and int(f["Date"].nunique()) == int(forecast_summary.get("unique_forecast_dates", -1))
    ) if len(f) else False
    _check(checks, "forecast_date_coverage", date_range_match,
           f"CSV covers {f['Date'].min().date() if len(f) else 'N/A'} to {f['Date'].max().date() if len(f) else 'N/A'} across {f['Date'].nunique() if len(f) else 0} unique dates.")
    row_count_match = (len(f) == int(forecast_summary.get("forecast_rows", -1))
                       and len(f) == int(evaluation.get("test_rows", -2)))
    _check(checks, "forecast_row_count", row_count_match,
           f"Forecast CSV rows={len(f)}, M11-06 summary={forecast_summary.get('forecast_rows')}, M11-05 test rows={evaluation.get('test_rows')}.")

    # Restocking output schema and row alignment.
    reorder_missing = REORDER_REQUIRED - set(reorder.columns)
    _check(checks, "reorder_schema", not reorder_missing,
           "All required reorder columns are present." if not reorder_missing else f"Missing columns: {sorted(reorder_missing)}")
    stockout_missing = STOCKOUT_REQUIRED - set(stockout.columns)
    _check(checks, "stockout_schema", not stockout_missing,
           "All required stockout columns are present." if not stockout_missing else f"Missing columns: {sorted(stockout_missing)}")
    if reorder_missing or stockout_missing:
        return _result(checks, {"mae": mae, "rmse": rmse, "forecast_rows": len(f)})

    r = reorder.copy()
    s = stockout.copy()
    for frame in (r, s):
        frame["Date"] = pd.to_datetime(frame["Date"], errors="coerce")
    r_keys, s_keys, f_keys = _keys(r), _keys(s), _keys(f)
    _check(checks, "reorder_forecast_key_alignment", r_keys == f_keys,
           f"Forecast keys={len(f_keys)}, reorder keys={len(r_keys)}, missing={len(f_keys-r_keys)}, extra={len(r_keys-f_keys)}.")
    _check(checks, "stockout_forecast_key_alignment", s_keys == f_keys,
           f"Forecast keys={len(f_keys)}, stockout keys={len(s_keys)}, missing={len(f_keys-s_keys)}, extra={len(s_keys-f_keys)}.")
    _check(checks, "reorder_key_uniqueness", not r.duplicated(KEYS).any(),
           f"Duplicate reorder keys: {int(r.duplicated(KEYS).sum())}.")
    _check(checks, "stockout_key_uniqueness", not s.duplicated(KEYS).any(),
           f"Duplicate stockout keys: {int(s.duplicated(KEYS).sum())}.")

    quantities = pd.to_numeric(r["suggested_order_quantity"], errors="coerce")
    qty_valid = bool(quantities.notna().all() and np.isfinite(quantities.to_numpy()).all() and (quantities >= 0).all())
    _check(checks, "reorder_quantities_valid", qty_valid,
           "Suggested order quantities are finite, present and non-negative.")
    reorder_statuses = set(r["recommendation_status"].dropna().astype(str).unique())
    _check(checks, "reorder_status_values", reorder_statuses.issubset(REORDER_STATUSES),
           f"Observed statuses: {sorted(reorder_statuses)}.")
    reorder_now = r["recommendation_status"].astype(str).eq("REORDER_NOW")
    positive_when_reorder = bool((quantities[reorder_now] > 0).all())
    _check(checks, "reorder_now_has_positive_quantity", positive_when_reorder,
           f"REORDER_NOW rows={int(reorder_now.sum())}; all have positive suggested quantities.")

    stock_statuses = set(s["stockout_status"].dropna().astype(str).unique())
    _check(checks, "stockout_status_values", stock_statuses.issubset(STOCKOUT_STATUSES),
           f"Observed statuses: {sorted(stock_statuses)}.")
    stock_levels = pd.to_numeric(s["Inventory Level"], errors="coerce")
    observed_stockout_consistent = bool((stock_levels[s["stockout_status"].astype(str).eq("STOCKOUT")] == 0).all())
    _check(checks, "observed_stockout_zero_stock", observed_stockout_consistent,
           "Rows labelled STOCKOUT have zero recorded inventory.")
    risk_rows = s["stockout_status"].astype(str).eq("STOCKOUT_RISK")
    risk_positive_stock = bool((stock_levels[risk_rows] > 0).all())
    _check(checks, "stockout_risk_positive_stock", risk_positive_stock,
           "Rows labelled STOCKOUT_RISK have positive recorded stock.")

    # Reconcile summary JSON with the actual CSV counts, including the important imbalance warning.
    reorder_counts = {str(k): int(v) for k, v in r["recommendation_status"].value_counts(dropna=False).items()}
    stockout_counts = {str(k): int(v) for k, v in s["stockout_status"].value_counts(dropna=False).items()}
    reorder_summary_match = (
        int(reorder_summary.get("records_processed", -1)) == len(r)
        and reorder_summary.get("status_counts") == reorder_counts
        and int(reorder_summary.get("reorder_now_count", -1)) == int(reorder_now.sum())
    )
    _check(checks, "reorder_summary_matches_csv", reorder_summary_match,
           f"CSV status counts={reorder_counts}; summary counts={reorder_summary.get('status_counts')}.")
    stockout_summary_match = (
        int(stockout_summary.get("records_processed", -1)) == len(s)
        and stockout_summary.get("status_counts") == stockout_counts
        and int(stockout_summary.get("observed_stockout_count", -1)) == int(s["stockout_status"].astype(str).eq("STOCKOUT").sum())
        and int(stockout_summary.get("stockout_risk_count", -1)) == int(risk_rows.sum())
    )
    _check(checks, "stockout_summary_matches_csv", stockout_summary_match,
           f"CSV status counts={stockout_counts}; summary counts={stockout_summary.get('status_counts')}.")

    reorder_share = float(reorder_now.mean()) if len(r) else 0.0
    risk_share = float(risk_rows.mean()) if len(s) else 0.0
    if reorder_share >= 0.95:
        _check(checks, "reorder_status_distribution", False,
               f"{reorder_share:.1%} of rows are REORDER_NOW; review demand/stock scaling and baseline assumptions before operational use.",
               severity="WARN")
    else:
        _check(checks, "reorder_status_distribution", True,
               f"REORDER_NOW share is {reorder_share:.1%}.")
    if risk_share >= 0.95:
        _check(checks, "stockout_status_distribution", False,
               f"{risk_share:.1%} of rows are STOCKOUT_RISK; this is a concentrated risk signal and should be reviewed before operational use.",
               severity="WARN")
    else:
        _check(checks, "stockout_status_distribution", True,
               f"STOCKOUT_RISK share is {risk_share:.1%}.")

    metrics = {
        "mae": mae,
        "rmse": rmse,
        "forecast_rows": int(len(f)),
        "forecast_unique_dates": int(f["Date"].nunique()),
        "forecast_start_date": str(f["Date"].min().date()),
        "forecast_end_date": str(f["Date"].max().date()),
        "reorder_rows": int(len(r)),
        "reorder_status_counts": reorder_counts,
        "reorder_now_share": reorder_share,
        "total_suggested_order_units": int(quantities.sum()),
        "stockout_rows": int(len(s)),
        "stockout_status_counts": stockout_counts,
        "stockout_risk_share": risk_share,
        "observed_stockout_count": int(s["stockout_status"].astype(str).eq("STOCKOUT").sum()),
    }
    return _result(checks, metrics)


def _result(checks: list[dict[str, Any]], metrics: dict) -> dict:
    statuses = {item["status"] for item in checks}
    overall = "FAIL" if "FAIL" in statuses else ("PASS_WITH_WARNINGS" if "WARN" in statuses else "PASS")
    return {"issue": "M15-03", "overall_status": overall, "checks": checks, "metrics": metrics}


def validate_repository(repo_root: Path) -> dict:
    """Load checked-in validation artefacts from a repository working tree."""
    root = Path(repo_root)
    forecast = pd.read_csv(root / "python-ai/forecasting/outputs/retail_demand_forecasts_m11_06.csv")
    reorder = pd.read_csv(root / "python-ai/restocking/outputs/retail_restocking_recommendations_m12_02.csv")
    stockout = pd.read_csv(root / "python-ai/restocking/outputs/retail_stockout_detection_m12_03.csv")
    evaluation = _read_json(root / "python-ai/forecasting/artifacts/retail_demand_ridge_test_evaluation.json")
    forecast_summary = _read_json(root / "python-ai/forecasting/outputs/retail_demand_forecast_summary_m11_06.json")
    reorder_summary = _read_json(root / "python-ai/restocking/outputs/retail_restocking_summary_m12_02.json")
    stockout_summary = _read_json(root / "python-ai/restocking/outputs/retail_stockout_detection_summary_m12_03.json")
    result = validate_frames(forecast, reorder, stockout, evaluation,
                             forecast_summary, reorder_summary, stockout_summary)
    result["validated_at_utc"] = pd.Timestamp.now(tz="UTC").isoformat()
    result["source_files"] = [
        "python-ai/forecasting/outputs/retail_demand_forecasts_m11_06.csv",
        "python-ai/forecasting/artifacts/retail_demand_ridge_test_evaluation.json",
        "python-ai/forecasting/outputs/retail_demand_forecast_summary_m11_06.json",
        "python-ai/restocking/outputs/retail_restocking_recommendations_m12_02.csv",
        "python-ai/restocking/outputs/retail_restocking_summary_m12_02.json",
        "python-ai/restocking/outputs/retail_stockout_detection_m12_03.csv",
        "python-ai/restocking/outputs/retail_stockout_detection_summary_m12_03.json",
    ]
    return result


def write_report(result: dict, results_dir: Path) -> None:
    results_dir.mkdir(parents=True, exist_ok=True)
    json_path = results_dir / "M15-03-ai-validation-results.json"
    md_path = results_dir / "M15-03-ai-validation-report.md"
    json_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    rows = "\n".join(
        f"| {item['check']} | **{item['status']}** | {item['detail']} |"
        for item in result["checks"]
    )
    metrics = result.get("metrics", {})
    report = f'''# M15-03 — AI Forecasting and Restocking Validation

## Overall result: {result['overall_status']}

This validation audits the saved M11-05/M11-06 forecasting outputs and M12-02/M12-03 restocking outputs. It does not retrain the model or change reorder/stockout thresholds.

## Forecasting summary

- MAE: {metrics.get('mae', 'N/A')}
- RMSE: {metrics.get('rmse', 'N/A')}
- Forecast rows: {metrics.get('forecast_rows', 'N/A')}
- Date coverage: {metrics.get('forecast_start_date', 'N/A')} to {metrics.get('forecast_end_date', 'N/A')}
- Model: Ridge Regression (M11-05/M11-06 saved evidence)

## Restocking summary

- Reorder rows: {metrics.get('reorder_rows', 'N/A')}
- Reorder status counts: `{metrics.get('reorder_status_counts', {})}`
- REORDER_NOW share: {metrics.get('reorder_now_share', 0):.1%}
- Total suggested order units: {metrics.get('total_suggested_order_units', 'N/A')}
- Stockout rows: {metrics.get('stockout_rows', 'N/A')}
- Stockout status counts: `{metrics.get('stockout_status_counts', {})}`
- STOCKOUT_RISK share: {metrics.get('stockout_risk_share', 0):.1%}
- Observed stockout records: {metrics.get('observed_stockout_count', 'N/A')}

## Validation checks

| Check | Result | Detail |
|---|---|---|
{rows}

## Interpretation and limitations

- Forecast MAE/RMSE are error measures on the saved historical evaluation period; they are not guarantees of future accuracy.
- The M11-05 metadata must confirm that the test data was not used for training and the evaluation did not refit the saved model.
- Reorder recommendations and stockout flags are historical replay outputs based on M12-01 assumptions. They do not represent live inventory, supplier orders or current alerts.
- A very high share of one status is reported as a warning, not silently accepted as balanced performance. Review the assumptions, demand units and inventory scale before operational use.

## Reproduction

From the repository root:

```powershell
python testing\\ai\\validate_ai_outputs.py
```

Outputs:

- `testing/results/M15-03-ai-validation-results.json`
- `testing/results/M15-03-ai-validation-report.md`
'''
    md_path.write_text(report, encoding="utf-8")


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    result = validate_repository(repo_root)
    write_report(result, repo_root / "testing" / "results")
    print(f"M15-03 overall status: {result['overall_status']}")
    for item in result["checks"]:
        print(f"[{item['status']}] {item['check']}: {item['detail']}")
    print("Reports written to testing/results/")
    return 1 if result["overall_status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
