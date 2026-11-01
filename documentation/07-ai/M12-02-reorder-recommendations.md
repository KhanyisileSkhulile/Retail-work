# M12-02 — Reorder Recommendations

## Objective

Generate advisory inventory reorder recommendations from the M11-06 forecast output and inventory records using the baseline assumptions defined in M12-01.

## Method

- Match forecast and inventory data by date, store and product.
- Prefer the saved model forecast; use the prior 7-day mean of observed demand only when a model forecast is unavailable.
- Calculate safety stock, reorder point, target stock and suggested order quantity.
- Flag missing/invalid inventory or unavailable demand instead of inventing quantities.
- Generate one recommendation per matched forecast row; recommendations are advisory and do not place orders.

## Configured assumptions

| Setting | Value |
|---|---:|
| Supplier lead time | 3 days |
| Review period | 1 day(s) |
| Safety-stock buffer | 1 day(s) of demand |

These are provisional defaults and should be updated when verified supplier and operational data becomes available.

## Run summary

| Item | Result |
|---|---|
| Records processed | 11,000 |
| Store-product pairs | 100 |
| Date range | 2023-09-14 to 2024-01-01 |
| REORDER_NOW records | 11,000 |
| Records with positive order quantity | 11,000 |
| Total suggested order units across historical records | 4,505,211 |

## Status counts

| Status | Records |
|---|---:|
| REORDER_NOW | 11,000 |

## Outputs

- Recommendations CSV: `python-ai/restocking/outputs/retail_restocking_recommendations_m12_02.csv`
- Summary JSON: `python-ai/restocking/outputs/retail_restocking_summary_m12_02.json`

## Reproduce

Run from the repository root:

```powershell
python .\python-ai\restocking\recommendations.py
```

**Scope note:** this output is a historical replay using inventory values from the dates in the forecasting test period. It is not a live current-stock recommendation feed.
