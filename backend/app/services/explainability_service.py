"""
STARTWISE AI — Explainability Service (Stage 13 XAI)
Calculates SHAP feature contributions, maps technical features to clean business concepts,
generates human-readable local & global insights, and caches explanation results.
"""

from __future__ import annotations

import logging
from typing import Dict, Any, List, Optional, Tuple
from uuid import UUID
from datetime import datetime, timezone
import numpy as np
import pandas as pd
import shap
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import User, StartupIdea, PredictionResult, PredictionExplanation
from app.repositories.explainability_repository import ExplainabilityRepository
from app.repositories.prediction_repository import PredictionRepository
from app.repositories.startup_repository import StartupRepository
from app.core.model_manager import get_model_manager
from app.core.exceptions import NotFoundException, ForbiddenException, AppException
from app.core.logging import get_logger
from ml.features.feature_engineering import add_engineered_features, get_feature_names_for_model
from app.schemas.explainability_schemas import (
    FeatureImpactItem,
    FactorItem,
    ModelTransparencyInfo,
    SingleModelExplanationResponse,
    CombinedExplanationResponse,
    PipelineStep,
)

logger = get_logger("app.services.explainability_service")

# ── Feature Metadata & Translation Map ──────────────────────────────────────
BUSINESS_FEATURE_MAP: Dict[str, Dict[str, Any]] = {
    "market_demand": {
        "display_name": "Market Demand",
        "category": "Market Viability",
        "pos_template": "Strong consumer demand ({val}/10) validates strong product-market fit.",
        "neg_template": "Subdued market demand ({val}/10) limits organic customer pull.",
    },
    "market_opportunity_score": {
        "display_name": "Market Opportunity Index",
        "category": "Market Viability",
        "pos_template": "Favorable industry expansion conditions and addressable market potential ({val:.0f}/100).",
        "neg_template": "Constrained sector growth prospects ({val:.0f}/100) cap market headroom.",
    },
    "customer_market_score": {
        "display_name": "Customer Market Fit",
        "category": "Market Viability",
        "pos_template": "Target customer segment exhibits high willingness to pay ({val:.0f}/100).",
        "neg_template": "Customer acquisition friction in target demographic ({val:.0f}/100).",
    },
    "investment_amount": {
        "display_name": "Initial Capital Outlay",
        "category": "Financial Health & Structure",
        "pos_template": "Prudent starting capital (INR {val:,.0f}) provides sufficient runway without over-leveraging.",
        "neg_template": "High initial capital requirement (INR {val:,.0f}) increases financial exposure.",
    },
    "expected_monthly_revenue": {
        "display_name": "Projected Monthly Revenue",
        "category": "Financial Health & Structure",
        "pos_template": "Robust projected monthly cash inflow (INR {val:,.0f}) supports positive cash flow.",
        "neg_template": "Modest expected monthly revenue (INR {val:,.0f}) tightens liquidity margins.",
    },
    "expected_monthly_expenses": {
        "display_name": "Operating Overhead",
        "category": "Financial Health & Structure",
        "pos_template": "Controlled operating expenses (INR {val:,.0f}) protect net margin sustainability.",
        "neg_template": "Elevated monthly operating cost (INR {val:,.0f}) creates burn rate pressure.",
    },
    "profit_estimate": {
        "display_name": "Net Operating Profit",
        "category": "Financial Health & Structure",
        "pos_template": "Healthy projected net monthly operating profit (INR {val:,.0f}).",
        "neg_template": "Slim operating margin (INR {val:,.0f}) offers limited cushion against variance.",
    },
    "profit_margin": {
        "display_name": "Operating Profit Margin",
        "category": "Financial Health & Structure",
        "pos_template": "Strong operating profit margin ({val:.1f}%) provides substantial risk resilience.",
        "neg_template": "Narrow profit margin ({val:.1f}%) increases vulnerability to operational cost spikes.",
    },
    "revenue_to_expense_ratio": {
        "display_name": "Revenue-to-Expense Multiple",
        "category": "Financial Health & Structure",
        "pos_template": "Healthy revenue-to-expense multiple ({val:.2f}x) ensures operational self-sufficiency.",
        "neg_template": "Tight revenue-to-expense coverage ({val:.2f}x) reduces financial margin of safety.",
    },
    "investment_to_revenue_ratio": {
        "display_name": "Capital Efficiency (Inv/Rev)",
        "category": "Financial Health & Structure",
        "pos_template": "Efficient capital recovery timeline ({val:.1f}x monthly revenue) optimizes ROI.",
        "neg_template": "Prolonged capital payback duration ({val:.1f}x monthly revenue) dampens rapid returns.",
    },
    "financial_health_score": {
        "display_name": "Financial Health Score",
        "category": "Financial Health & Structure",
        "pos_template": "Well-balanced cost structure and financial viability rating ({val:.0f}/100).",
        "neg_template": "Financial viability index ({val:.0f}/100) indicates sensitivity to cash burn.",
    },
    "experience_years": {
        "display_name": "Founder Industry Experience",
        "category": "Founder & Team Capability",
        "pos_template": "Extensive founder track record ({val} years) minimizes execution risk.",
        "neg_template": "Early-stage founder background ({val} years) presents an operational learning curve.",
    },
    "experience_score": {
        "display_name": "Execution Capability Rating",
        "category": "Founder & Team Capability",
        "pos_template": "High team competency and execution capability index ({val:.0f}/100).",
        "neg_template": "Execution experience rating ({val:.0f}/100) suggests value in adding seasoned advisors.",
    },
    "employee_count": {
        "display_name": "Operational Team Scale",
        "category": "Founder & Team Capability",
        "pos_template": "Optimal team size ({val} employees) balances operational agility with capacity.",
        "neg_template": "Lean staffing ({val} employees) may constrain throughput during high-demand surges.",
    },
    "business_age": {
        "display_name": "Business Maturity Stage",
        "category": "Founder & Team Capability",
        "pos_template": "Established operational history ({val} years) demonstrates business stability.",
        "neg_template": "Early founding phase ({val} years) involves typical startup validation hurdles.",
    },
    "competition_score_num": {
        "display_name": "Market Competition Intensity",
        "category": "Competitive Landscape",
        "pos_template": "Low competitive density provides immediate room for market share capture.",
        "neg_template": "High competitive saturation requires aggressive differentiation and marketing.",
    },
}

DEFAULT_PIPELINE_STEPS = [
    PipelineStep(
        step_number=1,
        title="Startup Data Ingestion",
        description="Structured business metrics (capital, location, revenue, expenses, experience) are securely normalized."
    ),
    PipelineStep(
        step_number=2,
        title="Feature Engineering & Scaling",
        description="Domain ratios (profit margins, capital multiples, opportunity indices) are derived and standardized."
    ),
    PipelineStep(
        step_number=3,
        title="ML Ensemble Inference",
        description="Offline-trained Random Forest, Decision Tree, and Regression models compute multi-target predictions."
    ),
    PipelineStep(
        step_number=4,
        title="SHAP Game-Theoretic Attribution",
        description="Shapley values calculate the exact positive or negative contribution of every individual feature."
    ),
    PipelineStep(
        step_number=5,
        title="Strategic Actionable Recommendations",
        description="Human-readable business insights and risk mitigation playbooks are generated dynamically."
    ),
]


class ExplainabilityService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ExplainabilityRepository(db)
        self.pred_repo = PredictionRepository(db)
        self.startup_repo = StartupRepository(db)
        self.manager = get_model_manager()

    def _ensure_models_loaded(self) -> None:
        """Ensure ML artifacts are in memory."""
        if not self.manager.is_loaded:
            success = self.manager.initialize()
            if not success:
                raise AppException(
                    message=f"ML Engine is offline: {self.manager.load_error}",
                    status_code=503,
                    error_code="ML_ENGINE_OFFLINE"
                )

    def _prepare_dataframe(self, startup: StartupIdea) -> pd.DataFrame:
        """Reconstruct DataFrame matching prediction feature engineering."""
        profit = float(startup.expected_monthly_revenue - (startup.expected_monthly_revenue * 0.6 if not hasattr(startup, 'expected_monthly_expenses') else getattr(startup, 'expected_monthly_expenses', startup.expected_monthly_revenue * 0.6)))
        data_dict = {
            "business_category": startup.business_category,
            "business_model": startup.business_model,
            "investment_amount": float(startup.investment_amount),
            "expected_monthly_revenue": float(startup.expected_monthly_revenue),
            "expected_monthly_expenses": float(getattr(startup, "expected_monthly_expenses", startup.expected_monthly_revenue * 0.6)),
            "employee_count": int(startup.employee_count),
            "experience_years": int(startup.experience_years),
            "location": startup.preferred_location,
            "target_customer": startup.target_customers,
            "market_demand": int(startup.market_demand),
            "competition_level": startup.competition_level,
            "funding_source": "Bootstrapped",
            "business_age": 1,
            "profit_estimate": profit,
        }
        df = pd.DataFrame([data_dict])
        df = add_engineered_features(df)
        return df

    def _prepare_for_model(self, df: pd.DataFrame, model_key: str) -> Tuple[np.ndarray, List[str]]:
        """Apply preprocessor for model and retrieve feature names."""
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

        X_trans = preprocessor.transform(X)
        try:
            feature_names = list(preprocessor.get_feature_names_out())
        except Exception:
            feature_names = [f"feature_{i}" for i in range(X_trans.shape[1])]

        return X_trans, feature_names

    def _compute_shap_contributions(
        self,
        model_name: str,
        df: pd.DataFrame,
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Calculate exact SHAP values for a specific model.
        Returns explanation_method and list of raw feature impact dicts.
        """
        model = self.manager.models[model_name]
        X_trans, feature_names = self._prepare_for_model(df, model_name)
        n_features = X_trans.shape[1]

        explanation_method = "SHAP TreeExplainer"
        shap_raw_values: np.ndarray

        try:
            if model_name == "roi":
                # Linear regression uses LinearExplainer with independent masker
                explanation_method = "SHAP LinearExplainer"
                masker = shap.maskers.Independent(data=np.zeros((1, n_features)))
                explainer = shap.LinearExplainer(model, masker=masker)
                sv = explainer.shap_values(X_trans)
                shap_raw_values = sv[0] if len(sv.shape) > 1 else sv
            else:
                # Tree-based classification models
                explanation_method = "SHAP TreeExplainer"
                explainer = shap.TreeExplainer(model)
                sv = explainer.shap_values(X_trans)

                if model_name == "success":
                    # Binary classification: extract class 1 (positive outcome)
                    if isinstance(sv, list):
                        shap_raw_values = sv[1][0]
                    elif len(sv.shape) == 3:
                        shap_raw_values = sv[0, :, 1]
                    else:
                        shap_raw_values = sv[0]
                else:
                    # Multiclass models (risk, competition): extract predicted class or risk-dominant slice
                    pred_class_idx = 0
                    if hasattr(model, "predict"):
                        try:
                            pred_val = model.predict(X_trans)[0]
                            if hasattr(model, "classes_"):
                                classes_list = list(model.classes_)
                                if pred_val in classes_list:
                                    pred_class_idx = classes_list.index(pred_val)
                        except Exception:
                            pred_class_idx = 0

                    if isinstance(sv, list):
                        shap_raw_values = sv[pred_class_idx][0]
                    elif len(sv.shape) == 3:
                        shap_raw_values = sv[0, :, pred_class_idx]
                    else:
                        shap_raw_values = sv[0]

        except Exception as e:
            logger.warning(f"SHAP explainer failed for {model_name} ({e}); using model feature importances fallback.")
            explanation_method = "Feature Importance Fallback"
            if hasattr(model, "feature_importances_"):
                imps = model.feature_importances_
                shap_raw_values = np.array(imps)
            elif hasattr(model, "coef_"):
                shap_raw_values = np.array(model.coef_)
            else:
                shap_raw_values = np.zeros(n_features)

        # Build feature impact mappings
        feature_impacts = []
        for idx in range(min(len(feature_names), len(shap_raw_values))):
            raw_name = feature_names[idx]
            val = float(shap_raw_values[idx])
            feature_impacts.append({
                "raw_name": raw_name,
                "impact": val,
            })

        return explanation_method, feature_impacts

    def _group_and_map_features(
        self,
        raw_impacts: List[Dict[str, Any]],
        df: pd.DataFrame,
    ) -> List[FeatureImpactItem]:
        """
        Map transformed/one-hot feature impacts into grouped, business-friendly items.
        """
        grouped_impacts: Dict[str, float] = {}

        for item in raw_impacts:
            raw = item["raw_name"]
            impact = item["impact"]

            clean_key = raw.replace("num__", "").replace("cat__", "")

            # Check if this is an engineered categorical feature (e.g., business_category_Food)
            matched_base = None
            for base_field in ["business_category", "business_model", "location", "target_customer", "funding_source", "investment_category"]:
                if clean_key.startswith(base_field):
                    matched_base = base_field
                    break

            target_key = matched_base if matched_base else clean_key
            grouped_impacts[target_key] = grouped_impacts.get(target_key, 0.0) + impact

        # Convert to structured FeatureImpactItems
        items: List[FeatureImpactItem] = []

        for key, impact_val in grouped_impacts.items():
            meta = BUSINESS_FEATURE_MAP.get(key, {})
            display_name = meta.get("display_name", key.replace("_", " ").title())
            category = meta.get("category", "General Evaluation")

            # Extract user input value from df if present
            user_val = None
            if key in df.columns:
                user_val = df[key].iloc[0]
                if isinstance(user_val, (np.floating, float)):
                    user_val = round(float(user_val), 2)
                elif isinstance(user_val, (np.integer, int)):
                    user_val = int(user_val)

            # Determine direction & human description
            direction = "positive" if impact_val > 0.001 else "negative" if impact_val < -0.001 else "neutral"

            if direction == "positive":
                template = meta.get("pos_template", f"Favorable configuration of {display_name} positively contributes to this score.")
            elif direction == "negative":
                template = meta.get("neg_template", f"{display_name} presents an area of resistance, reducing the calculated metric.")
            else:
                template = f"{display_name} has a neutral influence on this metric."

            try:
                if user_val is not None and "{val" in template:
                    desc = template.format(val=user_val)
                else:
                    desc = template
            except Exception:
                desc = f"{display_name} contributes {impact_val:+.2f} to the model score."

            items.append(
                FeatureImpactItem(
                    feature_name=key,
                    display_name=display_name,
                    category=category,
                    impact_value=round(float(impact_val), 4),
                    direction=direction,
                    user_value=user_val,
                    description=desc,
                )
            )

        # Sort by absolute impact descending
        items.sort(key=lambda x: abs(x.impact_value), reverse=True)
        return items

    def _generate_narrative_summary(
        self,
        model_name: str,
        predicted_val: Any,
        top_positive: List[FactorItem],
        top_negative: List[FactorItem],
        startup_name: str,
    ) -> str:
        """Create high-level dynamic local explanation text."""
        pos_names = [f.display_name for f in top_positive[:3]]
        neg_names = [f.display_name for f in top_negative[:3]]

        if model_name == "success":
            prob = f"{predicted_val:.1f}%" if isinstance(predicted_val, (int, float)) else str(predicted_val)
            if top_positive and top_negative:
                return (
                    f"{startup_name} achieved a predicted success probability of {prob}, primarily driven by "
                    f"positive contributions from {', '.join(pos_names)}. However, {', '.join(neg_names)} "
                    f"represent key areas of friction that moderate the outlook."
                )
            elif top_positive:
                return (
                    f"{startup_name} shows a strong predicted success probability of {prob}, reinforced across "
                    f"{', '.join(pos_names)}."
                )
            else:
                return f"{startup_name} received a success score of {prob} with balanced model attributions."

        elif model_name == "risk":
            return (
                f"Risk classification is rated '{predicted_val}'. "
                f"The highest risk-mitigating factors are {', '.join(pos_names) if pos_names else 'stable financial structure'}, "
                f"while primary risk drivers include {', '.join(neg_names) if neg_names else 'external market density'}."
            )

        elif model_name == "roi":
            roi_str = f"{predicted_val:.1f}%" if isinstance(predicted_val, (int, float)) else str(predicted_val)
            return (
                f"Estimated annual ROI of {roi_str} is strongly supported by {', '.join(pos_names) if pos_names else 'projected cash velocity'}, "
                f"with {', '.join(neg_names) if neg_names else 'initial setup overhead'} acting as capital recovery constraints."
            )

        elif model_name == "competition":
            return (
                f"Competition level is classified as '{predicted_val}'. "
                f"Category dynamics and {', '.join(pos_names) if pos_names else 'location characteristics'} establish baseline market density."
            )

        return f"Model {model_name} prediction influenced primarily by {', '.join(pos_names + neg_names)}."

    async def get_or_calculate_explanation(
        self,
        prediction_id: UUID,
        model_name: str,
        current_user: User,
    ) -> SingleModelExplanationResponse:
        """Retrieve cached explanation or compute fresh SHAP attribution."""
        self._ensure_models_loaded()

        # 1. Fetch prediction & check permissions (resolving by prediction_id or startup_id)
        pred = await self.pred_repo.get_by_id(prediction_id)
        if not pred:
            pred = await self.pred_repo.get_latest_by_startup_id(prediction_id)
        if not pred:
            raise NotFoundException(f"Prediction result {prediction_id} not found.")

        startup = await self.startup_repo.get_by_id(pred.startup_id)
        if not startup:
            raise NotFoundException("Associated startup idea not found.")

        if startup.user_id != current_user.id and current_user.role != "admin":
            raise ForbiddenException("Access denied. You can only view explanations for your own predictions.")

        # 2. Check for cached explanation
        cached = await self.repo.get_by_prediction_and_model(pred.id, model_name)
        if cached:
            # Reconstruct response from cached DB record
            feat_contribs = [FeatureImpactItem(**item) for item in (cached.feature_contributions or [])]
            pos_factors = [FactorItem(**item) for item in (cached.positive_factors or [])]
            neg_factors = [FactorItem(**item) for item in (cached.negative_factors or [])]

            pred_val, proba, target_metric = self._get_metric_values(model_name, pred)
            algo_map = {
                "success": "Random Forest Classifier",
                "risk": "Decision Tree Classifier",
                "roi": "Linear Regression Model",
                "competition": "Random Forest Classifier",
            }

            return SingleModelExplanationResponse(
                prediction_id=prediction_id,
                model_name=model_name,
                target_metric=target_metric,
                predicted_value=pred_val,
                probability=proba,
                model_info=ModelTransparencyInfo(
                    model_name=f"{model_name.title()} Model",
                    algorithm=algo_map.get(model_name, "Machine Learning Model"),
                    model_version=cached.model_version,
                    explanation_method=cached.explanation_method,
                    features_used=len(feat_contribs),
                    prediction_date=pred.created_at.isoformat() if hasattr(pred, 'created_at') and pred.created_at else None,
                ),
                top_positive_factors=pos_factors,
                top_negative_factors=neg_factors,
                feature_contributions=feat_contribs,
                summary=cached.summary.get("text", "") if isinstance(cached.summary, dict) else str(cached.summary or ""),
            )

        # 3. Compute SHAP Attribution
        df = self._prepare_dataframe(startup)
        method, raw_impacts = self._compute_shap_contributions(model_name, df)
        impact_items = self._group_and_map_features(raw_impacts, df)

        # Extract top factors
        pos_items = [item for item in impact_items if item.direction == "positive"]
        neg_items = [item for item in impact_items if item.direction == "negative"]

        pos_factors = [
            FactorItem(
                feature=item.feature_name,
                display_name=item.display_name,
                impact=item.impact_value,
                direction="positive",
                description=item.description,
                user_value=item.user_value,
            ) for item in pos_items[:5]
        ]

        neg_factors = [
            FactorItem(
                feature=item.feature_name,
                display_name=item.display_name,
                impact=item.impact_value,
                direction="negative",
                description=item.description,
                user_value=item.user_value,
            ) for item in neg_items[:5]
        ]

        pred_val, proba, target_metric = self._get_metric_values(model_name, pred)
        summary_text = self._generate_narrative_summary(
            model_name=model_name,
            predicted_val=pred_val,
            top_positive=pos_factors,
            top_negative=neg_factors,
            startup_name=startup.business_name,
        )

        algo_map = {
            "success": "Random Forest Classifier",
            "risk": "Decision Tree Classifier",
            "roi": "Linear Regression Model",
            "competition": "Random Forest Classifier",
        }

        # 4. Save to Cache DB
        await self.repo.save_explanation(
            prediction_id=prediction_id,
            model_name=model_name,
            explanation_method=method,
            feature_contributions=[item.model_dump() for item in impact_items],
            positive_factors=[item.model_dump() for item in pos_factors],
            negative_factors=[item.model_dump() for item in neg_factors],
            summary={"text": summary_text},
            model_version="1.0.0",
            explanation_version="1.0.0",
        )
        await self.db.commit()

        return SingleModelExplanationResponse(
            prediction_id=prediction_id,
            model_name=model_name,
            target_metric=target_metric,
            predicted_value=pred_val,
            probability=proba,
            model_info=ModelTransparencyInfo(
                model_name=f"{model_name.title()} Model",
                algorithm=algo_map.get(model_name, "Machine Learning Model"),
                model_version="1.0.0",
                explanation_method=method,
                features_used=len(impact_items),
                prediction_date=pred.created_at.isoformat() if hasattr(pred, 'created_at') and pred.created_at else None,
            ),
            top_positive_factors=pos_factors,
            top_negative_factors=neg_factors,
            feature_contributions=impact_items,
            summary=summary_text,
        )

    def _get_metric_values(self, model_name: str, pred: PredictionResult) -> Tuple[Any, Optional[float], str]:
        """Extract prediction target, probability, and label for model."""
        if model_name == "success":
            return pred.success_probability >= 50.0, pred.success_probability, "Success Probability (%)"
        elif model_name == "risk":
            return pred.risk_level, pred.business_score, "Risk Level"
        elif model_name == "roi":
            return pred.estimated_roi, None, "Estimated Annual ROI (%)"
        elif model_name == "competition":
            comp_level = "Medium"
            if isinstance(pred.ai_recommendation, dict):
                comp_level = pred.ai_recommendation.get("competition_level", "Medium")
            return comp_level, pred.competition_score, "Market Competition Density"
        return "N/A", None, "Metric"

    async def get_combined_explanation(
        self,
        prediction_id: UUID,
        current_user: User,
    ) -> CombinedExplanationResponse:
        """Fetch all 4 model explanations and build aggregated decision insight."""
        pred = await self.pred_repo.get_by_id(prediction_id)
        if not pred:
            pred = await self.pred_repo.get_latest_by_startup_id(prediction_id)
        if not pred:
            raise NotFoundException(f"Prediction result {prediction_id} not found.")

        startup = await self.startup_repo.get_by_id(pred.startup_id)
        if not startup:
            raise NotFoundException("Associated startup idea not found.")

        if startup.user_id != current_user.id and current_user.role != "admin":
            raise ForbiddenException("Access denied. You can only view explanations for your own predictions.")

        # Compute individual model explanations using resolved pred.id
        success_exp = await self.get_or_calculate_explanation(pred.id, "success", current_user)
        risk_exp = await self.get_or_calculate_explanation(pred.id, "risk", current_user)
        roi_exp = await self.get_or_calculate_explanation(pred.id, "roi", current_user)
        comp_exp = await self.get_or_calculate_explanation(pred.id, "competition", current_user)

        # Aggregate unique top positive & negative drivers across models
        all_pos: List[FactorItem] = []
        all_neg: List[FactorItem] = []
        seen_pos = set()
        seen_neg = set()

        for exp in [success_exp, risk_exp, roi_exp]:
            for f in exp.top_positive_factors:
                if f.feature not in seen_pos:
                    seen_pos.add(f.feature)
                    all_pos.append(f)
            for f in exp.top_negative_factors:
                if f.feature not in seen_neg:
                    seen_neg.add(f.feature)
                    all_neg.append(f)

        score_label = "Good"
        if isinstance(pred.ai_recommendation, dict):
            score_label = pred.ai_recommendation.get("score_label", "Good")

        # Dynamic overall decision summary
        pos_names = [f.display_name for f in all_pos[:3]]
        neg_names = [f.display_name for f in all_neg[:2]]
        overall_summary = (
            f"{startup.business_name} presents an overall business viability score of {pred.business_score:.1f}/100 ({score_label}). "
            f"Key pillars strengthening this prediction include {', '.join(pos_names) if pos_names else 'healthy financial metrics'}. "
            f"Strategic attention should focus on mitigating {', '.join(neg_names) if neg_names else 'market competition'} "
            f"to protect early operating cash flows and maximize long-term ROI."
        )

        return CombinedExplanationResponse(
            prediction_id=prediction_id,
            startup_id=startup.id,
            business_name=startup.business_name,
            business_score=pred.business_score,
            score_label=score_label,
            success=success_exp,
            risk=risk_exp,
            roi=roi_exp,
            competition=comp_exp,
            overall_decision_summary=overall_summary,
            top_positive_factors=all_pos[:5],
            top_negative_factors=all_neg[:5],
            pipeline_steps=DEFAULT_PIPELINE_STEPS,
        )
