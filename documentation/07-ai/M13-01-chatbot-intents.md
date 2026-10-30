# M13-01 — RetailAI Chatbot Intent Definitions

## 1. Objective and scope

Define the supported user-request intents, example utterances, slots, clarification prompts, approved data sources and response rules for the RetailAI chatbot.

This issue establishes the contract for later work. It does **not** implement natural-language classification, database/CSV querying, response generation, an LLM connection or chatbot UI. Those responsibilities are handled by M13-02 (query layer), M13-03 (assistant service), M13-04 (connect to forecasts and inventory) and M13-05 (UI integration).

The machine-readable catalogue is `python-ai/chatbot/intents.py`.

## 2. Intent catalogue

| Intent | Purpose | Required slots | Optional slots | Main data source |
|---|---|---|---|---|
| `GREETING` | Greeting/opening | None | None | None |
| `HELP` | Explain supported questions | None | None | None |
| `INVENTORY_LEVEL` | Recorded on-hand inventory lookup | None | Store, product, category, date | Cleaned inventory dataset |
| `SALES_SUMMARY` | Historical units-sold summary | None | Store, product, category, region, date range | Cleaned inventory dataset |
| `TOP_SELLING_PRODUCTS` | Rank items by observed sales | None | Store, category, region, date range, result limit | Cleaned inventory dataset |
| `DEMAND_FORECAST` | Retrieve saved model forecasts | Store and product | Date range | M11-06 forecast CSV |
| `REORDER_RECOMMENDATION` | Retrieve advisory reorder result | None | Store, product, as-of date, result limit | M12-02 recommendation CSV |
| `STOCKOUT_STATUS` | Retrieve observed stockout/risk/watch status | None | Store, product, as-of date, result limit | M12-03 stockout CSV |
| `SALES_FACTOR_ANALYSIS` | Compare sales across recorded factors | Factor | Store, product, category, region, date range | Cleaned inventory dataset |
| `DATA_AVAILABILITY` | Explain available data and limitations | None | None | Dataset and output metadata |
| `UNKNOWN` | Unsupported or unclear message | None | None | None |

Canonical identifiers and their contracts are defined in `intents.py`. All optional filters must be applied independently and must never mix store-product series.

## 3. Slot definitions

| Slot | Meaning | Example |
|---|---|---|
| `store_id` | Store identifier | `S001` |
| `product_id` | Product identifier | `P0001` |
| `category` | Category value from the dataset | Use the dataset value; do not invent product names |
| `region` | Region value from the dataset | Use the dataset value |
| `start_date` | Inclusive start date | `2023-10-01` |
| `end_date` | Inclusive end date | `2023-10-31` |
| `as_of_date` | Inventory/recommendation record date | `2023-10-01` |
| `factor` | `weather`, `promotion`, `discount` or `seasonality` | `promotion` |
| `limit` | Maximum ranked results | `5` |

Dates should be normalized to `YYYY-MM-DD`. Invalid or reversed ranges should be clarified or rejected by the query layer. Product/store identifiers must be validated against the available data before a result is returned.

## 4. Example utterances and slot expectations

| Example question | Intent | Extracted slots |
|---|---|---|
| “Hi RetailAI” | `GREETING` | None |
| “What can you help me with?” | `HELP` | None |
| “How much stock does P0001 have at S001?” | `INVENTORY_LEVEL` | `product_id=P0001`, `store_id=S001` |
| “Summarise sales for P0004 last month” | `SALES_SUMMARY` | `product_id=P0004`, date range resolved from context |
| “Show the top 5 products at S002” | `TOP_SELLING_PRODUCTS` | `store_id=S002`, `limit=5` |
| “What was the forecast for P0001 at S001?” | `DEMAND_FORECAST` | `store_id=S001`, `product_id=P0001` |
| “What should S001 reorder for P0001?” | `REORDER_RECOMMENDATION` | `store_id=S001`, `product_id=P0001` |
| “Was P0001 at S001 at stockout risk?” | `STOCKOUT_STATUS` | `store_id=S001`, `product_id=P0001` |
| “How did promotions affect sales?” | `SALES_FACTOR_ANALYSIS` | `factor=promotion` |
| “Are these live stock figures?” | `DATA_AVAILABILITY` | None |
| “Can you do something unrelated?” | `UNKNOWN` | None |

## 5. Data-source contract and limitations

| Source | What it supports | Important limitation |
|---|---|---|
| `dataset/processed/retail_store_inventory_clean.csv` | Recorded inventory, actual units sold, category, region, weather, promotion, discount and seasonality | Historical project dataset; not a live store feed |
| `python-ai/forecasting/outputs/retail_demand_forecasts_m11_06.csv` | `Date`, `Store ID`, `Product ID`, `Actual Units Sold`, `Forecast Units Sold`, `Absolute Error` | Ridge Regression rolling one-step-ahead chronological holdout; 2023-09-14 to 2024-01-01; not a new future forecast |
| `python-ai/restocking/outputs/retail_restocking_recommendations_m12_02.csv` | Per-row inventory, forecast, thresholds, suggested quantity, status and reason | Historical replay using provisional defaults (3-day lead time, 1-day review period, 1 demand-day safety stock); advisory only |
| `python-ai/restocking/outputs/retail_stockout_detection_m12_03.csv` | Observed stockout, risk/watch classification and days of cover | Historical replay; risk flag is not proof of a stockout or a guarantee of future availability |

The M12-02 run recorded 11,000 `REORDER_NOW` rows and the M12-03 run recorded 11,000 `STOCKOUT_RISK` rows across the same historical test window. These are the reported outputs under the configured assumptions; the assistant must not hide or reinterpret these distributions as live operational truth.

## 6. Conversation and response rules

1. Resolve a supported intent before executing a query. Intent matching and query execution are separate responsibilities.
2. Extract slots without inventing a store ID, product ID, date or category.
3. If a required slot is missing, ask the intent's clarification question. For `DEMAND_FORECAST`, both store and product are required.
4. If an optional filter is not supplied, use a clearly labelled aggregate only when that intent supports it; otherwise ask the user to narrow the request.
5. State the date/as-of date and applied filters for data answers.
6. Distinguish observed values (`Inventory Level`, `Units Sold`, `Actual Units Sold`) from model estimates (`Forecast Units Sold`) and rule-based flags (`STOCKOUT_RISK`, `REORDER_NOW`).
7. Never claim that the chatbot can access real-time stock, supplier systems, payment systems or place orders.
8. For `UNKNOWN`, ask one concise clarification question and offer supported topic examples.
9. Use plain, direct wording suitable for small retail-shop owners; explain technical terms when needed.

## 7. Boundaries for later M13 work

- **M13-02:** implement data query functions that consume these names, slots and source contracts.
- **M13-03:** implement the assistant service that identifies intents, extracts/validates slots and prepares responses.
- **M13-04:** connect the service to the M11-06 forecasts and M12-02 inventory/reorder outputs.
- **M13-05:** integrate the chatbot UI.

No intent classifier or query implementation is included in M13-01.

## 8. Verification

Run the catalogue self-check from the repository root:

```powershell
python .\python-ai\chatbot\intents.py
```

Run unit tests:

```powershell
python -m unittest discover -s .\testing\ai -p "test_chatbot_intents.py" -v
```

Expected catalogue output: `RetailAI intent catalogue v1.0: 11 intents validated.`
