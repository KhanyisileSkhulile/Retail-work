"""M13-02 read-only data query layer for RetailAI chatbot."""
from pathlib import Path
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCES = {
    "inventory": Path("dataset/processed/retail_store_inventory_clean.csv"),
    "forecast": Path("python-ai/forecasting/outputs/retail_demand_forecasts_m11_06.csv"),
    "reorder": Path("python-ai/restocking/outputs/retail_restocking_recommendations_m12_02.csv"),
    "stockout": Path("python-ai/restocking/outputs/retail_stockout_detection_m12_03.csv"),
}
FACTORS = {"weather": "Weather Condition", "promotion": "Holiday/Promotion",
           "discount": "Discount", "seasonality": "Seasonality"}

class QueryDataError(ValueError):
    """Missing, invalid or unsupported query data."""

def _load(name, data_dir=None):
    path = (Path(data_dir) if data_dir is not None else REPO_ROOT) / SOURCES[name]
    if not path.is_file():
        raise QueryDataError(f"Required data source is missing: {path}")
    df = pd.read_csv(path)
    required = {
        "inventory": {"Date","Store ID","Product ID","Category","Region","Inventory Level","Units Sold","Weather Condition","Holiday/Promotion","Discount","Seasonality"},
        "forecast": {"Date","Store ID","Product ID","Actual Units Sold","Forecast Units Sold"},
        "reorder": {"Date","Store ID","Product ID","recommendation_status","suggested_order_quantity"},
        "stockout": {"Date","Store ID","Product ID","stockout_status","days_of_cover"},
    }[name]
    missing = required - set(df.columns)
    if missing:
        raise QueryDataError(f"{name} source is missing columns: {', '.join(sorted(missing))}")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df

def _filter(df, store_id=None, product_id=None, category=None, region=None,
            start_date=None, end_date=None):
    for value, col in ((store_id,"Store ID"),(product_id,"Product ID"),
                       (category,"Category"),(region,"Region")):
        if value is not None:
            df = df[df[col].astype(str).str.casefold() == str(value).casefold()]
    if start_date:
        df = df[df["Date"] >= pd.to_datetime(start_date, errors="raise")]
    if end_date:
        df = df[df["Date"] <= pd.to_datetime(end_date, errors="raise")]
    if start_date and end_date and pd.to_datetime(end_date) < pd.to_datetime(start_date):
        raise QueryDataError("end_date must be on or after start_date")
    return df.copy()

def _limit(value):
    try:
        value = int(value)
    except (TypeError, ValueError):
        raise QueryDataError("limit must be an integer from 1 to 100")
    if not 1 <= value <= 100:
        raise QueryDataError("limit must be from 1 to 100")
    return value

def inventory_level(*, store_id=None, product_id=None, category=None, as_of_date=None, data_dir=None):
    return _filter(_load("inventory", data_dir), store_id, product_id, category,
                   start_date=as_of_date, end_date=as_of_date).reset_index(drop=True)

def sales_summary(*, store_id=None, product_id=None, category=None, region=None,
                  start_date=None, end_date=None, data_dir=None):
    df = _filter(_load("inventory", data_dir), store_id, product_id, category,
                 region, start_date, end_date)
    return {"records": int(len(df)),
            "units_sold": int(pd.to_numeric(df["Units Sold"], errors="coerce").fillna(0).sum()),
            "date_start": None if df.empty else str(df.Date.min().date()),
            "date_end": None if df.empty else str(df.Date.max().date())}

def top_selling_products(*, store_id=None, category=None, region=None,
                         start_date=None, end_date=None, limit=5, data_dir=None):
    df = _filter(_load("inventory", data_dir), store_id, category=category,
                 region=region, start_date=start_date, end_date=end_date)
    return (df.groupby("Product ID", as_index=False)["Units Sold"].sum()
              .sort_values(["Units Sold","Product ID"], ascending=[False,True])
              .head(_limit(limit)).reset_index(drop=True))

def demand_forecast(*, store_id, product_id, start_date=None, end_date=None, data_dir=None):
    if not store_id or not product_id:
        raise QueryDataError("store_id and product_id are required for demand forecasts")
    return _filter(_load("forecast", data_dir), store_id, product_id,
                   start_date=start_date, end_date=end_date).sort_values("Date").reset_index(drop=True)

def reorder_recommendations(*, store_id=None, product_id=None, as_of_date=None, limit=20, data_dir=None):
    return (_filter(_load("reorder", data_dir), store_id, product_id,
                    start_date=as_of_date, end_date=as_of_date)
            .sort_values("Date", ascending=False).head(_limit(limit)).reset_index(drop=True))

def stockout_status(*, store_id=None, product_id=None, as_of_date=None, limit=20, data_dir=None):
    return (_filter(_load("stockout", data_dir), store_id, product_id,
                    start_date=as_of_date, end_date=as_of_date)
            .sort_values("Date", ascending=False).head(_limit(limit)).reset_index(drop=True))

def sales_factor_analysis(*, factor, store_id=None, product_id=None, category=None,
                          region=None, start_date=None, end_date=None, data_dir=None):
    key = str(factor).strip().casefold()
    if key not in FACTORS:
        raise QueryDataError("factor must be weather, promotion, discount or seasonality")
    df = _filter(_load("inventory", data_dir), store_id, product_id, category,
                 region, start_date, end_date)
    return (df.groupby(FACTORS[key], dropna=False)["Units Sold"]
              .agg(records="count", total_units_sold="sum", average_units_sold="mean")
              .reset_index().sort_values("total_units_sold", ascending=False).reset_index(drop=True))

def data_availability(data_dir=None):
    root = Path(data_dir) if data_dir is not None else REPO_ROOT
    result = {}
    for name, relative in SOURCES.items():
        path = root / relative
        item = {"available": path.is_file(), "path": relative.as_posix()}
        if path.is_file():
            df = pd.read_csv(path)
            item["records"] = int(len(df))
            if "Date" in df.columns:
                dates = pd.to_datetime(df["Date"], errors="coerce").dropna()
                item["date_start"] = None if dates.empty else str(dates.min().date())
                item["date_end"] = None if dates.empty else str(dates.max().date())
        result[name] = item
    result["live_data_connected"] = False
    return result
