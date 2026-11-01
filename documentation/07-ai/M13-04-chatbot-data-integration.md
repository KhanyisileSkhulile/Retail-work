# M13-04 — Connect Chatbot to Forecasts and Inventory

## Objective
Connect the M13-03 assistant service to the saved RetailAI project CSV outputs using M13-02 read-only query functions.

## Integration map
| Assistant intent | Source file category |
|---|---|
| Inventory, sales, top-selling products, sales factors | Cleaned inventory dataset |
| Demand forecast | M11-06 saved forecast output |
| Reorder recommendation | M12-02 saved reorder output |
| Stockout status | M12-03 saved stockout output |

The integration checks source availability, routes supported messages through the assistant, and reports source record/date metadata. Missing files produce a clear setup message.

## Run a real-data chatbot query
From the repository root:

```powershell
python .\python-ai\chatbot\integration.py "Show sales for S001"
python .\python-ai\chatbot\integration.py "Forecast for S001 P0001"
python .\python-ai\chatbot\integration.py "Reorder for S001 P0001"
python .\python-ai\chatbot\integration.py "Stockout status for S001 P0001"
```

Prepare the cleaned inventory file first when it is absent:

```powershell
python .\python-ai\data\prepare_temporal_splits.py
```

## Verification

```powershell
python -m unittest discover -s .\testing\ai -p "test_chatbot_integration.py" -v
```

## Data and safety boundaries
- These are real project dataset/model-output files, but they are historical and offline.
- This integration does not connect to a live shop, POS terminal, supplier or live inventory feed.
- M11-06 values are saved historical holdout forecasts, not a newly generated future forecast.
- M12-02 reorder values are advisory historical replay results; no purchase order is placed.
- M12-03 risk flags do not prove a stockout occurred.
