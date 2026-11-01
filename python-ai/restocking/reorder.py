"""M12-02: Baseline inventory reorder calculations for RetailAI."""

from math import ceil, isfinite
from typing import Any

DEFAULT_LEAD_TIME_DAYS = 3
DEFAULT_REVIEW_PERIOD_DAYS = 1
DEFAULT_SAFETY_STOCK_DAYS = 1

STATUSES = {
    "REORDER_NOW",
    "WATCH",
    "HEALTHY",
    "DATA_REQUIRED",
    "INSUFFICIENT_HISTORY",
}


def _number(value: Any):
    """Return a finite float, or None when the input is missing/invalid."""
    if value is None:
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if isfinite(result) else None


def calculate_reorder_recommendation(
    current_stock,
    forecast_daily_demand,
    lead_time_days=DEFAULT_LEAD_TIME_DAYS,
    review_period_days=DEFAULT_REVIEW_PERIOD_DAYS,
    safety_stock_days=DEFAULT_SAFETY_STOCK_DAYS,
):
    """Calculate stock thresholds and an advisory suggested order quantity.

    Thresholds follow the assumptions documented in M12-01:
      safety stock = ceil(daily demand * safety-stock days)
      reorder point = ceil(daily demand * lead time + safety stock)
      target stock = ceil(daily demand * (lead time + review period)
                          + safety stock)

    WATCH deliberately has a zero suggested quantity; it flags stock that is
    below target but still above the reorder point. This is advisory only.
    """
    for name, value in (
        ("lead_time_days", lead_time_days),
        ("review_period_days", review_period_days),
        ("safety_stock_days", safety_stock_days),
    ):
        numeric = _number(value)
        if numeric is None or numeric < 0:
            raise ValueError(f"{name} must be a finite, non-negative number.")

    stock = _number(current_stock)
    if stock is None or stock < 0:
        return {
            "safety_stock": None,
            "reorder_point": None,
            "target_stock": None,
            "suggested_order_quantity": None,
            "recommendation_status": "DATA_REQUIRED",
            "recommendation_reason": "Current inventory is missing or invalid; review the stock record.",
        }

    demand = _number(forecast_daily_demand)
    if demand is None:
        return {
            "safety_stock": None,
            "reorder_point": None,
            "target_stock": None,
            "suggested_order_quantity": None,
            "recommendation_status": "INSUFFICIENT_HISTORY",
            "recommendation_reason": "No valid forecast or prior-demand fallback is available.",
        }

    # Demand cannot be negative. Treat a negative forecast as zero demand.
    demand = max(0.0, demand)
    lead_time = float(lead_time_days)
    review_period = float(review_period_days)
    buffer_days = float(safety_stock_days)

    safety_stock = int(ceil(demand * buffer_days))
    reorder_point = int(ceil(demand * lead_time + safety_stock))
    target_stock = int(ceil(demand * (lead_time + review_period) + safety_stock))

    if stock <= reorder_point:
        quantity = max(0, int(ceil(target_stock - stock)))
        status = "REORDER_NOW"
        reason = (
            f"Stock {stock:g} is at or below reorder point {reorder_point}; "
            f"suggest ordering {quantity} units to reach target stock {target_stock}."
        )
    elif stock < target_stock:
        quantity = 0
        status = "WATCH"
        reason = (
            f"Stock {stock:g} is above reorder point {reorder_point} "
            f"but below target stock {target_stock}; monitor inventory."
        )
    else:
        quantity = 0
        status = "HEALTHY"
        reason = f"Stock {stock:g} meets or exceeds target stock {target_stock}."

    return {
        "safety_stock": safety_stock,
        "reorder_point": reorder_point,
        "target_stock": target_stock,
        "suggested_order_quantity": quantity,
        "recommendation_status": status,
        "recommendation_reason": reason,
    }
