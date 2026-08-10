"""
STARTWISE AI — Prediction Utility (Stage 6)

Reusable end-to-end prediction function that:
  1. Validates and normalizes input dict
  2. Runs feature engineering
  3. Applies saved preprocessors
  4. Runs all 4 ML models
  5. Calculates business score
  6. Returns structured prediction result

IMPORTANT:
  - This utility loads saved model artifacts (does NOT retrain)
  - It is NOT connected to FastAPI yet — that is Stage 7
  - Uses the same feature engineering as the training pipeline

Usage:
    from ml.utils.prediction_utils import predict

    result = predict({
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
    })

Returns:
    {
        "success_probability": 84.5,
        "success_prediction": true,
        "risk_level": "Low",
        "estimated_roi": 21.8,
        "competition_level": "Medium",
        "business_score": 82.0
    }
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, Any, Optional

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ml.ml_config import (
    BUSINESS_CATEGORIES, BUSINESS_MODELS, LOCATIONS,
    TARGET_CUSTOMERS, FUNDING_SOURCES,
    RISK_LEVELS, COMPETITION_LEVELS,
)
from ml.features.feature_engineering import add_engineered_features, get_feature_names_for_model
from ml.utils.model_loader import load_all_models, ModelNotTrainedError
from ml.utils.scoring import calculate_business_score, explain_score


# ── Input Validation ──────────────────────────────────────────────────────────

class PredictionInputError(ValueError):
    """Raised when prediction input is invalid."""
    pass


REQUIRED_FIELDS = [
    "business_category",
    "investment_amount",
    "expected_monthly_revenue",
    "expected_monthly_expenses",
    "employee_count",
    "experience_years",
    "market_demand",
]

DEFAULTS = {
    "business_model": "Other",
    "location": "Bengaluru",
    "target_customer": "General Public",
    "competition_level": "Medium",
    "funding_source": "Personal",
    "business_age": 0,
}


def validate_input(data: Dict[str, Any]) -> None:
    """
    Validate prediction input dictionary.
    Raises PredictionInputError with descriptive messages.
    """
    errors = []

    # Required field check
    for field in REQUIRED_FIELDS:
        if field not in data or data[field] is None:
            errors.append(f"Missing required field: '{field}'")

    if errors:
        raise PredictionInputError(f"Input validation failed:\n" + "\n".join(errors))

    # Numeric range checks
    if data.get("investment_amount", 0) <= 0:
        errors.append("investment_amount must be > 0")

    if data.get("expected_monthly_revenue", -1) < 0:
        errors.append("expected_monthly_revenue must be >= 0")

    if data.get("expected_monthly_expenses", -1) < 0:
        errors.append("expected_monthly_expenses must be >= 0")

    if data.get("employee_count", -1) < 0:
        errors.append("employee_count must be >= 0")

    if data.get("experience_years", -1) < 0:
        errors.append("experience_years must be >= 0")

    md = data.get("market_demand", 0)
    if not (1 <= md <= 10):
        errors.append("market_demand must be between 1 and 10")

    if errors:
        raise PredictionInputError(f"Input validation failed:\n" + "\n".join(errors))


def normalize_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize input by:
    - Applying defaults for missing optional fields
    - Type coercion
    - Handling unknown categorical values gracefully (OHE uses handle_unknown='ignore')
    """
    normalized = dict(DEFAULTS)
    normalized.update(data)

    # Type coercion
    normalized["investment_amount"] = float(normalized.get("investment_amount", 0))
    normalized["expected_monthly_revenue"] = float(normalized.get("expected_monthly_revenue", 0))
    normalized["expected_monthly_expenses"] = float(normalized.get("expected_monthly_expenses", 0))
    normalized["employee_count"] = int(normalized.get("employee_count", 1))
    normalized["experience_years"] = int(normalized.get("experience_years", 0))
    normalized["market_demand"] = int(normalized.get("market_demand", 5))
    normalized["business_age"] = int(normalized.get("business_age", 0))

    # Clamp market demand
    normalized["market_demand"] = max(1, min(10, normalized["market_demand"]))

    return normalized


def _build_input_dataframe(data: Dict[str, Any]) -> pd.DataFrame:
    """
    Convert input dict to a single-row DataFrame for prediction.
    Applies feature engineering to add derived columns.
    """
    df = pd.DataFrame([data])

    # Add profit_estimate if not present (needed for feature engineering)
    if "profit_estimate" not in df.columns:
        df["profit_estimate"] = df["expected_monthly_revenue"] - df["expected_monthly_expenses"]

    # Apply feature engineering
    df = add_engineered_features(df)

    return df


def _prepare_for_model(df: pd.DataFrame, model_key: str, preprocessor) -> np.ndarray:
    """
    Prepare a row for a specific model's preprocessor.
    Selects the correct feature columns and transforms them.
    """
    numeric_cols, categorical_cols = get_feature_names_for_model(model_key)

    # Keep only available columns
    available_numeric = [c for c in numeric_cols if c in df.columns]
    available_categorical = [c for c in categorical_cols if c in df.columns]

    # Select feature columns
    feature_cols = available_numeric + available_categorical
    X = df[feature_cols].copy()

    # Fill missing columns with defaults
    for col in available_numeric:
        if col not in X.columns:
            X[col] = 0.0
    for col in available_categorical:
        if col not in X.columns:
            X[col] = "Other"

    return preprocessor.transform(X)


# ── Main Prediction Function ──────────────────────────────────────────────────

def predict(
    input_data: Dict[str, Any],
    include_explanation: bool = False,
) -> Dict[str, Any]:
    """
    Run all 4 ML models and return structured predictions.

    Args:
        input_data: Dict with startup/business details
        include_explanation: If True, include score breakdown in result

    Returns:
        dict: {
            success_probability: float (0–100),
            success_prediction: bool,
            risk_level: str (Low/Medium/High),
            estimated_roi: float (%),
            competition_level: str (Low/Medium/High),
            business_score: float (0–100),
            [score_explanation: dict]  # if include_explanation=True
        }

    Raises:
        PredictionInputError: On invalid input
        ModelNotTrainedError: If model artifacts are missing
    """
    # Validate
    validate_input(input_data)

    # Normalize
    data = normalize_input(input_data)

    # Build input DataFrame with engineered features
    df = _build_input_dataframe(data)

    # Load models (cached after first call)
    models = load_all_models()

    # ── Model 1: Success ──────────────────────────────────────────────────────
    success_preprocessor = models["preprocessors"]["success"]
    X_success = _prepare_for_model(df, "success", success_preprocessor)
    success_model = models["success"]
    success_proba = success_model.predict_proba(X_success)[0]

    # predict_proba returns [P(Fail), P(Success)]
    success_prob = float(success_proba[1]) * 100  # convert to %
    success_pred = bool(success_proba[1] >= 0.5)

    # ── Model 2: Risk ─────────────────────────────────────────────────────────
    risk_preprocessor = models["preprocessors"]["risk"]
    X_risk = _prepare_for_model(df, "risk", risk_preprocessor)
    risk_model = models["risk"]
    risk_pred = str(risk_model.predict(X_risk)[0])

    # ── Model 3: ROI ──────────────────────────────────────────────────────────
    roi_preprocessor = models["preprocessors"]["roi"]
    X_roi = _prepare_for_model(df, "roi", roi_preprocessor)
    roi_model = models["roi"]
    roi_pred = float(roi_model.predict(X_roi)[0])

    # ── Model 4: Competition ──────────────────────────────────────────────────
    comp_preprocessor = models["preprocessors"]["competition"]
    X_comp = _prepare_for_model(df, "competition", comp_preprocessor)
    comp_model = models["competition"]
    comp_pred = str(comp_model.predict(X_comp)[0])

    # ── Business Score ────────────────────────────────────────────────────────
    profit_margin = float(df["profit_margin"].iloc[0])
    revenue_to_expense = float(df["revenue_to_expense_ratio"].iloc[0])

    business_score = calculate_business_score(
        success_probability=success_prob,
        risk_level=risk_pred,
        competition_level=comp_pred,
        profit_margin=profit_margin,
        market_demand=int(data["market_demand"]),
        experience_years=int(data["experience_years"]),
        revenue_to_expense_ratio=revenue_to_expense,
    )

    # ── Result ────────────────────────────────────────────────────────────────
    result = {
        "success_probability": round(success_prob, 2),
        "success_prediction": success_pred,
        "risk_level": risk_pred,
        "estimated_roi": round(roi_pred, 2),
        "competition_level": comp_pred,
        "business_score": business_score,
    }

    if include_explanation:
        explanation = explain_score(
            success_probability=success_prob,
            risk_level=risk_pred,
            competition_level=comp_pred,
            profit_margin=profit_margin,
            market_demand=int(data["market_demand"]),
            experience_years=int(data["experience_years"]),
            revenue_to_expense_ratio=revenue_to_expense,
        )
        result["score_explanation"] = explanation

    return result


# ── Quick test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_cases = [
        # High-success case
        {
            "name": "Tech SaaS — High potential",
            "data": {
                "business_category": "Technology",
                "business_model": "SaaS",
                "investment_amount": 1500000,
                "expected_monthly_revenue": 400000,
                "expected_monthly_expenses": 200000,
                "employee_count": 8,
                "experience_years": 6,
                "location": "Bengaluru",
                "target_customer": "Businesses",
                "market_demand": 9,
                "competition_level": "Medium",
                "funding_source": "Angel Investor",
                "business_age": 1,
            }
        },
        # Moderate case (spec example)
        {
            "name": "Food Cafe — Moderate",
            "data": {
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
        },
        # High-risk case
        {
            "name": "Manufacturing — High risk",
            "data": {
                "business_category": "Manufacturing",
                "business_model": "Factory",
                "investment_amount": 3000000,
                "expected_monthly_revenue": 200000,
                "expected_monthly_expenses": 280000,  # loss-making
                "employee_count": 15,
                "experience_years": 0,
                "location": "Rural",
                "target_customer": "Businesses",
                "market_demand": 3,
                "competition_level": "High",
                "funding_source": "Bank Loan",
                "business_age": 0,
            }
        },
    ]

    for tc in test_cases:
        print(f"\n{'='*55}")
        print(f"  {tc['name']}")
        print('='*55)
        try:
            result = predict(tc["data"], include_explanation=True)
            print(f"  Success Probability: {result['success_probability']}%")
            print(f"  Success Prediction : {result['success_prediction']}")
            print(f"  Risk Level         : {result['risk_level']}")
            print(f"  Estimated ROI      : {result['estimated_roi']}%")
            print(f"  Competition Level  : {result['competition_level']}")
            print(f"  Business Score     : {result['business_score']}/100")
        except ModelNotTrainedError as e:
            print(f"  ERROR: {e}")
        except Exception as e:
            print(f"  ERROR: {type(e).__name__}: {e}")
