"""M11-03: Candidate models for retail demand forecasting."""

from sklearn.ensemble import (
    HistGradientBoostingRegressor,
    RandomForestRegressor,
)
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def get_candidate_models():
    """Return fresh instances of the candidate forecasting models."""

    return {
        "Ridge Regression": Pipeline([
            ("scaler", StandardScaler()),
            ("model", Ridge(alpha=10.0)),
        ]),

        "Random Forest": RandomForestRegressor(
            n_estimators=60,
            max_depth=18,
            min_samples_leaf=3,
            n_jobs=-1,
            random_state=42,
        ),

        "HistGradientBoosting": HistGradientBoostingRegressor(
            max_iter=100,
            learning_rate=0.08,
            max_leaf_nodes=31,
            l2_regularization=1.0,
            random_state=42,
        ),
    }