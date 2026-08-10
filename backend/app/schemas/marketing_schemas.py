"""
STARTWISE AI — Marketing Strategy Schemas (Stage 9 Pydantic V2)

Request and response models for Marketing Strategy generation, retrieval,
channel details, budget scenarios, campaign ideas, content strategy, and 30-day timeline tasks.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field

from app.schemas.schemas import BaseResponse


# ─── Marketing Channel Item Schema ──────────────────────────────────────────
class MarketingChannelItem(BaseModel):
    channel_name: str
    platform: str
    target_audience: List[str]
    business_categories: List[str]
    minimum_budget: float
    recommended_budget: float
    cost_level: str
    reach_level: str
    conversion_potential: str
    local_business_score: float
    digital_score: float
    b2b_score: float
    b2c_score: float
    difficulty: str
    time_to_results: str
    description: str
    best_for: str
    marketing_score: float = Field(..., description="0-100 calculated fit score")
    score_label: str = Field(..., description="Excellent, Strong, Good, etc.")
    ranking_position: int
    allocated_budget: float
    explanation: List[str]
    sub_scores: Dict[str, float]


# ─── Campaign Idea Schema ───────────────────────────────────────────────────
class CampaignIdeaItem(BaseModel):
    campaign_name: str
    platform: str
    objective: str
    target_audience: str
    estimated_budget: float
    call_to_action: str
    description: str


# ─── 30-Day Plan Task Item ──────────────────────────────────────────────────
class ThirtyDayTaskItem(BaseModel):
    task_name: str
    channel: str
    expected_objective: str
    kpis: str
    status: str = "Pending"


class ThirtyDayWeekPhase(BaseModel):
    week: int
    phase: str
    tasks: List[ThirtyDayTaskItem]


# ─── Marketing Strategy Request ─────────────────────────────────────────────
class MarketingStrategyRequest(BaseModel):
    startup_id: UUID = Field(..., description="UUID of startup idea to analyze")


# ─── Full Marketing Strategy Response ───────────────────────────────────────
class MarketingStrategyResponse(BaseResponse):
    id: Optional[UUID] = None
    startup_id: UUID
    user_id: Optional[UUID] = None
    strategy_name: str
    strategy_type: str = "BALANCED"
    marketing_score: float
    strategy_label: str
    total_recommended_budget: float
    profile: Dict[str, Any]
    recommended_channels: List[MarketingChannelItem]
    budget_allocation: Dict[str, Any]
    campaign_ideas: List[CampaignIdeaItem]
    content_strategy: Dict[str, Any]
    thirty_day_plan: List[ThirtyDayWeekPhase]
    kpis: List[Dict[str, str]]
    disclaimer: str = Field(default="INDICATIVE ESTIMATES: Marketing figures are dataset-driven estimates.")
    created_at: datetime = Field(default_factory=datetime.utcnow)
