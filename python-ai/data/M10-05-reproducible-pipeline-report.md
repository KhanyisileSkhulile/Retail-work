# M10-05 — Reproducible Data Pipeline

## Objective

Document how to reproduce the RetailAI data preparation pipeline and verify its outputs.

## Environment

- Python: 3.11.9
- pandas: 3.0.5
- numpy: 2.4.6
- python-dateutil: 2.9.0.post0
- six: 1.17.0
- tzdata: 2026.3
- Dependency definitions: `python-ai/requirements.txt`

The listed package versions are pinned in the requirements file. The environment was checked using pip's offline dry-run mode; all five requirements were already satisfied.

## Source Dataset

- File: `dataset/raw/retail_store_inventory.csv`
- Records loaded: 73,100
- Columns: 15

The pipeline rebuilds the cleaned dataset from the raw source before preparing the forecasting splits.

## Reproduction Steps

From the repository root, activate the project's Python environment, then run:

```powershell
python -m pip install -r python-ai\requirements.txt
python python-ai\data\prepare_temporal_splits.py
```

The first command installs the pinned dependencies when necessary. The second runs cleaning, feature preparation, temporal splitting, and validation.

## Generated Data Outputs

1. `dataset/processed/retail_store_inventory_clean.csv`
2. `dataset/processed/retail_forecasting_train_m10_04.csv`
3. `dataset/processed/retail_forecasting_validation_m10_04.csv`
4. `dataset/processed/retail_forecasting_test_m10_04.csv`
5. `dataset/processed/retail_forecasting_features_m10_04.csv`

## Verification Results

The pipeline completed successfully. All six validation checks passed:

| Validation check | Result |
|---|---|
| Chronological ordering | PASS |
| Identical columns | PASS |
| No dates shared between splits | PASS |
| Split rows match combined dataset | PASS |
| All usable rows retained | PASS |
| No missing target values | PASS |

## Split Summary

| Dataset | Rows |
|---|---:|
| Training | 51,100 |
| Validation | 11,000 |
| Test | 11,000 |
| **Total** | **73,100** |

The three split counts sum to 73,100 rows. The cleaning run also reported 73,100 cleaned rows, with no exact duplicates removed, no rows missing required values, and no invalid dates.

## Evidence

- Executed `python python-ai\data\prepare_temporal_splits.py` successfully.
- Observed all six validation checks report PASS.
- Executed `python -m pip install --dry-run --no-index -r python-ai\requirements.txt`; all five pinned requirements were already satisfied.
- The pipeline printed the paths of the generated CSV files and the existing M10-04 temporal split report.

## Scope Note

This report records the local verification run. The dependency pins cover the data pipeline's core dependencies; they do not claim to lock every package used by the entire RetailAI application.
