# M10-04 - Temporal Train/Validation/Test Splits

## Overview

- **Source:** `dataset/raw/retail_store_inventory.csv`
- **Cleaning:** `python-ai/data/clean_data.py`
- **Feature engineering:** `python-ai/forecasting/feature_engineering.py`
- **Split strategy:** chronological by date
- **Target column:** `Units Sold`
- **Total usable rows:** 73,100
- **Unique dates:** 731

## Split evidence

| Split | Rows | Actual row share | Unique dates | Start date | End date |
|---|---:|---:|---:|---|---|
| Training | 51,100 | 69.90% | 511 | 2022-01-01 | 2023-05-26 |
| Validation | 11,000 | 15.05% | 110 | 2023-05-27 | 2023-09-13 |
| Test | 11,000 | 15.05% | 110 | 2023-09-14 | 2024-01-01 |

## Validation results

- [x] Chronological ordering
- [x] Identical columns
- [x] No dates shared between splits
- [x] Split rows match combined dataset
- [x] All usable rows retained
- [x] No missing target values

### Missing target values

- Training: 0
- Validation: 0
- Test: 0

## Leakage prevention

- Dates are split chronologically; records from the same date remain in the same split.
- The existing M10-03 feature-preparation function is reused.
- Numeric imputation and category encoding are fitted using the training period and applied consistently to later periods.
- Existing excluded columns remain excluded from model inputs.

## Generated outputs

- `dataset\processed\retail_forecasting_train_m10_04.csv`
- `dataset\processed\retail_forecasting_validation_m10_04.csv`
- `dataset\processed\retail_forecasting_test_m10_04.csv`
- `dataset\processed\retail_forecasting_features_m10_04.csv`

The generated CSV files are local processed artifacts. The script and this report provide reproducible evidence.
