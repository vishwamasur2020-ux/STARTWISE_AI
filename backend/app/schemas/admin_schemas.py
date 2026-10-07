"""
STARTWISE AI — Admin Schemas (Stage 12)
Pydantic V2 request/response models for all admin API endpoints.
"""

from datetime import datetime
from typing import Optional, List, Any, Dict
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# ─── Shared ──────────────────────────────────────────────────────────────────
class AdminBase(BaseModel):
    model_config = {"from_attributes": True}


# ─── Dashboard Stats ──────────────────────────────────────────────────────────
class UserStats(AdminBase):
    total: int
    active: int


class StartupStats(AdminBase):
    total: int


class PredictionStats(AdminBase):
    total: int
    average_score: float
    average_success_probability: float
    average_roi: float
    high_risk_count: int


class ReportStats(AdminBase):
    total: int
    emails_sent: int


class FranchiseStats(AdminBase):
    total: int


class AdminDashboardStats(AdminBase):
    users: UserStats
    startups: StartupStats
    predictions: PredictionStats
    reports: ReportStats
    franchises: FranchiseStats


# ─── User Management ─────────────────────────────────────────────────────────
class AdminUserOut(AdminBase):
    id: UUID
    full_name: str
    email: str
    role: str
    is_active: bool
    is_verified: bool
    email_verified: bool = False
    email_verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    startup_count: int = 0
    analysis_count: int = 0
    report_count: int = 0
    last_activity: Optional[datetime] = None


class AdminUserListResponse(AdminBase):
    items: List[AdminUserOut]
    total: int
    page: int
    per_page: int
    pages: int


class AdminUserDetail(AdminBase):
    id: UUID
    full_name: str
    email: str
    role: str
    is_active: bool
    is_verified: bool
    email_verified: bool = False
    email_verified_at: Optional[datetime] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    startup_count: int = 0
    analysis_count: int = 0
    report_count: int = 0
    last_activity: Optional[datetime] = None
    recent_startups: List[Dict[str, Any]] = []
    recent_reports: List[Dict[str, Any]] = []


class UpdateUserStatusRequest(BaseModel):
    is_active: bool


class UpdateUserRoleRequest(BaseModel):
    role: str = Field(..., pattern="^(user|admin|USER|ADMIN)$")


# ─── Startup Admin ────────────────────────────────────────────────────────────
class AdminStartupOut(AdminBase):
    id: UUID
    business_name: str
    owner_name: str
    owner_email: str
    business_category: str
    preferred_location: str
    investment_amount: float
    success_probability: Optional[float] = None
    risk_level: Optional[str] = None
    estimated_roi: Optional[float] = None
    business_score: Optional[float] = None
    has_prediction: bool = False
    created_at: datetime


class AdminStartupListResponse(AdminBase):
    items: List[AdminStartupOut]
    total: int
    page: int
    per_page: int
    pages: int


class AdminStartupDetail(AdminBase):
    id: UUID
    business_name: str
    owner_name: str
    owner_email: str
    business_category: str
    business_model: str
    preferred_location: str
    target_customers: str
    investment_amount: float
    expected_monthly_revenue: float
    market_demand: int
    competition_level: str
    experience_years: int
    employee_count: int
    description: Optional[str] = None
    created_at: datetime
    # Prediction
    prediction: Optional[Dict[str, Any]] = None
    # Related
    franchise_recs_count: int = 0
    marketing_count: int = 0
    reports_count: int = 0


# ─── Prediction Admin ─────────────────────────────────────────────────────────
class AdminPredictionOut(AdminBase):
    id: UUID
    startup_id: UUID
    startup_name: str
    owner_name: str
    success_probability: float
    business_score: float
    risk_level: str
    estimated_roi: float
    competition_score: float
    confidence_score: float
    created_at: datetime


class AdminPredictionListResponse(AdminBase):
    items: List[AdminPredictionOut]
    total: int
    page: int
    per_page: int
    pages: int


# ─── Franchise Admin ──────────────────────────────────────────────────────────
class AdminFranchiseCreate(BaseModel):
    franchise_name: str = Field(..., min_length=2, max_length=255)
    industry: str = Field(..., min_length=2, max_length=100)
    business_model: Optional[str] = Field(default="Franchise", max_length=100)
    minimum_investment: float = Field(..., gt=0)
    maximum_investment: float = Field(..., gt=0)
    roi: float = Field(..., ge=0)
    risk_level: str = Field(..., pattern="^(Low|Medium|High)$")
    city: Optional[str] = None
    state: Optional[str] = None
    country: str = Field(default="India")
    experience_required: int = Field(default=0, ge=0)
    market_demand: int = Field(default=5, ge=1, le=10)
    target_customer: Optional[str] = None
    description: Optional[str] = None
    advantages: Optional[List[str]] = None
    disadvantages: Optional[List[str]] = None
    website: Optional[str] = None
    contact_email: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: bool = True


class AdminFranchiseUpdate(BaseModel):
    franchise_name: Optional[str] = Field(None, min_length=2, max_length=255)
    industry: Optional[str] = None
    business_model: Optional[str] = None
    minimum_investment: Optional[float] = Field(None, gt=0)
    maximum_investment: Optional[float] = Field(None, gt=0)
    roi: Optional[float] = Field(None, ge=0)
    risk_level: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    experience_required: Optional[int] = None
    market_demand: Optional[int] = None
    target_customer: Optional[str] = None
    description: Optional[str] = None
    advantages: Optional[List[str]] = None
    disadvantages: Optional[List[str]] = None
    website: Optional[str] = None
    contact_email: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: Optional[bool] = None


class AdminFranchiseOut(AdminBase):
    id: UUID
    franchise_name: str
    industry: str
    business_model: Optional[str] = None
    minimum_investment: float
    maximum_investment: float
    roi: float
    risk_level: str
    city: Optional[str] = None
    state: Optional[str] = None
    country: str
    experience_required: int
    market_demand: int
    target_customer: Optional[str] = None
    description: Optional[str] = None
    advantages: Optional[Any] = None
    disadvantages: Optional[Any] = None
    website: Optional[str] = None
    contact_email: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class AdminFranchiseListResponse(AdminBase):
    items: List[AdminFranchiseOut]
    total: int
    page: int
    per_page: int
    pages: int


class ToggleFranchiseStatusRequest(BaseModel):
    is_active: bool


# ─── Marketing Admin ──────────────────────────────────────────────────────────
class AdminMarketingOut(AdminBase):
    id: UUID
    strategy_name: str
    business_category: str
    platform: str
    total_budget: float
    strategy_type: str
    marketing_score: float
    startup_id: Optional[UUID] = None
    startup_name: Optional[str] = None
    owner_name: Optional[str] = None
    created_at: datetime


class AdminMarketingListResponse(AdminBase):
    items: List[AdminMarketingOut]
    total: int
    page: int
    per_page: int
    pages: int


# ─── Reports Admin ────────────────────────────────────────────────────────────
class AdminReportOut(AdminBase):
    id: UUID
    title: str
    user_id: UUID
    owner_name: str
    owner_email: str
    startup_id: Optional[UUID] = None
    startup_name: Optional[str] = None
    generated_at: datetime
    has_file: bool
    pdf_path: Optional[str] = None


class AdminReportListResponse(AdminBase):
    items: List[AdminReportOut]
    total: int
    page: int
    per_page: int
    pages: int


# ─── ML Monitoring ────────────────────────────────────────────────────────────
class ModelInfo(AdminBase):
    name: str
    algorithm: Optional[str] = None
    version: str = "1.0.0"
    status: str  # loaded / not_loaded
    loaded: bool


class ServiceHealthItem(AdminBase):
    name: str
    status: str  # healthy / degraded / unavailable
    message: Optional[str] = None


class AdminMLResponse(AdminBase):
    models: List[ModelInfo]
    preprocessors: List[ModelInfo]
    services: List[ServiceHealthItem]
    metrics: Dict[str, Any]
    artifacts_dir: str
    is_fully_loaded: bool


# ─── Audit Logs ───────────────────────────────────────────────────────────────
class AdminAuditLogOut(AdminBase):
    id: UUID
    timestamp: datetime
    admin_name: Optional[str] = None
    admin_email: Optional[str] = None
    action: str
    resource: str
    resource_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    details: Optional[Any] = None


class AdminAuditLogListResponse(AdminBase):
    items: List[AdminAuditLogOut]
    total: int
    page: int
    per_page: int
    pages: int


# ─── Analytics ────────────────────────────────────────────────────────────────
class TimeSeriesPoint(AdminBase):
    date: str
    value: float
    label: Optional[str] = None


class DistributionItem(AdminBase):
    label: str
    count: int
    percentage: float


class AdminAnalyticsResponse(AdminBase):
    user_growth: List[TimeSeriesPoint]
    startup_creation: List[TimeSeriesPoint]
    analysis_volume: List[TimeSeriesPoint]
    risk_distribution: List[DistributionItem]
    success_distribution: List[DistributionItem]
    category_distribution: List[DistributionItem]
    avg_business_score_trend: List[TimeSeriesPoint]
    avg_roi_trend: List[TimeSeriesPoint]
    report_generation: List[TimeSeriesPoint]
    franchise_rec_volume: List[TimeSeriesPoint]
    period_start: Optional[str] = None
    period_end: Optional[str] = None


# ─── Settings ─────────────────────────────────────────────────────────────────
class AdminSettingsResponse(AdminBase):
    platform: Dict[str, Any]
    email: Dict[str, Any]
    ml: Dict[str, Any]
    security: Dict[str, Any]
