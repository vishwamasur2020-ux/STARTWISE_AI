"""
STARTWISE AI -- Dashboard Schemas (Stage 10)
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

class UserOverview(BaseModel):
    id: UUID
    full_name: str
    email: str
    role: str

class StartupOverview(BaseModel):
    id: UUID
    business_name: str
    business_category: str
    business_model: Optional[str] = None
    investment_amount: float
    expected_monthly_revenue: float
    expected_monthly_expenses: float
    preferred_location: str
    target_customers: str
    experience_years: int = 0
    created_at: datetime

class PredictionOverview(BaseModel):
    id: UUID
    success_probability: float
    risk_level: str
    estimated_roi: float
    competition_level: str
    business_score: float
    score_label: str
    confidence: Optional[float] = 0.85
    created_at: datetime

class FinancialMetrics(BaseModel):
    investment_amount: float
    expected_monthly_revenue: float
    expected_monthly_expenses: float
    monthly_profit: float
    annual_profit: float
    estimated_roi: float
    payback_period_years: Optional[float] = None
    payback_period_label: str

class BusinessHealthDimension(BaseModel):
    dimension: str
    score: float
    label: str

class FranchiseMatchSummary(BaseModel):
    id: UUID
    franchise_name: str
    category: str
    investment_required: float
    match_score: float
    risk_level: str
    location: str
    why_recommended: List[str]

class MarketingSummary(BaseModel):
    marketing_score: float
    strategy_type: str
    recommended_total_budget: float
    top_channels: List[Dict[str, Any]]

class PredictionHistoryItem(BaseModel):
    id: UUID
    analysis_date: datetime
    success_probability: float
    risk_level: str
    estimated_roi: float
    business_score: float
    competition_level: str

class CompletenessItem(BaseModel):
    label: str
    key: str
    completed: bool

class CompletenessChecklist(BaseModel):
    percentage: int
    items: List[CompletenessItem]

class BusinessInsightItem(BaseModel):
    title: str
    type: str  # 'positive', 'warning', 'info', 'action'
    description: str

class ActivityItem(BaseModel):
    id: UUID
    action: str
    resource: str
    details: Optional[Dict[str, Any]] = None
    created_at: datetime

class NotificationItem(BaseModel):
    id: str
    title: str
    message: str
    type: str  # 'info', 'success', 'warning'
    timestamp: datetime

class DashboardResponse(BaseModel):
    user: UserOverview
    startup: Optional[StartupOverview] = None
    all_startups: List[StartupOverview] = []
    prediction: Optional[PredictionOverview] = None
    financial: Optional[FinancialMetrics] = None
    health_dimensions: List[BusinessHealthDimension] = []
    franchises: List[FranchiseMatchSummary] = []
    marketing: Optional[MarketingSummary] = None
    history: List[PredictionHistoryItem] = []
    completeness: CompletenessChecklist
    insights: List[BusinessInsightItem] = []
    activities: List[ActivityItem] = []
    notifications: List[NotificationItem] = []
    has_startups: bool
    has_prediction: bool

class DashboardStatisticsResponse(BaseModel):
    total_startups: int
    completed_analyses: int
    average_business_score: float
    average_success_probability: float
    average_estimated_roi: float
    high_risk_startups_count: int
    recommended_franchises_count: int
    generated_reports_count: int

class AnalysisComparisonRequest(BaseModel):
    analysis_id_a: UUID
    analysis_id_b: UUID

class AnalysisComparisonItem(BaseModel):
    metric: str
    value_a: Any
    value_b: Any
    delta: Optional[float] = None
    unit: str = ""

class AnalysisComparisonResponse(BaseModel):
    analysis_a: PredictionOverview
    analysis_b: PredictionOverview
    comparisons: List[AnalysisComparisonItem]
