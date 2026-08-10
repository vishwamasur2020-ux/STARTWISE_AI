"""
STARTWISE AI — Model 2: Risk Classification (Stage 6)

Algorithm: DecisionTreeClassifier
Target: risk_level (Low / Medium / High)

Why Decision Tree?
------------------
Decision Trees are chosen for risk classification because:
  1. Interpretability — the tree can be visualized and each branch explained
     to investors, founders, or university viva examiners.
  2. Explicit decision rules — "If profit margin < 5% AND competition is High
     AND experience < 2 years → High Risk" is human-readable.
  3. Non-parametric — no assumptions about data distribution.
  4. Handles categorical and numerical features directly (post OHE).
  5. Naturally supports multi-class classification (Low/Medium/High).

Limitation:
  - Single trees can overfit. We use max_depth and min_samples constraints.
  - For production, this could be upgraded to Gradient Boosting, but the
    academic scope requires DecisionTree.

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

import joblib
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report
)

from ml.ml_config import (
    RISK_MODEL_PATH, RISK_PREPROCESSOR_PATH,
    RISK_MODEL_PARAMS, RANDOM_STATE, TARGET_RISK
)
from ml.preprocessing.data_preprocessing import prepare_data, validate_dataset, clean_dataset
from ml.features.feature_engineering import add_engineered_features, get_feature_names_for_model
from ml.utils.dataset_generator import load_dataset


def train_risk_model(df=None) -> Dict[str, Any]:
    """
    Train the Risk Classification model.

    Args:
        df: Optional pre-loaded DataFrame. If None, loads from disk.

    Returns:
        dict: Training metrics and model metadata.
    """
    print("\n" + "="*60)
    print("MODEL 2 — Risk Classification")
    print("Algorithm: DecisionTreeClassifier")
    print("="*60)

    if df is None:
        df = load_dataset()

    validate_dataset(df)
    df = clean_dataset(df)
    df = add_engineered_features(df)

    numeric_cols, categorical_cols = get_feature_names_for_model("risk")

    # Exclude competition_level from features to avoid correlation leak
    # (competition is a separate target model)
    X_train, X_test, y_train, y_test, preprocessor, feature_names = prepare_data(
        df=df,
        target=TARGET_RISK,
        numeric_cols=numeric_cols,
        categorical_cols=categorical_cols,
        stratify=True,
    )

    # ── Baseline: Random Forest for comparison ────────────────────────────────
    print("\n[Model 2] Training baseline (RandomForest for comparison)...")
    rf_baseline = RandomForestClassifier(n_estimators=50, random_state=RANDOM_STATE, class_weight="balanced")
    rf_baseline.fit(X_train, y_train)
    rf_preds = rf_baseline.predict(X_test)
    rf_acc = accuracy_score(y_test, rf_preds)
    rf_f1 = f1_score(y_test, rf_preds, average="weighted", zero_division=0)
    print(f"[Model 2] Baseline RF Accuracy: {rf_acc:.4f}, F1: {rf_f1:.4f}")

    # ── Primary Model: Decision Tree ──────────────────────────────────────────
    print("\n[Model 2] Training DecisionTreeClassifier...")
    dt_model = DecisionTreeClassifier(**RISK_MODEL_PARAMS)
    dt_model.fit(X_train, y_train)

    y_pred = dt_model.predict(X_test)

    # Metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average="weighted", zero_division=0)
    recall = recall_score(y_test, y_pred, average="weighted", zero_division=0)
    f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)
    cm = confusion_matrix(y_test, y_pred, labels=["Low", "Medium", "High"])
    report = classification_report(y_test, y_pred, labels=["Low", "Medium", "High"], output_dict=True)

    print(f"\n[Model 2] Results (Decision Tree vs Baseline RF):")
    print(f"  Accuracy:  {accuracy:.4f}  (RF: {rf_acc:.4f})")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall:    {recall:.4f}")
    print(f"  F1 Score:  {f1:.4f}")
    print(f"\nClassification Report:\n{classification_report(y_test, y_pred, labels=['Low', 'Medium', 'High'])}")

    # Feature importances from DT
    feature_importances = {
        name: float(imp)
        for name, imp in zip(feature_names, dt_model.feature_importances_)
    }
    top_features = sorted(feature_importances.items(), key=lambda x: x[1], reverse=True)[:10]
    print(f"\n[Model 2] Top 10 Features:")
    for feat, imp in top_features:
        print(f"  {feat:<45} {imp:.4f}")

    # Tree depth info
    tree_depth = dt_model.get_depth()
    tree_leaves = dt_model.get_n_leaves()
    print(f"\n[Model 2] Tree depth: {tree_depth}, Leaves: {tree_leaves}")

    # ── Save artifacts ────────────────────────────────────────────────────────
    RISK_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(dt_model, RISK_MODEL_PATH)
    joblib.dump(preprocessor, RISK_PREPROCESSOR_PATH)
    print(f"\n[Model 2] Saved: {RISK_MODEL_PATH}")
    print(f"[Model 2] Saved: {RISK_PREPROCESSOR_PATH}")

    metrics = {
        "model_name": "risk_model",
        "algorithm": "DecisionTreeClassifier",
        "version": "1.0.0",
        "training_date": datetime.now(timezone.utc).isoformat(),
        "dataset_version": "1.0.0",
        "feature_names": list(feature_names),
        "training_samples": int(len(X_train)),
        "test_samples": int(len(X_test)),
        "target_variable": TARGET_RISK,
        "target_classes": ["Low", "Medium", "High"],
        "hyperparameters": RISK_MODEL_PARAMS,
        "metrics": {
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
        },
        "baseline_comparison": {
            "random_forest_accuracy": round(rf_acc, 4),
            "random_forest_f1": round(rf_f1, 4),
        },
        "tree_info": {
            "depth": tree_depth,
            "n_leaves": tree_leaves,
        },
        "confusion_matrix": cm.tolist(),
        "classification_report": report,
        "top_10_features": [{"name": n, "importance": round(i, 4)} for n, i in top_features],
    }

    return metrics


if __name__ == "__main__":
    results = train_risk_model()
    print(f"\nFinal Accuracy: {results['metrics']['accuracy']:.2%}")
