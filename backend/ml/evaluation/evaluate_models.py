"""
STARTWISE AI — Model Evaluation & Visualization (Stage 6)

Generates and saves plots to ml/artifacts/plots/:
  1. Confusion matrices (heatmap) — Success, Risk, Competition models
  2. ROC Curve — Success model (binary classification)
  3. Actual vs Predicted ROI scatter — ROI model
  4. Feature Importance bar charts — all tree-based models
  5. Model Comparison chart — accuracy/F1 side-by-side

All plots are saved as PNG files. No interactive display is used.
"""

from __future__ import annotations

import sys
import json
from pathlib import Path
from typing import Dict, Any

import numpy as np
import joblib

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Matplotlib backend must be set before importing pyplot
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend — no display needed
import matplotlib.pyplot as plt
import seaborn as sns

from ml.ml_config import (
    PLOTS_DIR, ARTIFACTS_DIR,
    SUCCESS_MODEL_PATH, SUCCESS_PREPROCESSOR_PATH,
    RISK_MODEL_PATH, RISK_PREPROCESSOR_PATH,
    ROI_MODEL_PATH, ROI_PREPROCESSOR_PATH,
    COMPETITION_MODEL_PATH, COMPETITION_PREPROCESSOR_PATH,
    TARGET_SUCCESS, TARGET_RISK, TARGET_ROI, TARGET_COMPETITION,
    RANDOM_STATE,
)
from ml.preprocessing.data_preprocessing import prepare_data, validate_dataset, clean_dataset
from ml.features.feature_engineering import add_engineered_features, get_feature_names_for_model
from ml.utils.dataset_generator import load_dataset


# Plot styling
sns.set_theme(style="whitegrid", palette="husl")
plt.rcParams.update({
    "font.family": "sans-serif",
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})


def _save_plot(fig: plt.Figure, filename: str) -> Path:
    """Save figure and close it."""
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    path = PLOTS_DIR / filename
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[Evaluation] Saved plot: {path}")
    return path


def plot_confusion_matrix(
    cm: np.ndarray,
    class_names: list,
    model_name: str,
    filename: str,
) -> None:
    """Plot and save a confusion matrix heatmap."""
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.heatmap(
        cm, annot=True, fmt="d", cmap="Blues",
        xticklabels=class_names, yticklabels=class_names,
        linewidths=0.5, ax=ax,
    )
    ax.set_title(f"Confusion Matrix — {model_name}", fontsize=14, fontweight="bold", pad=15)
    ax.set_ylabel("Actual", fontsize=12)
    ax.set_xlabel("Predicted", fontsize=12)
    _save_plot(fig, filename)


def plot_roc_curve(model, X_test, y_test, filename: str = "roc_curve_success.png") -> None:
    """Plot and save the ROC curve for the Success model."""
    from sklearn.metrics import roc_curve, auc

    y_proba = model.predict_proba(X_test)[:, 1]
    fpr, tpr, _ = roc_curve(y_test, y_proba)
    roc_auc = auc(fpr, tpr)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(fpr, tpr, color="#4C72B0", lw=2.5, label=f"ROC Curve (AUC = {roc_auc:.3f})")
    ax.plot([0, 1], [0, 1], color="gray", lw=1, linestyle="--", label="Random Classifier")
    ax.fill_between(fpr, tpr, alpha=0.1, color="#4C72B0")

    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel("False Positive Rate", fontsize=12)
    ax.set_ylabel("True Positive Rate", fontsize=12)
    ax.set_title("ROC Curve — Business Success Model", fontsize=14, fontweight="bold")
    ax.legend(loc="lower right", fontsize=11)
    _save_plot(fig, filename)


def plot_actual_vs_predicted_roi(y_actual, y_pred, filename: str = "roi_actual_vs_predicted.png") -> None:
    """Scatter plot of actual vs predicted ROI."""
    from sklearn.metrics import r2_score
    r2 = r2_score(y_actual, y_pred)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(y_actual, y_pred, alpha=0.4, color="#DD8452", s=15, label="Predictions")

    # Perfect prediction line
    min_val = min(y_actual.min(), y_pred.min())
    max_val = max(y_actual.max(), y_pred.max())
    ax.plot([min_val, max_val], [min_val, max_val], "b--", lw=2, label=f"Perfect (R²={r2:.3f})")

    ax.set_xlabel("Actual ROI (%)", fontsize=12)
    ax.set_ylabel("Predicted ROI (%)", fontsize=12)
    ax.set_title("Actual vs Predicted ROI — Linear Regression", fontsize=14, fontweight="bold")
    ax.legend(fontsize=11)
    _save_plot(fig, filename)


def plot_feature_importance(
    feature_names: list,
    importances: np.ndarray,
    model_name: str,
    filename: str,
    top_n: int = 15,
) -> None:
    """Horizontal bar chart of feature importances."""
    indices = np.argsort(importances)[-top_n:]
    top_names = [feature_names[i] for i in indices]
    top_imps = importances[indices]

    fig, ax = plt.subplots(figsize=(9, 6))
    bars = ax.barh(range(len(top_names)), top_imps, color=sns.color_palette("husl", len(top_names)))
    ax.set_yticks(range(len(top_names)))
    ax.set_yticklabels(top_names, fontsize=10)
    ax.set_xlabel("Feature Importance", fontsize=12)
    ax.set_title(f"Feature Importance — {model_name}", fontsize=14, fontweight="bold")
    ax.grid(axis="x", alpha=0.3)

    # Add value labels on bars
    for bar, val in zip(bars, top_imps):
        ax.text(val + 0.001, bar.get_y() + bar.get_height() / 2,
                f"{val:.4f}", va="center", fontsize=8)

    _save_plot(fig, filename)


def plot_model_comparison(all_metrics: Dict[str, Any], filename: str = "model_comparison.png") -> None:
    """Bar chart comparing models by their primary metric."""
    models = []
    values = []
    metric_labels = []
    colors = []

    palette = ["#4C72B0", "#DD8452", "#55A868", "#C44E52"]
    color_map = {
        "success_model": "#4C72B0",
        "risk_model": "#DD8452",
        "competition_model": "#55A868",
        "roi_model": "#C44E52",
    }

    for key, metrics in all_metrics.items():
        m = metrics.get("metrics", {})
        model_name = metrics.get("algorithm", key)
        if "accuracy" in m:
            models.append(f"{model_name}\n(Accuracy)")
            values.append(m["accuracy"] * 100)
            metric_labels.append(f"{m['accuracy']*100:.1f}%")
        elif "r2_score" in m:
            models.append(f"{model_name}\n(R²×100)")
            values.append(max(0, m["r2_score"] * 100))
            metric_labels.append(f"R²={m['r2_score']:.3f}")
        colors.append(color_map.get(key, "#95A5A6"))

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(models, values, color=colors, width=0.5, edgecolor="white", linewidth=1.5)

    for bar, label in zip(bars, metric_labels):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.5,
            label, ha="center", va="bottom", fontsize=11, fontweight="bold"
        )

    ax.set_ylim(0, 115)
    ax.set_ylabel("Score (%)", fontsize=12)
    ax.set_title("STARTWISE AI — Model Performance Comparison", fontsize=14, fontweight="bold")
    ax.grid(axis="y", alpha=0.3)
    _save_plot(fig, filename)


def generate_all_plots(df=None) -> None:
    """
    Load trained models and generate all evaluation plots.
    Requires all 4 models to be trained first.
    """
    print("\n[Evaluation] Generating all evaluation plots...")

    # Load data
    if df is None:
        df = load_dataset()
    validate_dataset(df)
    df = clean_dataset(df)
    df = add_engineered_features(df)

    # ── Model 1: Success Model ─────────────────────────────────────────────────
    if SUCCESS_MODEL_PATH.exists() and SUCCESS_PREPROCESSOR_PATH.exists():
        print("\n[Evaluation] Plotting: Success Model...")
        model = joblib.load(SUCCESS_MODEL_PATH)
        preprocessor = joblib.load(SUCCESS_PREPROCESSOR_PATH)

        numeric_cols, categorical_cols = get_feature_names_for_model("success")
        X_train, X_test, y_train, y_test, _, feature_names = prepare_data(
            df, TARGET_SUCCESS, numeric_cols, categorical_cols, stratify=True
        )
        y_pred = model.predict(X_test)

        from sklearn.metrics import confusion_matrix as cm_fn
        cm = cm_fn(y_test, y_pred)
        plot_confusion_matrix(cm, ["Fail", "Success"], "Business Success", "confusion_success.png")
        plot_roc_curve(model, X_test, y_test)
        plot_feature_importance(list(feature_names), model.feature_importances_, "Success Model", "feature_importance_success.png")

    # ── Model 2: Risk Model ────────────────────────────────────────────────────
    if RISK_MODEL_PATH.exists() and RISK_PREPROCESSOR_PATH.exists():
        print("\n[Evaluation] Plotting: Risk Model...")
        model = joblib.load(RISK_MODEL_PATH)
        preprocessor = joblib.load(RISK_PREPROCESSOR_PATH)

        numeric_cols, categorical_cols = get_feature_names_for_model("risk")
        X_train, X_test, y_train, y_test, _, feature_names = prepare_data(
            df, TARGET_RISK, numeric_cols, categorical_cols, stratify=True
        )
        y_pred = model.predict(X_test)

        from sklearn.metrics import confusion_matrix as cm_fn
        cm = cm_fn(y_test, y_pred, labels=["Low", "Medium", "High"])
        plot_confusion_matrix(cm, ["Low", "Medium", "High"], "Risk Classification", "confusion_risk.png")
        plot_feature_importance(list(feature_names), model.feature_importances_, "Risk Model (Decision Tree)", "feature_importance_risk.png")

    # ── Model 3: ROI Model ─────────────────────────────────────────────────────
    if ROI_MODEL_PATH.exists() and ROI_PREPROCESSOR_PATH.exists():
        print("\n[Evaluation] Plotting: ROI Model...")
        model = joblib.load(ROI_MODEL_PATH)

        numeric_cols, categorical_cols = get_feature_names_for_model("roi")
        X_train, X_test, y_train, y_test, _, feature_names = prepare_data(
            df, TARGET_ROI, numeric_cols, categorical_cols, stratify=False
        )
        y_pred = model.predict(X_test)
        plot_actual_vs_predicted_roi(y_test.values, y_pred)

    # ── Model 4: Competition Model ─────────────────────────────────────────────
    if COMPETITION_MODEL_PATH.exists() and COMPETITION_PREPROCESSOR_PATH.exists():
        print("\n[Evaluation] Plotting: Competition Model...")
        model = joblib.load(COMPETITION_MODEL_PATH)

        numeric_cols, categorical_cols = get_feature_names_for_model("competition")
        X_train, X_test, y_train, y_test, _, feature_names = prepare_data(
            df, TARGET_COMPETITION, numeric_cols, categorical_cols, stratify=True
        )
        y_pred = model.predict(X_test)

        from sklearn.metrics import confusion_matrix as cm_fn
        cm = cm_fn(y_test, y_pred, labels=["Low", "Medium", "High"])
        plot_confusion_matrix(cm, ["Low", "Medium", "High"], "Market Competition", "confusion_competition.png")
        plot_feature_importance(list(feature_names), model.feature_importances_, "Competition Model", "feature_importance_competition.png")

    # ── Model Comparison ───────────────────────────────────────────────────────
    metrics_path = ARTIFACTS_DIR / "model_metrics.json"
    if metrics_path.exists():
        with open(metrics_path) as f:
            all_metrics = json.load(f)
        plot_model_comparison(all_metrics)

    print(f"\n[Evaluation] All plots saved to: {PLOTS_DIR}")


if __name__ == "__main__":
    generate_all_plots()
