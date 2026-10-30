# M13-02 — RetailAI Chatbot Query Layer

## Objective
Provide read-only data query functions for the M13-01 intent catalogue. This layer retrieves and aggregates data; it does not classify messages, generate conversational responses, connect an LLM, or provide live store connectivity.

## Functions
- `inventory_level`: historical inventory by store, product, category and as-of date.
- `sales_summary`: observed units sold and date coverage.
- `top_selling_products`: rank products by observed units sold.
- `demand_forecast`: retrieve M11-06 forecasts for a required store/product pair.
- `reorder_recommendations`: retrieve M12-02 advisory results.
- `stockout_status`: retrieve M12-03 observed stockout/risk results.
- `sales_factor_analysis`: descriptive comparisons for weather, promotion, discount or seasonality.
- `data_availability`: source presence, record counts and date coverage.

## Safeguards
- Uses the approved cleaned inventory dataset and committed M11-06, M12-02 and M12-03 output CSVs.
- Applies store and product filters independently and case-insensitively.
- Uses inclusive date filters; reversed date ranges are rejected.
- Limits ranked results to 1–100.
- Raises `QueryDataError` for missing sources, missing required columns or unsupported factors.
- Forecast queries require both store and product IDs.
- Factor comparisons are descriptive, not causal.
- All functions are read-only. No orders are created and no data is modified.
- Data is historical; `data_availability` reports `live_data_connected: false`.

## Verification
Run from the repository root:
```powershell
python -m unittest discover -s .\testing\ai -p "test_chatbot_queries.py" -v
```
