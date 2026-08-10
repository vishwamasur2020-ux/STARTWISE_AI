"""
STARTWISE AI — Model 1: Business Success Prediction (Stage 6)

Algorithm: RandomForestClassifier
Target: success (binary 0/1)
Output: success_probability (0–100%), success_prediction (True/False)

Why RandomForest?
-----------------
Random Forest is an ensemble method that builds multiple decision trees and
averages their predictions. It is chosen here because:
  1. It handles both categorical (OHE) and numerical features well.
  2. It naturally avoids overfitting via bagging (sampling rows + features).
  3. predict_proba() gives well-calibrated probability estimates.
  4. Feature importance is built-in and interpretable for viva explanations.
  5. Robust to outliers and noisy features.

Evaluation Metrics:
  - Accuracy: Overall correctness
  - Precision: Of predicted successes, how many are truly successful
  - Recall: Of actual successes, how many we correctly identified
  - F1 Score: Harmonic mean of Precision and Recall
  - ROC-AUC: Area under the ROC curve (threshold-independent metric)
  - Confusion Matrix: Visual breakdown of TP/FP/TN/FN
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

import numpy as np
import joblib

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix, classification_report
)

from ml.ml_config import (
    SUCCESS_MODEL_PATH, SUCCESS_PREPROCESSOR_PATH,
    SUCCESS_MODEL_PARAMS, RANDOM_STATE, TARGET_SUCCESS, FEATURE_METADATA_PATH
)
from ml.preprocessing.data_preprocessing import prepare_data, validate_dataset, clean_dataset
from ml.features.feature_engineering import add_engineered_features, get_feature_names_for_model
from ml.utils.dataset_generator import load_dataset


def train_success_model(df=None) -> Dict[str, Any]:
    """
    Train the Business Success Prediction model.

    Args:
        df: Optional pre-loaded DataFrame. If None, loads from disk.

    Returns:
        dict: Training metrics and model metadata.
    """
    print("\n" + "="*60)
    print("MODEL 1 — Business Success Prediction")
    print("Algorithm: RandomForestClassifier")
    print("="*60)

    # Load data
    if df is None:
        df = load_dataset()

    # Validate and clean
    validate_dataset(df)
    df = clean_dataset(df)

    # Feature engineering
    df = add_engineered_features(df)

    # Get feature names for this model
    numeric_cols, categorical_cols = get_feature_names_for_model("success")

    # Prepare data (includes train/test split + fit preprocessor on train only)
    X_train, X_test, y_train, y_test, preprocessor, feature_names = prepare_data(
        df=df,
        target=TARGET_SUCCESS,
        numeric_cols=numeric_cols,
        categorical_cols=categorical_cols,
        stratify=True,  # Stratify to maintain class balance
    )

    # ── Baseline Comparison: Logistic Regression ──────────────────────────────
    print("\n[Model 1] Training baseline (Logistic Regression)...")
    lr_baseline = LogisticRegression(random_state=RANDOM_STATE, max_iter=500, class_weight="balanced")
    lr_baseline.fit(X_train, y_train)
    lr_preds = lr_baseline.predict(X_test)
    lr_acc = accuracy_score(y_test, lr_preds)
    lr_f1 = f1_score(y_test, lr_preds, average="weighted")
    print(f"[Model 1] Baseline Accuracy: {lr_acc:.4f}, F1: {lr_f1:.4f}")

    # ── Primary Model: Random Forest ──────────────────────────────────────────
    print("\n[Model 1] Training RandomForestClassifier...")
    rf_model = RandomForestClassifier(**SUCCESS_MODEL_PARAMS)
    rf_model.fit(X_train, y_train)

    # Predictions
    y_pred = rf_model.predict(X_test)
    y_proba = rf_model.predict_proba(X_test)[:, 1]  # probability of success

    # Metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average="weighted", zero_division=0)
    recall = recall_score(y_test, y_pred, average="weighted", zero_division=0)
    f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)
    roc_auc = roc_auc_score(y_test, y_proba)
    cm = confusion_matrix(y_test, y_pred)
    report = classification_report(y_test, y_pred, target_names=["Fail", "Success"], output_dict=True)

    print(f"\n[Model 1] Results (Random Forest vs Baseline LR):")
    print(f"  Accuracy:  {accuracy:.4f}  (LR: {lr_acc:.4f})")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall:    {recall:.4f}")
    print(f"  F1 Score:  {f1:.4f}")
    print(f"  ROC-AUC:   {roc_auc:.4f}")
    print(f"\nClassification Report:\n{classification_report(y_test, y_pred, target_names=['Fail', 'Success'])}")

    # Feature importances
    feature_importances = {
        name: float(imp)
        for name, imp in zip(feature_names, rf_model.feature_importances_)
    }
    top_features = sorted(feature_importances.items(), key=lambda x: x[1], reverse=True)[:10]
    print(f"\n[Model 1] Top 10 Features:")
    for feat, imp in top_features:
        print(f"  {feat:<45} {imp:.4f}")

    # ── Save artifacts ────────────────────────────────────────────────────────
    SUCCESS_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(rf_model, SUCCESS_MODEL_PATH)
    joblib.dump(preprocessor, SUCCESS_PREPROCESSOR_PATH)
    print(f"\n[Model 1] Saved: {SUCCESS_MODEL_PATH}")
    print(f"[Model 1] Saved: {SUCCESS_PREPROCESSOR_PATH}")

    # ── Metadata ──────────────────────────────────────────────────────────────
    metrics = {
        "model_name": "success_model",
        "algorithm": "RandomForestClassifier",
        "version": "1.0.0",
        "training_date": datetime.now(timezone.utc).isoformat(),
        "dataset_version": "1.0.0",
        "feature_names": list(feature_names),
        "training_samples": int(len(X_train)),
        "test_samples": int(len(X_test)),
        "target_variable": TARGET_SUCCESS,
        "hyperparameters": SUCCESS_MODEL_PARAMS,
        "metrics": {
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(roc_auc, 4),
        },
        "baseline_comparison": {
            "logistic_regression_accuracy": round(lr_acc, 4),
            "logistic_regression_f1": round(lr_f1, 4),
        },
        "confusion_matrix": cm.tolist(),
        "classification_report": report,
        "top_10_features": [{"name": n, "importance": round(i, 4)} for n, i in top_features],
    }

    return metrics


if __name__ == "__main__":
    results = train_success_model()
    print(f"\nFinal Accuracy: {results['metrics']['accuracy']:.2%}")
