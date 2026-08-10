"""
STARTWISE AI — Prediction Schemas (Stage 7 Pydantic V2)

Request and response schemas for AI Startup Feasibility Analysis endpoints.
Enforces strict input validation and clean JSON output structure.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

from app.schemas.schemas import BaseResponse


# ─── Prediction Analysis Request ─────────────────────────────────────────────
class PredictionAnalysisRequest(BaseModel):
    startup_id: Optional[UUID] = Field(None, description="Optional UUID of existing startup idea to associate")
    business_name: str = Field(..., min_length=2, max_length=255, description="Name of the business idea")
    business_category: str = Field(..., min_length=2, max_length=100, description="Category (Food, Retail, Tech, etc.)")
    business_model: str = Field(default="Standard", min_length=2, max_length=100, description="Model (Cafe, SaaS, etc.)")
    business_description: Optional[str] = Field(None, max_length=2000, description="Brief concept description")
    investment_amount: float = Field(..., gt=0, description="Total capital investment in INR (> 0)")
    expected_monthly_revenue: float = Field(..., ge=0, description="Estimated monthly revenue in INR (>= 0)")
    expected_monthly_expenses: float = Field(..., ge=0, description="Estimated monthly expenses in INR (>= 0)")
    employee_count: int = Field(default=1, ge=0, description="Number of team members/employees (>= 0)")
    experience_years: int = Field(default=0, ge=0, le=50, description="Founder relevant experience in years (>= 0)")
    location: str = Field(..., min_length=2, max_length=255, description="Target city/location")
    target_customer: str = Field(..., min_length=2, max_length=255, description="Primary customer demographic")
    market_demand: int = Field(default=5, ge=1, le=10, description="Market demand score on scale 1 to 10")
    competition_level: str = Field(default="Medium", description="Perceived competition level (Low, Medium, High)")
    funding_source: str = Field(default="Personal", description="Funding source (Personal, Angel, Loan, VC)")
    business_age: int = Field(default=0, ge=0, le=50, description="Years operating / planning horizon")

    # Alias handling for Stage 5 frontend compatibility
    preferred_location: Optional[str] = None
    target_customers: Optional[str] = None
    experience_years_alias: Optional[int] = Field(None, alias="business_experience_years")
    monthly_revenue_alias: Optional[float] = Field(None, alias="monthly_revenue")

    @field_validator("business_name")
    @classmethod
    def validate_non_empty_name(cls, v: str) -> str:
        s = v.strip()
        if len(s) < 2:
            raise ValueError("Business name must be at least 2 characters long.")
        return s

    @field_validator("competition_level")
    @classmethod
    def validate_competition_level(cls, v: str) -> str:
        normalized = v.strip().capitalize()
        if normalized not in ("Low", "Medium", "High"):
            return "Medium"
        return normalized

    @model_validator(mode="after")
    def sync_aliases(self) -> "PredictionAnalysisRequest":
        if self.preferred_location and not self.location:
            self.location = self.preferred_location
        if self.target_customers and not self.target_customer:
            self.target_customer = self.target_customers
        if self.experience_years_alias is not None:
            self.experience_years = self.experience_years_alias
        if self.monthly_revenue_alias is not None:
            self.expected_monthly_revenue = self.monthly_revenue_alias
        return self


# ─── Structured Output Sub-Models ────────────────────────────────────────────
class SuccessPredictionOutput(BaseModel):
    prediction: bool
    probability: float = Field(..., description="Success probability percentage (0–100)")


class RiskPredictionOutput(BaseModel):
    level: str = Field(..., description="Risk level (Low, Medium, High)")
    probability: float = Field(..., description="Risk confidence percentage (0–100)")


class RoiPredictionOutput(BaseModel):
    estimated_percentage: float = Field(..., description="Estimated annual ROI percentage")


class CompetitionPredictionOutput(BaseModel):
    level: str = Field(..., description="Competition level (Low, Medium, High)")
    probability: float = Field(..., description="Competition confidence percentage (0–100)")


class ModelInformationOutput(BaseModel):
    success_model: str = "RandomForestClassifier"
    risk_model: str = "DecisionTreeClassifier"
    roi_model: str = "LinearRegression"
    competition_model: str = "RandomForestClassifier"


class FeatureImportanceOutput(BaseModel):
    feature_name: str
    importance: float


# ─── Full Prediction Analysis Response ──────────────────────────────────────
class PredictionAnalysisResponse(BaseModel):
    id: Optional[UUID] = None
    startup_id: Optional[UUID] = None
    business_name: str
    success: SuccessPredictionOutput
    risk: RiskPredictionOutput
    roi: RoiPredictionOutput
    competition: CompetitionPredictionOutput
    business_score: float = Field(..., description="Overall Business Score (0–100)")
    score_label: str = Field(..., description="Qualitative rating (Excellent, Good, Moderate, High Risk, Very High Risk)")
    recommendations: List[str] = Field(default_factory=list, description="Dynamic AI business recommendations")
    model_information: ModelInformationOutput = Field(default_factory=ModelInformationOutput)
    top_features: List[FeatureImportanceOutput] = Field(default_factory=list, description="Top feature importances")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"from_attributes": True}


# ─── ML Health Response ──────────────────────────────────────────────────────
class MlHealthResponse(BaseModel):
    status: str
    models_loaded: bool
    models: Dict[str, bool]
    preprocessors: Optional[Dict[str, bool]] = None
    error: Optional[str] = None
