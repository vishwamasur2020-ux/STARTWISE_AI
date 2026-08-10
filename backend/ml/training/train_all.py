"""
STARTWISE AI — Master Training Script (Stage 6)

Run this script to execute the complete ML pipeline:
  1. Generate dataset (if not already present)
  2. Validate dataset
  3. Clean dataset
  4. Engineer features
  5. Train all 4 models
  6. Evaluate all models
  7. Save artifacts
  8. Save metrics JSON
  9. Generate plots
  10. Run sample prediction
  11. Print training summary

Usage:
    cd backend
    python -m ml.training.train_all

    # Or from backend directory:
    .\\venv\\Scripts\\python.exe -m ml.training.train_all

Output artifacts:
    ml/artifacts/success_model.joblib
    ml/artifacts/risk_model.joblib
    ml/artifacts/roi_model.joblib
    ml/artifacts/competition_model.joblib
    ml/artifacts/success_preprocessor.joblib
    ml/artifacts/risk_preprocessor.joblib
    ml/artifacts/roi_preprocessor.joblib
    ml/artifacts/competition_preprocessor.joblib
    ml/artifacts/model_metrics.json
    ml/artifacts/feature_metadata.json
    ml/artifacts/plots/*.png
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ml.ml_config import (
    ARTIFACTS_DIR, MODEL_METRICS_PATH, FEATURE_METADATA_PATH,
    RANDOM_STATE, DATASET_VERSION, NUM_SAMPLES,
    ENGINEERED_NUMERIC_COLS, ENGINEERED_CATEGORICAL_COLS,
)
from ml.utils.dataset_generator import generate_dataset, save_dataset, load_dataset, RAW_DATASET_PATH
from ml.preprocessing.data_preprocessing import validate_dataset, clean_dataset
from ml.features.feature_engineering import add_engineered_features, get_feature_names_for_model

from ml.training.train_success_model import train_success_model
from ml.training.train_risk_model import train_risk_model
from ml.training.train_roi_model import train_roi_model
from ml.training.train_competition_model import train_competition_model

from ml.evaluation.evaluate_models import generate_all_plots


def print_header():
    print("\n" + "=" * 60)
    print("  STARTWISE AI — ML PIPELINE TRAINING")
    print(f"  Stage 6 | Random State: {RANDOM_STATE}")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


def print_summary(all_metrics: dict, total_time: float):
    print("\n" + "=" * 60)
    print("  STARTWISE AI MODEL TRAINING — RESULTS SUMMARY")
    print("=" * 60)

    m = all_metrics

    # Success Model
    if "success_model" in m:
        sm = m["success_model"]["metrics"]
        print(f"\n  [OK] Success Model (RandomForestClassifier)")
        print(f"     Accuracy : {sm['accuracy']:.2%}")
        print(f"     F1 Score : {sm['f1_score']:.2%}")
        print(f"     ROC-AUC  : {sm['roc_auc']:.2%}")

    # Risk Model
    if "risk_model" in m:
        rm = m["risk_model"]["metrics"]
        print(f"\n  [!!] Risk Model (DecisionTreeClassifier)")
        print(f"     Accuracy : {rm['accuracy']:.2%}")
        print(f"     F1 Score : {rm['f1_score']:.2%}")

    # ROI Model
    if "roi_model" in m:
        roim = m["roi_model"]["metrics"]
        print(f"\n  [$$] ROI Model (LinearRegression)")
        print(f"     RMSE     : {roim['rmse']:.2f}%")
        print(f"     R2       : {roim['r2_score']:.4f}")
        print(f"     MAE      : {roim['mae']:.2f}%")

    # Competition Model
    if "competition_model" in m:
        cm = m["competition_model"]["metrics"]
        print(f"\n  [**] Competition Model (RandomForestClassifier)")
        print(f"     Accuracy : {cm['accuracy']:.2%}")
        print(f"     F1 Score : {cm['f1_score']:.2%}")

    print(f"\n  ⏱  Total training time: {total_time:.1f}s")
    print("\n" + "=" * 60)
    print("  Training Completed Successfully!")
    print("=" * 60 + "\n")


def save_feature_metadata(df) -> None:
    """Save feature metadata JSON for model loading/prediction."""
    numeric_success, categorical_success = get_feature_names_for_model("success")
    numeric_risk, categorical_risk = get_feature_names_for_model("risk")
    numeric_roi, categorical_roi = get_feature_names_for_model("roi")
    numeric_comp, categorical_comp = get_feature_names_for_model("competition")

    metadata = {
        "dataset_version": DATASET_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_records": len(df),
        "random_state": RANDOM_STATE,
        "models": {
            "success_model": {
                "target": "success",
                "type": "binary_classification",
                "numeric_features": numeric_success,
                "categorical_features": categorical_success,
            },
            "risk_model": {
                "target": "risk_level",
                "type": "multiclass_classification",
                "classes": ["Low", "Medium", "High"],
                "numeric_features": numeric_risk,
                "categorical_features": categorical_risk,
            },
            "roi_model": {
                "target": "roi",
                "type": "regression",
                "numeric_features": numeric_roi,
                "categorical_features": categorical_roi,
            },
            "competition_model": {
                "target": "competition_level",
                "type": "multiclass_classification",
                "classes": ["Low", "Medium", "High"],
                "numeric_features": numeric_comp,
                "categorical_features": categorical_comp,
            },
        },
        "all_targets": ["success", "roi", "risk_level", "competition_level", "business_score"],
        "synthetic_dataset_disclaimer": (
            "This dataset is SYNTHETIC and generated for academic demonstration. "
            "It does NOT represent real-world proprietary business data. "
            "Predictions from this system should NOT be used for actual investment decisions."
        ),
    }

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(FEATURE_METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"\n[train_all] Saved feature metadata: {FEATURE_METADATA_PATH}")


def run_sample_prediction() -> None:
    """Run a sample prediction to verify the pipeline works end-to-end."""
    print("\n[train_all] Running sample prediction verification...")
    from ml.utils.prediction_utils import predict

    sample_input = {
        "business_category": "Food",
        "business_model": "Cafe",
        "investment_amount": 800000,
        "expected_monthly_revenue": 250000,
        "expected_monthly_expenses": 150000,
        "employee_count": 5,
        "experience_years": 2,
        "location": "Bengaluru",
        "target_customer": "Students",
        "market_demand": 7,
        "competition_level": "Medium",
        "funding_source": "Personal",
        "business_age": 0,
    }

    result = predict(sample_input)

    print("\n  Sample Input:")
    print(f"    Business: Food / Cafe, Bengaluru")
    print(f"    Investment: INR {sample_input['investment_amount']:,.0f}")
    print(f"    Revenue: INR {sample_input['expected_monthly_revenue']:,.0f}/mo")
    print(f"    Expenses: INR {sample_input['expected_monthly_expenses']:,.0f}/mo")
    print(f"    Experience: {sample_input['experience_years']} years")
    print(f"    Market Demand: {sample_input['market_demand']}/10")

    print("\n  Prediction Output:")
    print(f"    [OK] Success Probability : {result['success_probability']}%")
    print(f"    [OK] Success Prediction  : {result['success_prediction']}")
    print(f"    [!!] Risk Level          : {result['risk_level']}")
    print(f"    [$$] Estimated ROI       : {result['estimated_roi']}%")
    print(f"    [**] Competition Level   : {result['competition_level']}")
    print(f"    [##] Business Score      : {result['business_score']}/100")

    return result


def main():
    start_time = time.time()
    print_header()
    all_metrics = {}

    # ── Step 1: Generate Dataset ───────────────────────────────────────────────
    print("\n[train_all] Step 1: Dataset Generation")
    if not RAW_DATASET_PATH.exists():
        print("[train_all] No existing dataset found. Generating new dataset...")
        df = generate_dataset(n_samples=NUM_SAMPLES, seed=RANDOM_STATE)
        save_dataset(df)
    else:
        print(f"[train_all] Found existing dataset at {RAW_DATASET_PATH}")
        df = load_dataset()
        if len(df) < 1000:
            print("[train_all] Dataset too small. Regenerating...")
            df = generate_dataset(n_samples=NUM_SAMPLES, seed=RANDOM_STATE)
            save_dataset(df)

    # ── Step 2: Validate ───────────────────────────────────────────────────────
    print("\n[train_all] Step 2: Dataset Validation")
    validate_dataset(df)

    # ── Step 3: Clean ─────────────────────────────────────────────────────────
    print("\n[train_all] Step 3: Data Cleaning")
    df = clean_dataset(df)

    # ── Step 4: Feature Engineering ───────────────────────────────────────────
    print("\n[train_all] Step 4: Feature Engineering")
    df = add_engineered_features(df)
    print(f"[train_all] Dataset now has {df.shape[1]} columns after engineering.")

    # ── Step 5: Save Feature Metadata ─────────────────────────────────────────
    save_feature_metadata(df)

    # ── Step 6: Train All Models ───────────────────────────────────────────────
    print("\n[train_all] Step 5–8: Training All Models")
    all_metrics["success_model"] = train_success_model(df.copy())
    all_metrics["risk_model"] = train_risk_model(df.copy())
    all_metrics["roi_model"] = train_roi_model(df.copy())
    all_metrics["competition_model"] = train_competition_model(df.copy())

    # ── Step 7: Save Metrics ───────────────────────────────────────────────────
    print("\n[train_all] Step 9: Saving Model Metrics")
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(MODEL_METRICS_PATH, "w") as f:
        json.dump(all_metrics, f, indent=2, default=str)
    print(f"[train_all] Saved metrics: {MODEL_METRICS_PATH}")

    # ── Step 8: Generate Plots ────────────────────────────────────────────────
    print("\n[train_all] Step 10: Generating Evaluation Plots")
    try:
        generate_all_plots(df.copy())
    except Exception as e:
        print(f"[train_all] Warning: Plot generation error: {e}")
        print("[train_all] Continuing without plots...")

    # ── Step 9: Sample Prediction ─────────────────────────────────────────────
    print("\n[train_all] Step 11: Verification Prediction")
    try:
        run_sample_prediction()
    except Exception as e:
        print(f"[train_all] Warning: Sample prediction error: {e}")

    # ── Summary ───────────────────────────────────────────────────────────────
    total_time = time.time() - start_time
    print_summary(all_metrics, total_time)


if __name__ == "__main__":
    main()
