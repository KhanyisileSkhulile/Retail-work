# M12-03 — Stockout Detection

## Purpose

Flag observed zero-stock records and identify positive-stock records whose demand-adjusted stock is at or below the M12-01 baseline reorder point. Results are advisory and do not guarantee future availability.

## Detection rules

- `STOCKOUT`: on-hand inventory is exactly zero, regardless of forecast availability.
- `STOCKOUT_RISK`: positive stock is at or below the baseline reorder point (lead time plus safety stock).
- `WATCH`: stock is above the reorder point but below target stock.
- `NO_STOCKOUT_RISK`: stock meets or exceeds target stock under the baseline assumptions.
- `DATA_REQUIRED`: inventory is missing, invalid or negative.
- `INSUFFICIENT_HISTORY`: stock is positive but neither a model forecast nor prior demand is available.

Demand defaults to a valid saved M11-06 model forecast. If missing, detection uses only the available prior seven days of observed demand for the same store-product series; it never uses future actual sales as a fallback. Negative demand is normalized to zero.

## Configured assumptions

| Setting | Value |
|---|---:|
| Supplier lead time | 3 days |
| Review period | 1 day(s) |
| Safety stock buffer | 1 day(s) of demand |

## Run summary

| Item | Result |
|---|---|
| Records processed | 11,000 |
| Store-product pairs | 100 |
| Date range | 2023-09-14 to 2024-01-01 |
| Observed stockouts | 0 |
| Stockout-risk flags | 11,000 |
| Watch flags | 0 |

## Status counts

| Status | Records |
|---|---:|
| STOCKOUT_RISK | 11,000 |

## Output

- CSV: `python-ai/restocking/outputs/retail_stockout_detection_m12_03.csv`
- Summary: `python-ai/restocking/outputs/retail_stockout_detection_summary_m12_03.json`

## Reproduce

From the repository root, run:

```powershell
python .\python-ai\restocking\stockout.py
```

**Scope note:** this is historical replay using inventory and forecasts aligned to dates in the M11-06 evaluation period. It is not a live current-stock monitoring service.
