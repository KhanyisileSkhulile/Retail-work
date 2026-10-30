"""M13-03 deterministic RetailAI assistant service.

Connects the M13-01 intent catalogue to the read-only M13-02 query layer.
Uses transparent keyword routing and explicit slot extraction; no LLM or live
store integration is claimed.
"""
from __future__ import annotations

import re
from typing import Any, Dict, Optional

try:
    from . import intents, queries
except ImportError:
    import intents
    import queries

STORE_RE = re.compile(r"\bS\d{3,}\b", re.I)
PRODUCT_RE = re.compile(r"\bP\d{4,}\b", re.I)
DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
LIMIT_RE = re.compile(r"\btop\s+(\d{1,3})\b|\b(\d{1,3})\s+(?:products|items|results)\b", re.I)

INTENT_PATTERNS = (
    ("GREETING", (r"^\s*(hi|hello|hey|good morning|good afternoon|good evening)\b",)),
    ("HELP", (r"\b(help|what can you do|what can i ask|examples of questions|how do i use)\b",)),
    ("DATA_AVAILABILITY", (r"\b(data available|what data|live data|live inventory|how recent|data coverage)\b",)),
    ("DEMAND_FORECAST", (r"\b(forecast|forecasted|prediction|predicted|demand estimate)\b",)),
    ("REORDER_RECOMMENDATION", (r"\b(reorder|re-stock|restock|order quantity|should .* order)\b",)),
    ("STOCKOUT_STATUS", (r"\b(stockout|stock out|out of stock|days of cover|stockout risk)\b",)),
    ("SALES_FACTOR_ANALYSIS", (r"\b(weather|promotion|promotions|discount|seasonality|sales factor|affect sales|impact on sales)\b",)),
    ("TOP_SELLING_PRODUCTS", (r"\b(top selling|best.?selling|sold the most|most popular products|top products)\b",)),
    ("INVENTORY_LEVEL", (r"\b(inventory|stock level|how much stock|stock for|on.hand)\b",)),
    ("SALES_SUMMARY", (r"\b(sales|units sold|how many .* sold|sales summary)\b",)),
)


def classify_intent(message: str) -> str:
    """Classify a message to one supported canonical intent."""
    text = str(message or "").strip()
    if not text:
        return "UNKNOWN"
    for name, patterns in INTENT_PATTERNS:
        if any(re.search(pattern, text, re.I) for pattern in patterns):
            return name
    return "UNKNOWN"


def extract_slots(message: str) -> Dict[str, Any]:
    """Extract explicit store/product IDs, ISO dates, factor and top-N limit."""
    text = str(message or "")
    lower = text.casefold()
    slots: Dict[str, Any] = {}
    stores, products, dates = STORE_RE.findall(text), PRODUCT_RE.findall(text), DATE_RE.findall(text)
    if stores:
        slots["store_id"] = stores[0].upper()
    if products:
        slots["product_id"] = products[0].upper()
    if dates:
        if len(dates) == 1 and any(x in lower for x in (" on ", " as of ", " for date ")):
            slots["as_of_date"] = dates[0]
        else:
            slots["start_date"] = dates[0]
            if len(dates) > 1:
                slots["end_date"] = dates[1]
    match = LIMIT_RE.search(text)
    if match:
        slots["limit"] = int(next(x for x in match.groups() if x))
    for factor, words in {
        "weather": ("weather",),
        "promotion": ("promotion", "promotions", "holiday"),
        "discount": ("discount", "discounts"),
        "seasonality": ("seasonality", "seasonal"),
    }.items():
        if any(word in lower for word in words):
            slots["factor"] = factor
            break
    return slots


def _clarification(intent_name: str, slots: Dict[str, Any]) -> Optional[str]:
    if intent_name == "DEMAND_FORECAST":
        if not slots.get("store_id") or not slots.get("product_id"):
            return "Please provide both a store ID and a product ID, for example S001 and P0001."
    elif intent_name == "SALES_FACTOR_ANALYSIS" and not slots.get("factor"):
        return "Which factor should I compare: weather, promotion, discount or seasonality?"
    elif intent_name == "INVENTORY_LEVEL" and not (slots.get("store_id") or slots.get("product_id")):
        return "Which store or product should I check? For example, S001 or P0001."
    return None


def _records_text(frame, columns, max_rows=5) -> str:
    if frame.empty:
        return "No matching historical records were found."
    output = []
    for _, row in frame.head(max_rows).iterrows():
        fields = []
        for column in columns:
            if column in frame.columns:
                value = row[column]
                if hasattr(value, "strftime"):
                    value = value.strftime("%Y-%m-%d")
                fields.append(f"{column}: {value}")
        output.append("- " + "; ".join(fields))
    return "\n".join(output)


def _run_query(intent_name: str, slots: Dict[str, Any]):
    common = {k: slots[k] for k in
              ("store_id", "product_id", "category", "region", "start_date", "end_date")
              if k in slots}
    if intent_name == "INVENTORY_LEVEL":
        return queries.inventory_level(store_id=slots.get("store_id"),
            product_id=slots.get("product_id"), category=slots.get("category"),
            as_of_date=slots.get("as_of_date"))
    if intent_name == "SALES_SUMMARY":
        return queries.sales_summary(**common)
    if intent_name == "TOP_SELLING_PRODUCTS":
        return queries.top_selling_products(store_id=slots.get("store_id"),
            category=slots.get("category"), region=slots.get("region"),
            start_date=slots.get("start_date"), end_date=slots.get("end_date"),
            limit=slots.get("limit", 5))
    if intent_name == "DEMAND_FORECAST":
        return queries.demand_forecast(store_id=slots["store_id"],
            product_id=slots["product_id"], start_date=slots.get("start_date"),
            end_date=slots.get("end_date"))
    if intent_name == "REORDER_RECOMMENDATION":
        return queries.reorder_recommendations(store_id=slots.get("store_id"),
            product_id=slots.get("product_id"), as_of_date=slots.get("as_of_date"),
            limit=slots.get("limit", 20))
    if intent_name == "STOCKOUT_STATUS":
        return queries.stockout_status(store_id=slots.get("store_id"),
            product_id=slots.get("product_id"), as_of_date=slots.get("as_of_date"),
            limit=slots.get("limit", 20))
    if intent_name == "SALES_FACTOR_ANALYSIS":
        return queries.sales_factor_analysis(factor=slots["factor"], **common)
    if intent_name == "DATA_AVAILABILITY":
        return queries.data_availability()
    raise ValueError(f"No query handler is registered for {intent_name}")


def _format_response(intent_name: str, result: Any, slots: Dict[str, Any]) -> str:
    if intent_name == "GREETING":
        return ("Hello! I can help with historical sales, inventory, saved demand forecasts, "
                "reorder recommendations and stockout results. What would you like to check?")
    if intent_name == "HELP":
        return ("I can answer questions about historical inventory, observed sales, top-selling "
                "products, saved demand forecasts, reorder recommendations, stockout results, "
                "sales-factor comparisons and project data availability. These are project "
                "dataset/model outputs, not live store data.")
    if intent_name == "SALES_SUMMARY":
        return (f"Historical sales summary: {result['units_sold']} observed units sold across "
                f"{result['records']} records. Result date range: {result['date_start'] or 'N/A'} "
                f"to {result['date_end'] or 'N/A'}.")
    if intent_name == "INVENTORY_LEVEL":
        return "Historical inventory records:\n" + _records_text(
            result, ["Date", "Store ID", "Product ID", "Inventory Level"])
    if intent_name == "TOP_SELLING_PRODUCTS":
        return "Top products by observed units sold:\n" + _records_text(result, ["Product ID", "Units Sold"])
    if intent_name == "DEMAND_FORECAST":
        return ("Saved M11-06 historical holdout values (not a new future or live forecast):\n" +
                _records_text(result, ["Date", "Store ID", "Product ID", "Actual Units Sold", "Forecast Units Sold"]))
    if intent_name == "REORDER_RECOMMENDATION":
        return ("Historical M12-02 advisory results only; no purchase order was created:\n" +
                _records_text(result, ["Date", "Store ID", "Product ID", "recommendation_status", "suggested_order_quantity"]))
    if intent_name == "STOCKOUT_STATUS":
        return ("Historical M12-03 replay results. A risk flag is not proof that a stockout occurred:\n" +
                _records_text(result, ["Date", "Store ID", "Product ID", "stockout_status", "days_of_cover"]))
    if intent_name == "SALES_FACTOR_ANALYSIS":
        return ("Descriptive historical comparison only; this does not establish causation:\n" +
                _records_text(result, [queries.FACTORS[slots["factor"]], "records",
                                       "total_units_sold", "average_units_sold"]))
    if intent_name == "DATA_AVAILABILITY":
        summaries = []
        for name, info in result.items():
            if isinstance(info, dict):
                status = "available" if info.get("available") else "missing"
                suffix = f", {info.get('records', 0)} records" if info.get("available") else ""
                summaries.append(f"{name}: {status}{suffix}")
        return "Project data availability: " + "; ".join(summaries) + ". Live store data connected: no."
    return "I could not safely prepare a response for that request."


def process_message(message: str) -> Dict[str, Any]:
    """Return structured intent, extracted slots, query result and response text."""
    intent_name = classify_intent(message)
    slots = extract_slots(message)
    definition = intents.get_intent(intent_name)
    clarification = _clarification(intent_name, slots)
    if intent_name == "UNKNOWN":
        return {"intent": intent_name, "slots": slots, "needs_clarification": True,
                "data": None, "response": definition.clarification_prompt}
    if clarification:
        return {"intent": intent_name, "slots": slots, "needs_clarification": True,
                "data": None, "response": clarification}
    if intent_name in ("GREETING", "HELP"):
        return {"intent": intent_name, "slots": slots, "needs_clarification": False,
                "data": None, "response": _format_response(intent_name, None, slots)}
    try:
        data = _run_query(intent_name, slots)
        response = _format_response(intent_name, data, slots)
        return {"intent": intent_name, "slots": slots, "needs_clarification": False,
                "data": data, "response": response}
    except (queries.QueryDataError, ValueError, KeyError) as exc:
        return {"intent": intent_name, "slots": slots, "needs_clarification": True,
                "data": None, "response": f"I couldn't retrieve that information: {exc}"}


if __name__ == "__main__":
    print(process_message(input("You: "))["response"])
