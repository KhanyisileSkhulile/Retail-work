"""M13-04 file-backed integration of RetailAI assistant and project data.

Routes user messages through M13-03 assistant to M13-02 read-only queries and
checks that the historical project source required by each intent is present.
No live point-of-sale, supplier or inventory integration is implied.
"""
from __future__ import annotations

import argparse
from typing import Any, Dict, Optional

try:
    from . import assistant, queries
except ImportError:
    import assistant
    import queries

INTENT_SOURCE = {
    "INVENTORY_LEVEL": "inventory",
    "SALES_SUMMARY": "inventory",
    "TOP_SELLING_PRODUCTS": "inventory",
    "SALES_FACTOR_ANALYSIS": "inventory",
    "DEMAND_FORECAST": "forecast",
    "REORDER_RECOMMENDATION": "reorder",
    "STOCKOUT_STATUS": "stockout",
}


def process_project_message(message: str) -> Dict[str, Any]:
    """Answer through the assistant using the repository's actual saved CSVs.

    Returns the assistant's normal response plus source metadata. If the
    required source is absent, returns a clear setup message instead of
    pretending a data lookup succeeded.
    """
    intent_name = assistant.classify_intent(message)
    if intent_name in ("UNKNOWN", "GREETING", "HELP"):
        result = assistant.process_message(message)
        result["integration"] = {"mode": "assistant_only", "live_data_connected": False}
        return result

    if intent_name == "DATA_AVAILABILITY":
        result = assistant.process_message(message)
        availability = queries.data_availability()
        result["integration"] = {
            "mode": "historical_project_files",
            "live_data_connected": False,
            "sources": availability,
        }
        return result

    source_name = INTENT_SOURCE.get(intent_name)
    if source_name is None:
        result = assistant.process_message(message)
        result["integration"] = {"mode": "historical_project_files", "live_data_connected": False}
        return result

    availability = queries.data_availability()
    source_info = availability.get(source_name, {})
    if not source_info.get("available"):
        relative_path = queries.SOURCES[source_name].as_posix()
        return {
            "intent": intent_name,
            "slots": assistant.extract_slots(message),
            "needs_clarification": True,
            "data": None,
            "response": (
                f"The {source_name} project data file is not available yet: {relative_path}. "
                "Prepare or restore the required project dataset/output, then run the query again."
            ),
            "integration": {
                "mode": "historical_project_files",
                "source": source_name,
                "source_available": False,
                "live_data_connected": False,
            },
        }

    result = assistant.process_message(message)
    result["integration"] = {
        "mode": "historical_project_files",
        "source": source_name,
        "source_available": True,
        "source_records": source_info.get("records"),
        "date_start": source_info.get("date_start"),
        "date_end": source_info.get("date_end"),
        "live_data_connected": False,
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask RetailAI using saved project data")
    parser.add_argument("message", nargs="+", help="Question for the RetailAI assistant")
    args = parser.parse_args()
    result = process_project_message(" ".join(args.message))
    print(result["response"])
    if result.get("integration"):
        info = result["integration"]
        if info.get("source"):
            print(f"\nData source: {info['source']} ({'available' if info.get('source_available') else 'missing'})")
        print("Live data connected: no")


if __name__ == "__main__":
    main()
