# M13-03 — RetailAI Assistant Service

## Objective
Implement a deterministic service connecting the M13-01 intent catalogue to the M13-02 read-only query layer.

## Processing flow
1. Accept a user message.
2. Classify it into a supported intent using ordered keyword rules.
3. Extract explicit store IDs, product IDs, ISO dates, supported sales factors and top-N limits.
4. Request clarification when the intent is unknown or required details are missing.
5. Call the matching M13-02 query function.
6. Return a structured result with intent, slots, clarification state, query data and response text.

## Supported intents
Greeting, help, historical inventory, observed sales, top-selling products, saved demand forecasts, reorder recommendations, stockout status, descriptive sales-factor comparisons and data availability.

## Limitations and safeguards
- Deterministic keyword classification; no LLM/API is connected.
- Slot extraction recognizes canonical IDs and explicit ISO dates only; it does not guess product names or relative dates.
- M11-06 forecasts are saved historical holdout values, not newly generated future forecasts.
- M12-02 recommendations are historical/advisory; no purchase order is created.
- M12-03 risk flags are not proof of an observed stockout.
- No live point-of-sale, supplier or inventory connection is claimed.
- Query errors are returned as safe user-facing messages.

## Verification
Run from the repository root:

```powershell
python -m unittest discover -s .\testing\ai -p "test_chatbot_assistant.py" -v
```
