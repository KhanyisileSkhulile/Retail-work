# M10-03 — Forecasting Feature Preparation

- **Source:** `dataset/raw/retail_store_inventory.csv`
- **Cleaning stage:** `python-ai/data/clean_data.py`
- **Feature engineering:** `python-ai/forecasting/feature_engineering.py`
- **Target:** `Units Sold`
- **Input rows:** 73,100
- **Usable rows:** 73,100
- **Rows dropped for invalid Date/target:** 0
- **Unique dates:** 731
- **Training rows:** 58,400
- **Testing rows:** 14,700
- **Feature count:** 53
- **Training date range:** 2022-01-01 to 2023-08-07
- **Testing date range:** 2023-08-08 to 2024-01-01
- **First test date (cutoff):** 2023-08-08

## Excluded columns

These fields are excluded from model inputs because of potential target leakage or uncertain measurement timing:

- `Demand Forecast`
- `Units Ordered`
- `Inventory Level`

## Engineered calendar features

- `day_of_week`
- `day_of_month`
- `month`
- `quarter`
- `day_of_year`
- `week_of_year`
- `is_weekend`

Categorical variables are one-hot encoded. Numeric missing values are imputed using training-period medians. Test categories not seen in training are ignored so that training and testing have identical feature columns.

## Model feature columns

- `Price`
- `Discount`
- `Competitor Pricing`
- `Holiday/Promotion`
- `day_of_week`
- `day_of_month`
- `month`
- `quarter`
- `day_of_year`
- `week_of_year`
- `is_weekend`
- `Store ID_S001`
- `Store ID_S002`
- `Store ID_S003`
- `Store ID_S004`
- `Store ID_S005`
- `Product ID_P0001`
- `Product ID_P0002`
- `Product ID_P0003`
- `Product ID_P0004`
- `Product ID_P0005`
- `Product ID_P0006`
- `Product ID_P0007`
- `Product ID_P0008`
- `Product ID_P0009`
- `Product ID_P0010`
- `Product ID_P0011`
- `Product ID_P0012`
- `Product ID_P0013`
- `Product ID_P0014`
- `Product ID_P0015`
- `Product ID_P0016`
- `Product ID_P0017`
- `Product ID_P0018`
- `Product ID_P0019`
- `Product ID_P0020`
- `Category_Clothing`
- `Category_Electronics`
- `Category_Furniture`
- `Category_Groceries`
- `Category_Toys`
- `Region_East`
- `Region_North`
- `Region_South`
- `Region_West`
- `Weather Condition_Cloudy`
- `Weather Condition_Rainy`
- `Weather Condition_Snowy`
- `Weather Condition_Sunny`
- `Seasonality_Autumn`
- `Seasonality_Spring`
- `Seasonality_Summer`
- `Seasonality_Winter`

## Generated outputs

- `dataset\processed\retail_forecasting_train.csv`
- `dataset\processed\retail_forecasting_test.csv`
- `dataset\processed\retail_forecasting_features.csv`

Generated CSV files are local processed artifacts and are not committed. This report and the scripts provide reproducible evidence.
