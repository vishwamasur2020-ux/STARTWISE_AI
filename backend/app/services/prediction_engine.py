"""
STARTWISE AI — AI Prediction Engine (Stage 7)

Performs live inference using loaded ML model artifacts via ModelManager.
No retraining occurs inside FastAPI — only preprocessing, model evaluation,
score calculation, and dynamic recommendation generation.
"""

from __future__ import annotations

import logging
from typing import Dict, Any, List
import numpy as np
import pandas as pd

from app.core.model_manager import get_model_manager
from app.core.exceptions import AppException
from app.schemas.prediction_schemas import (
    PredictionAnalysisRequest,
    PredictionAnalysisResponse,
    SuccessPredictionOutput,
    RiskPredictionOutput,
    RoiPredictionOutput,
    CompetitionPredictionOutput,
    ModelInformationOutput,
    FeatureImportanceOutput,
)

from app.core.logging import get_logger
from ml.features.feature_engineering import add_engineered_features, get_feature_names_for_model
from ml.utils.scoring import calculate_business_score, explain_score

logger = get_logger("app.services.prediction_engine")


def get_score_label(score: float) -> str:
    """Map numeric score (0-100) to qualitative label."""
    if score >= 90.0:
        return "Excellent"
    elif score >= 75.0:
        return "Good"
    elif score >= 60.0:
        return "Moderate"
    elif score >= 40.0:
        return "High Risk"
    else:
        return "Very High Risk"


def generate_recommendations(
    req: PredictionAnalysisRequest,
    success_prob: float,
    risk_level: str,
    roi: float,
    competition_level: str,
    business_score: float,
    profit_margin: float,
) -> List[str]:
    """
    Generate dynamic, contextual business recommendations based on ML inference.
    """
    recs = []

    # 1. Success & Score Insights
    if success_prob >= 75.0:
        recs.append(
            f"Your business shows strong market viability ({success_prob:.1f}% success chance). "
            f"Focus on customer acquisition and building brand equity."
        )
    elif success_prob < 50.0:
        recs.append(
            f"Calculated success probability is modest ({success_prob:.1f}%). "
            f"Consider refining your business model and validating customer willingness to pay before launching."
        )

    # 2. Risk Insights
    if risk_level == "High":
        recs.append(
            "High risk profile detected. Consider reducing initial capital expenditure "
            "and running a low-cost MVP pilot to test market response."
        )
    elif risk_level == "Low":
        recs.append(
            "Low overall risk profile. Financial structure and market conditions are favorable."
        )

    # 3. Competition Insights
    if competition_level == "High":
        recs.append(
            "Market competition is high in this category. Differentiate through specialized service, "
            "unique pricing tiers, or strong local branding."
        )
    elif competition_level == "Low":
        recs.append(
            "Low market competition detected. Capitalize on first-mover advantage in this territory."
        )

    # 4. Financial Health Insights
    if profit_margin < 0.15:
        recs.append(
            f"Operating profit margin is tight ({profit_margin * 100:.1f}%). "
            f"Review expected monthly expenses (INR {req.expected_monthly_expenses:,.0f}) to improve cash flow buffers."
        )
    elif profit_margin >= 0.35:
        recs.append(
            f"Healthy profit margin ({profit_margin * 100:.1f}%). Reinvest excess operating cash into marketing and expansion."
        )

    # 5. Experience Insights
    if req.experience_years < 2:
        recs.append(
            "Founder experience is early-stage (under 2 years). Consider partnering with experienced industry advisors or mentors."
        )

    # 6. Demand Insights
    if req.market_demand >= 8:
        recs.append(
            f"High consumer demand score ({req.market_demand}/10). Ensure your operational capacity (team of {req.employee_count}) can handle peak volume."
        )

    return recs[:4]  # Return top 4 most relevant recommendations


class PredictionEngine:

    def __init__(self):
        self.manager = get_model_manager()

    def _prepare_dataframe(self, req: PredictionAnalysisRequest) -> pd.DataFrame:
        """Convert input request into single-row DataFrame and add engineered features."""
        data_dict = {
            "business_category": req.business_category,
            "business_model": req.business_model,
            "investment_amount": float(req.investment_amount),
            "expected_monthly_revenue": float(req.expected_monthly_revenue),
            "expected_monthly_expenses": float(req.expected_monthly_expenses),
            "employee_count": int(req.employee_count),
            "experience_years": int(req.experience_years),
            "location": req.location,
            "target_customer": req.target_customer,
            "market_demand": int(req.market_demand),
            "competition_level": req.competition_level,
            "funding_source": req.funding_source,
            "business_age": int(req.business_age),
            "profit_estimate": float(req.expected_monthly_revenue - req.expected_monthly_expenses),
        }
        df = pd.DataFrame([data_dict])
        df = add_engineered_features(df)
        return df

    def _prepare_for_model(self, df: pd.DataFrame, model_key: str) -> np.ndarray:
        """Apply preprocessor for a specific model key."""
        preprocessor = self.manager.preprocessors[model_key]
        numeric_cols, categorical_cols = get_feature_names_for_model(model_key)

        available_numeric = [c for c in numeric_cols if c in df.columns]
        available_categorical = [c for c in categorical_cols if c in df.columns]

        X = df[available_numeric + available_categorical].copy()

        for col in available_numeric:
            if col not in X.columns:
                X[col] = 0.0
        for col in available_categorical:
            if col not in X.columns:
                X[col] = "Other"

        return preprocessor.transform(X)

    def analyze(self, req: PredictionAnalysisRequest) -> PredictionAnalysisResponse:
        """
        Run complete ML analysis pipeline on prediction request.
        """
        if not self.manager.is_loaded:
            success = self.manager.initialize()
            if not success:
                raise AppException(
                    message=f"ML Engine is offline: {self.manager.load_error}",
                    status_code=503,
                    error_code="ML_ENGINE_OFFLINE"
                )

        try:
            # 1. Feature Engineering
            df = self._prepare_dataframe(req)

            # 2. Model 1: Success Model
            X_success = self._prepare_for_model(df, "success")
            success_model = self.manager.models["success"]
            success_probas = success_model.predict_proba(X_success)[0]
            success_prob = float(success_probas[1]) * 100.0
            success_pred = bool(success_probas[1] >= 0.5)

            # 3. Model 2: Risk Model
            X_risk = self._prepare_for_model(df, "risk")
            risk_model = self.manager.models["risk"]
            risk_pred = str(risk_model.predict(X_risk)[0])
            if hasattr(risk_model, "predict_proba"):
                risk_probas = risk_model.predict_proba(X_risk)[0]
                risk_prob = float(np.max(risk_probas)) * 100.0
            else:
                risk_prob = 85.0

            # 4. Model 3: ROI Model
            X_roi = self._prepare_for_model(df, "roi")
            roi_model = self.manager.models["roi"]
            raw_roi = float(roi_model.predict(X_roi)[0])
            # Clamp ROI to realistic bounds (-100% to +500%)
            roi_pred = round(float(np.clip(raw_roi, -100.0, 500.0)), 2)

            # 5. Model 4: Competition Model
            X_comp = self._prepare_for_model(df, "competition")
            comp_model = self.manager.models["competition"]
            comp_pred = str(comp_model.predict(X_comp)[0])
            if hasattr(comp_model, "predict_proba"):
                comp_probas = comp_model.predict_proba(X_comp)[0]
                comp_prob = float(np.max(comp_probas)) * 100.0
            else:
                comp_prob = 75.0

            # 6. Business Score Calculation
            profit_margin = float(df["profit_margin"].iloc[0])
            revenue_to_expense = float(df["revenue_to_expense_ratio"].iloc[0])

            score = calculate_business_score(
                success_probability=success_prob,
                risk_level=risk_pred,
                competition_level=comp_pred,
                profit_margin=profit_margin,
                market_demand=req.market_demand,
                experience_years=req.experience_years,
                revenue_to_expense_ratio=revenue_to_expense,
            )
            score_label = get_score_label(score)

            # 7. Recommendations
            recommendations = generate_recommendations(
                req=req,
                success_prob=success_prob,
                risk_level=risk_pred,
                roi=roi_pred,
                competition_level=comp_pred,
                business_score=score,
                profit_margin=profit_margin,
            )

            # 8. Top Features (from Success Model feature importances)
            top_features_list = []
            if hasattr(success_model, "feature_importances_"):
                try:
                    preprocessor = self.manager.preprocessors["success"]
                    feature_names = preprocessor.get_feature_names_out()
                    imps = success_model.feature_importances_
                    top_indices = np.argsort(imps)[-5:][::-1]
                    for idx in top_indices:
                        name = str(feature_names[idx]).replace("cat__", "").replace("num__", "")
                        top_features_list.append(
                            FeatureImportanceOutput(
                                feature_name=name,
                                importance=round(float(imps[idx]), 4)
                            )
                        )
                except Exception:
                    pass

            return PredictionAnalysisResponse(
                startup_id=req.startup_id,
                business_name=req.business_name,
                success=SuccessPredictionOutput(
                    prediction=success_pred,
                    probability=round(success_prob, 2)
                ),
                risk=RiskPredictionOutput(
                    level=risk_pred,
                    probability=round(risk_prob, 2)
                ),
                roi=RoiPredictionOutput(
                    estimated_percentage=roi_pred
                ),
                competition=CompetitionPredictionOutput(
                    level=comp_pred,
                    probability=round(comp_prob, 2)
                ),
                business_score=score,
                score_label=score_label,
                recommendations=recommendations,
                model_information=ModelInformationOutput(),
                top_features=top_features_list,
            )

        except Exception as e:
            logger.error(f"Prediction inference failed: {e}", exc_info=True)
            raise AppException(
                message=f"Prediction calculation error: {str(e)}",
                status_code=500,
                error_code="PREDICTION_FAILED"
            )
