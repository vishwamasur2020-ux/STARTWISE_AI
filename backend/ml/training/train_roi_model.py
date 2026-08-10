"""
STARTWISE AI — Model 3: ROI Prediction (Stage 6)

Algorithm: LinearRegression (with Ridge comparison)
Target: roi (continuous float — estimated annual ROI percentage)

Why Linear Regression?
----------------------
Linear Regression is chosen for ROI prediction because:
  1. ROI is a continuous numeric variable — a regression problem, not classification.
  2. Linear Regression provides interpretable coefficients — each feature's
     contribution to ROI can be directly read from coefficients.
  3. Serves as a strong baseline — if non-linear models don't improve much,
     linear regression is preferred for simplicity.
  4. Academic scope requires Linear Regression to be implemented.
  5. Ridge regularization (L2) comparison helps prevent multicollinearity issues.

Evaluation Metrics (Regression):
  - MAE  (Mean Absolute Error): Average prediction error in same units (%)
  - MSE  (Mean Squared Error): Penalizes large errors more
  - RMSE (Root Mean Squared Error): Interpretable in % units
  - R²   (Coefficient of Determination): 1.0 = perfect, 0.0 = mean-only baseline

Why NOT use F1/Accuracy here?
  Those are classification metrics. ROI is continuous, so we use regression metrics.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

import numpy as np
import joblib

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from ml.ml_config import (
    ROI_MODEL_PATH, ROI_PREPROCESSOR_PATH,
    ROI_MODEL_PARAMS, TARGET_ROI
)
from ml.preprocessing.data_preprocessing import prepare_data, validate_dataset, clean_dataset
from ml.features.feature_engineering import add_engineered_features, get_feature_names_for_model
from ml.utils.dataset_generator import load_dataset


def train_roi_model(df=None) -> Dict[str, Any]:
    """
    Train the ROI Prediction model.

    Args:
        df: Optional pre-loaded DataFrame. If None, loads from disk.

    Returns:
        dict: Training metrics and model metadata.
    """
    print("\n" + "="*60)
    print("MODEL 3 — ROI Prediction")
    print("Algorithm: LinearRegression")
    print("="*60)

    if df is None:
        df = load_dataset()

    validate_dataset(df)
    df = clean_dataset(df)
    df = add_engineered_features(df)

    numeric_cols, categorical_cols = get_feature_names_for_model("roi")

    X_train, X_test, y_train, y_test, preprocessor, feature_names = prepare_data(
        df=df,
        target=TARGET_ROI,
        numeric_cols=numeric_cols,
        categorical_cols=categorical_cols,
        stratify=False,  # Stratify not applicable for regression
    )

    # ── Baseline: Ridge Regression (L2 regularization) ────────────────────────
    print("\n[Model 3] Training baseline (Ridge Regression)...")
    ridge = Ridge(alpha=1.0)
    ridge.fit(X_train, y_train)
    ridge_pred = ridge.predict(X_test)
    ridge_rmse = float(np.sqrt(mean_squared_error(y_test, ridge_pred)))
    ridge_r2 = float(r2_score(y_test, ridge_pred))
    print(f"[Model 3] Ridge RMSE: {ridge_rmse:.2f}%,  R²: {ridge_r2:.4f}")

    # ── Primary Model: Linear Regression ─────────────────────────────────────
    print("\n[Model 3] Training LinearRegression...")
    lr_model = LinearRegression(**ROI_MODEL_PARAMS)
    lr_model.fit(X_train, y_train)

    y_pred = lr_model.predict(X_test)

    # Metrics
    mae = float(mean_absolute_error(y_test, y_pred))
    mse = float(mean_squared_error(y_test, y_pred))
    rmse = float(np.sqrt(mse))
    r2 = float(r2_score(y_test, y_pred))

    print(f"\n[Model 3] Results (Linear Regression vs Ridge):")
    print(f"  MAE:   {mae:.2f}%")
    print(f"  MSE:   {mse:.2f}")
    print(f"  RMSE:  {rmse:.2f}%   (Ridge: {ridge_rmse:.2f}%)")
    print(f"  R²:    {r2:.4f}      (Ridge: {ridge_r2:.4f})")

    # Sample predictions
    sample_actual = y_test[:5].values
    sample_pred = y_pred[:5]
    print(f"\n[Model 3] Sample predictions (first 5):")
    for actual, pred in zip(sample_actual, sample_pred):
        print(f"  Actual: {actual:8.2f}%  |  Predicted: {pred:8.2f}%")

    # Feature coefficient analysis (top contributors)
    abs_coefficients = np.abs(lr_model.coef_)
    coef_pairs = sorted(zip(feature_names, lr_model.coef_), key=lambda x: abs(x[1]), reverse=True)[:10]
    print(f"\n[Model 3] Top 10 Features by Coefficient Magnitude:")
    for feat, coef in coef_pairs:
        direction = "+" if coef > 0 else "-"
        print(f"  {feat:<45} {direction}{abs(coef):.4f}")

    # ── Save artifacts ────────────────────────────────────────────────────────
    ROI_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(lr_model, ROI_MODEL_PATH)
    joblib.dump(preprocessor, ROI_PREPROCESSOR_PATH)
    print(f"\n[Model 3] Saved: {ROI_MODEL_PATH}")
    print(f"[Model 3] Saved: {ROI_PREPROCESSOR_PATH}")

    metrics = {
        "model_name": "roi_model",
        "algorithm": "LinearRegression",
        "version": "1.0.0",
        "training_date": datetime.now(timezone.utc).isoformat(),
        "dataset_version": "1.0.0",
        "feature_names": list(feature_names),
        "training_samples": int(len(X_train)),
        "test_samples": int(len(X_test)),
        "target_variable": TARGET_ROI,
        "hyperparameters": ROI_MODEL_PARAMS,
        "metrics": {
            "mae": round(mae, 4),
            "mse": round(mse, 4),
            "rmse": round(rmse, 4),
            "r2_score": round(r2, 4),
        },
        "baseline_comparison": {
            "ridge_rmse": round(ridge_rmse, 4),
            "ridge_r2": round(ridge_r2, 4),
        },
        "top_10_coefficients": [
            {"name": n, "coefficient": round(float(c), 4)}
            for n, c in coef_pairs
        ],
        "roi_stats": {
            "actual_mean": round(float(y_test.mean()), 2),
            "actual_std": round(float(y_test.std()), 2),
            "predicted_mean": round(float(y_pred.mean()), 2),
        }
    }

    return metrics


if __name__ == "__main__":
    results = train_roi_model()
    print(f"\nFinal RMSE: {results['metrics']['rmse']:.2f}%, R²: {results['metrics']['r2_score']:.4f}")
