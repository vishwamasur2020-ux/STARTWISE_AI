"""
STARTWISE AI — Model 4: Market Competition Classification (Stage 6)

Algorithm: RandomForestClassifier
Target: competition_level (Low / Medium / High)

Why RandomForest for Competition Prediction?
--------------------------------------------
RandomForest is again used here (instead of DecisionTree) because:
  1. Competition level depends on a combination of market factors, location,
     category, and investment — high-dimensional, non-linear interactions
     are better captured by an ensemble.
  2. Compared to DecisionTree, RandomForest is more stable and less prone
     to overfitting on this multi-class problem.
  3. predict_proba() allows calculating a competition risk score.
  4. Feature importance is useful for explaining which factors drive competition.

Note: This model intentionally does NOT use risk_level or success as input
      features because those are outputs from other models (circular leakage).

Evaluation Metrics:
  - Accuracy
  - Precision (weighted)
  - Recall (weighted)
  - F1 Score (weighted)
  - Confusion Matrix
  - Classification Report
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

import numpy as np
import joblib

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report
)

from ml.ml_config import (
    COMPETITION_MODEL_PATH, COMPETITION_PREPROCESSOR_PATH,
    COMPETITION_MODEL_PARAMS, RANDOM_STATE, TARGET_COMPETITION
)
from ml.preprocessing.data_preprocessing import prepare_data, validate_dataset, clean_dataset
from ml.features.feature_engineering import add_engineered_features, get_feature_names_for_model
from ml.utils.dataset_generator import load_dataset


def train_competition_model(df=None) -> Dict[str, Any]:
    """
    Train the Market Competition Classification model.

    Args:
        df: Optional pre-loaded DataFrame. If None, loads from disk.

    Returns:
        dict: Training metrics and model metadata.
    """
    print("\n" + "="*60)
    print("MODEL 4 — Market Competition Classification")
    print("Algorithm: RandomForestClassifier")
    print("="*60)

    if df is None:
        df = load_dataset()

    validate_dataset(df)
    df = clean_dataset(df)
    df = add_engineered_features(df)

    # Get feature names for competition model
    # competition_score_num is excluded (it's derived FROM competition_level)
    numeric_cols, categorical_cols = get_feature_names_for_model("competition")

    X_train, X_test, y_train, y_test, preprocessor, feature_names = prepare_data(
        df=df,
        target=TARGET_COMPETITION,
        numeric_cols=numeric_cols,
        categorical_cols=categorical_cols,
        stratify=True,
    )

    # ── Baseline: Decision Tree ───────────────────────────────────────────────
    print("\n[Model 4] Training baseline (DecisionTree)...")
    dt_baseline = DecisionTreeClassifier(max_depth=6, random_state=RANDOM_STATE, class_weight="balanced")
    dt_baseline.fit(X_train, y_train)
    dt_preds = dt_baseline.predict(X_test)
    dt_acc = accuracy_score(y_test, dt_preds)
    dt_f1 = f1_score(y_test, dt_preds, average="weighted", zero_division=0)
    print(f"[Model 4] Baseline DT Accuracy: {dt_acc:.4f}, F1: {dt_f1:.4f}")

    # ── Primary Model: Random Forest ──────────────────────────────────────────
    print("\n[Model 4] Training RandomForestClassifier...")
    rf_model = RandomForestClassifier(**COMPETITION_MODEL_PARAMS)
    rf_model.fit(X_train, y_train)

    y_pred = rf_model.predict(X_test)

    # Metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average="weighted", zero_division=0)
    recall = recall_score(y_test, y_pred, average="weighted", zero_division=0)
    f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)
    cm = confusion_matrix(y_test, y_pred, labels=["Low", "Medium", "High"])
    report = classification_report(y_test, y_pred, labels=["Low", "Medium", "High"], output_dict=True)

    print(f"\n[Model 4] Results (Random Forest vs Baseline DT):")
    print(f"  Accuracy:  {accuracy:.4f}  (DT: {dt_acc:.4f})")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall:    {recall:.4f}")
    print(f"  F1 Score:  {f1:.4f}")
    print(f"\nClassification Report:\n{classification_report(y_test, y_pred, labels=['Low', 'Medium', 'High'])}")

    # Feature importances
    feature_importances = {
        name: float(imp)
        for name, imp in zip(feature_names, rf_model.feature_importances_)
    }
    top_features = sorted(feature_importances.items(), key=lambda x: x[1], reverse=True)[:10]
    print(f"\n[Model 4] Top 10 Features:")
    for feat, imp in top_features:
        print(f"  {feat:<45} {imp:.4f}")

    # ── Save artifacts ────────────────────────────────────────────────────────
    COMPETITION_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(rf_model, COMPETITION_MODEL_PATH)
    joblib.dump(preprocessor, COMPETITION_PREPROCESSOR_PATH)
    print(f"\n[Model 4] Saved: {COMPETITION_MODEL_PATH}")
    print(f"[Model 4] Saved: {COMPETITION_PREPROCESSOR_PATH}")

    metrics = {
        "model_name": "competition_model",
        "algorithm": "RandomForestClassifier",
        "version": "1.0.0",
        "training_date": datetime.now(timezone.utc).isoformat(),
        "dataset_version": "1.0.0",
        "feature_names": list(feature_names),
        "training_samples": int(len(X_train)),
        "test_samples": int(len(X_test)),
        "target_variable": TARGET_COMPETITION,
        "target_classes": ["Low", "Medium", "High"],
        "hyperparameters": COMPETITION_MODEL_PARAMS,
        "metrics": {
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
        },
        "baseline_comparison": {
            "decision_tree_accuracy": round(dt_acc, 4),
            "decision_tree_f1": round(dt_f1, 4),
        },
        "confusion_matrix": cm.tolist(),
        "classification_report": report,
        "top_10_features": [{"name": n, "importance": round(i, 4)} for n, i in top_features],
    }

    return metrics


if __name__ == "__main__":
    results = train_competition_model()
    print(f"\nFinal Accuracy: {results['metrics']['accuracy']:.2%}")
