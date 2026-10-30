"""M13-01: Declarative intent catalogue for the RetailAI assistant.

This module defines the supported user-request types and their slot/data
contracts. It deliberately does not classify messages or execute data queries;
those responsibilities belong to the later M13-02 and M13-03 issues.
"""

from dataclasses import dataclass
from typing import Dict, Tuple


INTENT_CATALOG_VERSION = "1.0"


@dataclass(frozen=True)
class IntentDefinition:
    """A stable contract for one chatbot intent."""

    name: str
    description: str
    examples: Tuple[str, ...]
    required_slots: Tuple[str, ...]
    optional_slots: Tuple[str, ...]
    data_sources: Tuple[str, ...]
    clarification_prompt: str
    response_guidelines: Tuple[str, ...]


# Slots are extracted from user messages by the future assistant service.
# The catalogue uses canonical dataset identifiers; natural-language product
# names may only be resolved when an approved product/category mapping exists.
SLOT_DEFINITIONS = {
    "store_id": "Store identifier from the dataset, for example S001.",
    "product_id": "Product identifier from the dataset, for example P0001.",
    "category": "Product category exactly as represented in the inventory data.",
    "region": "Region exactly as represented in the inventory data.",
    "start_date": "Inclusive start date for a historical date-range query (YYYY-MM-DD).",
    "end_date": "Inclusive end date for a historical date-range query (YYYY-MM-DD).",
    "as_of_date": "Date of the inventory/recommendation record (YYYY-MM-DD).",
    "factor": "Descriptive sales factor: weather, promotion, discount or seasonality.",
    "limit": "Maximum number of ranked records requested by the user.",
}


# Data-source paths refer to committed project outputs or the approved input.
# All forecast/restocking/stockout outputs are historical evaluation/replay data,
# not a live connection to a shop's current point-of-sale or inventory system.
INTENTS: Dict[str, IntentDefinition] = {
    "GREETING": IntentDefinition(
        name="GREETING",
        description="A greeting or conversational opening that does not request a data lookup.",
        examples=("Hi RetailAI", "Hello", "Good morning"),
        required_slots=(),
        optional_slots=(),
        data_sources=(),
        clarification_prompt="",
        response_guidelines=(
            "Reply briefly and invite the user to ask about sales, inventory, forecasts or restocking.",
        ),
    ),
    "HELP": IntentDefinition(
        name="HELP",
        description="The user asks what the assistant can do or requests example questions.",
        examples=("What can you help me with?", "Show me examples of questions", "How do I use RetailAI?"),
        required_slots=(),
        optional_slots=(),
        data_sources=(),
        clarification_prompt="",
        response_guidelines=(
            "List only capabilities represented in this intent catalogue.",
            "Explain that returned forecast and restocking results are historical project outputs.",
        ),
    ),
    "INVENTORY_LEVEL": IntentDefinition(
        name="INVENTORY_LEVEL",
        description="Look up recorded on-hand inventory for a store, product, category or date.",
        examples=(
            "How much stock does P0001 have at S001?",
            "Show inventory for store S003",
            "What was the stock level for P0002 on 2023-10-01?",
        ),
        required_slots=(),
        optional_slots=("store_id", "product_id", "category", "as_of_date"),
        data_sources=("dataset/processed/retail_store_inventory_clean.csv",),
        clarification_prompt="Which store or product should I check? You can provide an ID such as S001 or P0001.",
        response_guidelines=(
            "Report the inventory record date with the quantity.",
            "Do not call a historical dataset value the shop's live or current stock.",
            "Ask for a store or product filter when an unfiltered result would be too broad.",
        ),
    ),
    "SALES_SUMMARY": IntentDefinition(
        name="SALES_SUMMARY",
        description="Summarise observed historical units sold over an optional period or entity filter.",
        examples=(
            "How many units did S001 sell?",
            "Summarise sales for P0004 last month",
            "Show sales in Gauteng region between 2023-10-01 and 2023-10-31",
        ),
        required_slots=(),
        optional_slots=("store_id", "product_id", "category", "region", "start_date", "end_date"),
        data_sources=("dataset/processed/retail_store_inventory_clean.csv",),
        clarification_prompt="Which store, product or date range should I use for the sales summary?",
        response_guidelines=(
            "Use observed Units Sold, not Forecast Units Sold.",
            "State the date range and filters used in the summary.",
            "Do not describe association as proof that a factor caused a sales change.",
        ),
    ),
    "TOP_SELLING_PRODUCTS": IntentDefinition(
        name="TOP_SELLING_PRODUCTS",
        description="Rank products or categories by observed units sold in the selected period.",
        examples=(
            "Which products sold the most?",
            "Show the top 5 products at S002",
            "What were the best-selling categories in October 2023?",
        ),
        required_slots=(),
        optional_slots=("store_id", "category", "region", "start_date", "end_date", "limit"),
        data_sources=("dataset/processed/retail_store_inventory_clean.csv",),
        clarification_prompt="Would you like the ranking for a particular store, region or date range?",
        response_guidelines=(
            "Rank by the sum of observed Units Sold within the selected filters.",
            "State the period and the number of results returned.",
        ),
    ),
    "DEMAND_FORECAST": IntentDefinition(
        name="DEMAND_FORECAST",
        description="Retrieve saved model-generated demand estimates for a store-product series and available forecast dates.",
        examples=(
            "What was the forecast for P0001 at S001?",
            "Show demand predictions for S003 and P0007",
            "Compare actual and forecast demand for P0002 at S004",
        ),
        required_slots=("store_id", "product_id"),
        optional_slots=("start_date", "end_date"),
        data_sources=("python-ai/forecasting/outputs/retail_demand_forecasts_m11_06.csv",),
        clarification_prompt="Which store ID and product ID should I look up? For example, S001 and P0001.",
        response_guidelines=(
            "Use the saved M11-06 Forecast Units Sold values and preserve their dates.",
            "M11-06 is a rolling one-step-ahead chronological holdout from 2023-09-14 to 2024-01-01.",
            "Do not present this evaluation output as a new forecast for future dates or as a live forecast.",
            "When actual values are shown, label them separately from model forecasts.",
        ),
    ),
    "REORDER_RECOMMENDATION": IntentDefinition(
        name="REORDER_RECOMMENDATION",
        description="Retrieve an advisory M12-02 reorder recommendation for a store-product pair and date.",
        examples=(
            "What should store S001 reorder for product P0001?",
            "Show the reorder recommendation for P0010 at S004",
            "Which items were marked REORDER_NOW at S002?",
        ),
        required_slots=(),
        optional_slots=("store_id", "product_id", "as_of_date", "limit"),
        data_sources=("python-ai/restocking/outputs/retail_restocking_recommendations_m12_02.csv",),
        clarification_prompt="Which store or product should I check? You can provide IDs such as S001 and P0001.",
        response_guidelines=(
            "Return the recorded recommendation status, suggested quantity and as-of date when available.",
            "Explain that lead time (3 days), review period (1 day) and safety stock (1 demand day) are provisional M12-01 assumptions.",
            "Never imply that a purchase order was created or sent.",
            "Identify M12-02 outputs as historical replay results, not live purchase advice.",
        ),
    ),
    "STOCKOUT_STATUS": IntentDefinition(
        name="STOCKOUT_STATUS",
        description="Look up observed stockout status, baseline stockout risk, watch status or days of cover.",
        examples=(
            "Did P0001 at S001 experience a stockout?",
            "Which products were flagged as stockout risk?",
            "How many days of cover did P0002 have at S003?",
        ),
        required_slots=(),
        optional_slots=("store_id", "product_id", "as_of_date", "limit"),
        data_sources=("python-ai/restocking/outputs/retail_stockout_detection_m12_03.csv",),
        clarification_prompt="Which store or product should I check for stockout status?",
        response_guidelines=(
            "Distinguish an observed STOCKOUT from a STOCKOUT_RISK prediction/threshold flag.",
            "Use the recorded M12-03 status and days_of_cover when present.",
            "Explain that a risk flag is not proof that a stockout occurred.",
            "Identify the results as historical replay, not live alerts or a guarantee of future availability.",
        ),
    ),
    "SALES_FACTOR_ANALYSIS": IntentDefinition(
        name="SALES_FACTOR_ANALYSIS",
        description="Describe historical sales differences across recorded weather, promotion, discount or seasonality values.",
        examples=(
            "How did promotions affect sales?",
            "Compare sales during different weather conditions",
            "What is the relationship between discounts and units sold?",
        ),
        required_slots=("factor",),
        optional_slots=("store_id", "product_id", "category", "region", "start_date", "end_date"),
        data_sources=("dataset/processed/retail_store_inventory_clean.csv",),
        clarification_prompt="Which factor should I compare: weather, promotion, discount or seasonality?",
        response_guidelines=(
            "Use only fields available in the approved inventory dataset.",
            "Report descriptive comparisons or associations, not causal conclusions.",
            "State the date range and filters used.",
        ),
    ),
    "DATA_AVAILABILITY": IntentDefinition(
        name="DATA_AVAILABILITY",
        description="Explain which project data is available, its fields, date coverage or limitations.",
        examples=(
            "What data can you access?",
            "How recent are the forecasts?",
            "Are these live inventory figures?",
        ),
        required_slots=(),
        optional_slots=(),
        data_sources=(
            "dataset/processed/retail_store_inventory_clean.csv",
            "python-ai/forecasting/outputs/retail_demand_forecasts_m11_06.csv",
            "python-ai/restocking/outputs/retail_restocking_recommendations_m12_02.csv",
            "python-ai/restocking/outputs/retail_stockout_detection_m12_03.csv",
        ),
        clarification_prompt="",
        response_guidelines=(
            "Explain that the supplied project files are historical dataset/model outputs.",
            "Do not claim access to a shop's live point-of-sale system, supplier system or real-time inventory.",
            "Use the metadata/report to state exact date coverage; do not guess missing coverage.",
        ),
    ),
    "UNKNOWN": IntentDefinition(
        name="UNKNOWN",
        description="The message does not confidently match a supported RetailAI intent.",
        examples=("Can you do my homework?", "Tell me something unrelated", "That makes no sense"),
        required_slots=(),
        optional_slots=(),
        data_sources=(),
        clarification_prompt="I may have misunderstood. Are you asking about sales, inventory, forecasts, reorder recommendations or stockout status?",
        response_guidelines=(
            "Do not fabricate a data answer or silently choose an unrelated intent.",
            "Ask one concise clarification question and offer supported example topics.",
        ),
    ),
}


def get_intent(name: str) -> IntentDefinition:
    """Return an intent definition by its canonical name (case-insensitive)."""
    key = str(name).strip().upper()
    try:
        return INTENTS[key]
    except KeyError as exc:
        raise KeyError(f"Unknown RetailAI intent: {name!r}") from exc


def list_intents(include_unknown: bool = True) -> Tuple[IntentDefinition, ...]:
    """Return catalogue entries in their documented, stable order."""
    definitions = tuple(INTENTS.values())
    if include_unknown:
        return definitions
    return tuple(item for item in definitions if item.name != "UNKNOWN")


def validate_catalog() -> Tuple[str, ...]:
    """Return catalogue consistency errors; an empty tuple means it is valid."""
    errors = []
    for key, definition in INTENTS.items():
        if key != definition.name:
            errors.append(f"Key {key!r} does not match definition name {definition.name!r}.")
        if not definition.description.strip():
            errors.append(f"{key} has no description.")
        if not definition.examples:
            errors.append(f"{key} has no example utterance.")
        if not definition.response_guidelines:
            errors.append(f"{key} has no response guidelines.")
        if set(definition.required_slots) & set(definition.optional_slots):
            errors.append(f"{key} repeats a slot as both required and optional.")
        unknown_slots = (set(definition.required_slots) | set(definition.optional_slots)) - set(SLOT_DEFINITIONS)
        if unknown_slots:
            errors.append(f"{key} uses undefined slots: {sorted(unknown_slots)}.")
    return tuple(errors)


if __name__ == "__main__":
    issues = validate_catalog()
    if issues:
        raise SystemExit("Intent catalogue validation failed:\n- " + "\n- ".join(issues))
    print(f"RetailAI intent catalogue v{INTENT_CATALOG_VERSION}: {len(INTENTS)} intents validated.")
