# M11-04 — Trained Selected Forecasting Model

## Objective

Train and save the selected model following the M11-03 comparison.

## Selected model

**Ridge Regression**

The model was selected because it achieved the lowest validation MAE
in the M11-03 comparison. See
`M11-03-model-comparison-results.md` for the comparison evidence.

## Training details

| Item | Result |
|---|---|
| Source dataset | `dataset/processed/retail_store_inventory_clean.csv` |
| Target | `Units Sold` |
| Original training rows | 51,100 |
| Validation rows included in final fit | 11,000 |
| Total fitting rows | 62,100 |
| Fitting date range | 2022-01-01 to 2023-09-13 |
| Number of features | 58 |
| Scaler | StandardScaler |
| Regressor | Ridge Regression |
| Ridge alpha | 10.0 |
| Test split used for fitting | No |
| Test split used for smoke test | No |

The final model was fitted on the original training and validation
periods after model selection. The test split was excluded from fitting
and smoke testing.

## Verification

- Model saved successfully using Joblib.
- Saved model loaded back successfully.
- Reloaded model generated 10 smoke-test predictions using
  training rows only.
- All smoke-test predictions were finite.
- Reloaded-model predictions matched the original model predictions.
- Model feature count: 58.

## Generated artifacts

- Trained model: `python-ai/forecasting/artifacts/retail_demand_ridge_model.joblib`
- Metadata: `python-ai/forecasting/artifacts/retail_demand_ridge_model_metadata.json`
- Training script: `python-ai/forecasting/train_selected_model.py`

## Limitations

The smoke test verifies model serialization and prediction behavior;
it is not an independent accuracy evaluation. The test split remains
reserved for a later final evaluation.
