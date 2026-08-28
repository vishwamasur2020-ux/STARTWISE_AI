"""
STARTWISE AI — Explainable AI (XAI) Schemas (Stage 13)
Pydantic V2 request & response models for feature importance, SHAP explanations,
and human-readable prediction insights.
"""

from datetime import datetime
from typing import Optional, List, Any, Dict
from uuid import UUID
from pydantic import BaseModel, Field


class XAIBase(BaseModel):
    model_config = {"from_attributes": True}


class FeatureImpactItem(XAIBase):
    feature_name: str
    display_name: str
    category: str = "General"
    impact_value: float
    direction: str = Field(..., pattern="^(positive|negative|neutral)$")
    user_value: Optional[Any] = None
    description: str


class FactorItem(XAIBase):
    feature: str
    display_name: str
    impact: float
    direction: str = Field(..., pattern="^(positive|negative)$")
    description: str
    user_value: Optional[Any] = None


class ModelTransparencyInfo(XAIBase):
    model_name: str
    algorithm: str
    model_version: str = "1.0.0"
    explanation_method: str
    features_used: int = 0
    prediction_date: Optional[str] = None


class SingleModelExplanationResponse(XAIBase):
    prediction_id: UUID
    model_name: str
    target_metric: str
    predicted_value: Any
    probability: Optional[float] = None
    model_info: ModelTransparencyInfo
    top_positive_factors: List[FactorItem] = []
    top_negative_factors: List[FactorItem] = []
    feature_contributions: List[FeatureImpactItem] = []
    summary: str
    disclaimer: str = (
        "These explanations describe which model features influenced the prediction. "
        "They do not prove that a feature directly causes the business outcome."
    )


class PipelineStep(XAIBase):
    step_number: int
    title: str
    description: str


class CombinedExplanationResponse(XAIBase):
    prediction_id: UUID
    startup_id: UUID
    business_name: str
    business_score: float
    score_label: str
    success: SingleModelExplanationResponse
    risk: SingleModelExplanationResponse
    roi: SingleModelExplanationResponse
    competition: SingleModelExplanationResponse
    overall_decision_summary: str
    top_positive_factors: List[FactorItem] = []
    top_negative_factors: List[FactorItem] = []
    pipeline_steps: List[PipelineStep] = []
    disclaimer: str = (
        "These explanations describe which model features influenced the prediction. "
        "They do not prove that a feature directly causes the business outcome."
    )
