"""
STARTWISE AI — Franchise & Recommendation Schemas (Stage 8 Pydantic V2)

Request and response models for Franchise browsing, search, recommendations, and side-by-side comparison.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field

from app.schemas.schemas import BaseResponse


# ─── Franchise Out Schema ───────────────────────────────────────────────────
class FranchiseOut(BaseResponse):
    id: UUID
    franchise_name: str
    industry: str
    business_model: Optional[str] = "Franchise"
    minimum_investment: float
    maximum_investment: float
    roi: float
    risk_level: str
    city: Optional[str] = None
    state: Optional[str] = None
    country: str = "India"
    experience_required: int = 0
    market_demand: int = 5
    target_customer: Optional[str] = "General Public"
    website: Optional[str] = None
    contact_email: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    advantages: Optional[List[str]] = None
    disadvantages: Optional[List[str]] = None
    is_active: bool = True
    created_at: datetime

    # Aliases for frontend compatibility
    name: Optional[str] = None
    category: Optional[str] = None
    min_investment: Optional[float] = None
    max_investment: Optional[float] = None
    expected_roi: Optional[float] = None
    website_url: Optional[str] = None

    def model_post_init(self, __context: Any) -> None:
        if not self.name:
            self.name = self.franchise_name
        if not self.category:
            self.category = self.industry
        if self.min_investment is None:
            self.min_investment = self.minimum_investment
        if self.max_investment is None:
            self.max_investment = self.maximum_investment
        if self.expected_roi is None:
            self.expected_roi = self.roi
        if not self.website_url:
            self.website_url = self.website


# ─── Recommendation Request ─────────────────────────────────────────────────
class FranchiseRecommendationRequest(BaseModel):
    startup_id: Optional[UUID] = Field(None, description="UUID of existing startup idea")
    budget: float = Field(..., gt=0, description="Available capital investment budget in INR")
    business_category: str = Field(..., min_length=2, description="Target industry/category")
    location: str = Field(..., min_length=2, description="Target city or preferred location")
    experience_years: int = Field(default=0, ge=0, description="Founder relevant experience years")
    expected_roi: float = Field(default=25.0, ge=0, description="Expected annual ROI %")
    risk_preference: str = Field(default="Low", description="Risk preference (Low, Medium, High)")
    target_customer: str = Field(default="General Public", description="Target customer segment")


# ─── Single Recommendation Output ────────────────────────────────────────────
class FranchiseRecommendationItem(BaseModel):
    franchise: FranchiseOut
    match_score: float = Field(..., description="Calculated hybrid match percentage (0-100%)")
    score_label: str = Field(..., description="Qualitative rating label (Excellent Match, Strong Match, etc.)")
    ranking_position: int = Field(..., description="Rank position (1 to K)")
    recommendation_type: str = Field("PRIMARY", description="PRIMARY or ALTERNATIVE match")
    explanation: List[str] = Field(default_factory=list, description="Dynamic bullet points explaining why it matched")
    sub_scores: Dict[str, float] = Field(default_factory=dict, description="Detailed sub-score breakdown")


# ─── Full Recommendation Response ───────────────────────────────────────────
class FranchiseRecommendationResponse(BaseModel):
    startup_id: Optional[UUID] = None
    user_budget: float
    category: str
    location: str
    risk_preference: str
    total_recommendations: int
    recommendations: List[FranchiseRecommendationItem]
    disclaimer: str = Field(default="DEMO / SYNTHETIC DATA: Financial figures are indicative estimates for academic demonstration.")
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ─── Side-by-Side Comparison Request ─────────────────────────────────────────
class FranchiseComparisonRequest(BaseModel):
    franchise_ids: List[UUID] = Field(..., min_items=2, max_items=4, description="List of 2 to 4 franchise UUIDs to compare")


class FranchiseComparisonResponse(BaseModel):
    franchises: List[FranchiseOut]
    comparison_matrix: Dict[str, Dict[str, Any]]
