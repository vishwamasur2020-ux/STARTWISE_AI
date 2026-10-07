"""
STARTWISE AI — Production ORM Models (Stage 3)
Complete database tables defined with SQLAlchemy 2.0 mapped columns, relationships, and property aliases.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List, Any
import enum

from sqlalchemy import (
    String, Boolean, Text, Float, Integer,
    DateTime, ForeignKey, JSON, Enum as SAEnum, Uuid
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base
from app.database.mixins import UUIDMixin, TimestampMixin


# ─── Enums ───────────────────────────────────────────────────────────────────
class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"
    USER = "USER"
    ADMIN = "ADMIN"


class BusinessCategory(str, enum.Enum):
    food = "Food"
    retail = "Retail"
    technology = "Technology"
    healthcare = "Healthcare"
    education = "Education"
    agriculture = "Agriculture"
    manufacturing = "Manufacturing"
    finance = "Finance"
    tourism = "Tourism"
    other = "Other"


class CompetitionLevel(str, enum.Enum):
    low = "Low"
    medium = "Medium"
    high = "High"


class RiskLevel(str, enum.Enum):
    low = "Low"
    medium = "Medium"
    high = "High"


# ─── User Model ──────────────────────────────────────────────────────────────
class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), default=UserRole.user, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    email_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    profile_image_col: Mapped[Optional[str]] = mapped_column("profile_image", String(500), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Spec Property Aliases
    @property
    def password_hash(self) -> str:
        return self.hashed_password

    @password_hash.setter
    def password_hash(self, value: str):
        self.hashed_password = value

    @property
    def phone_number(self) -> Optional[str]:
        return self.phone

    @phone_number.setter
    def phone_number(self, value: Optional[str]):
        self.phone = value

    @property
    def profile_image(self) -> Optional[str]:
        return self.avatar_url or self.profile_image_col

    # Relationships
    startup_ideas: Mapped[List["StartupIdea"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    reports: Mapped[List["Report"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    password_resets: Mapped[List["PasswordReset"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    otp_verifications: Mapped[List["OTPVerification"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    # Alias for backward compatibility
    @property
    def business_ideas(self):
        return self.startup_ideas


# ─── Startup Idea Model ──────────────────────────────────────────────────────
class StartupIdea(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "startup_ideas"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    business_name: Mapped[str] = mapped_column(String(255), nullable=False)
    business_category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    business_model: Mapped[str] = mapped_column(String(255), nullable=False)
    investment_amount: Mapped[float] = mapped_column(Float, nullable=False)
    preferred_location: Mapped[str] = mapped_column(String(255), nullable=False)
    target_customers: Mapped[str] = mapped_column(String(255), nullable=False)
    experience_years: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    expected_monthly_revenue: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    market_demand: Mapped[int] = mapped_column(Integer, default=5, nullable=False)  # 1-10 scale
    competition_level: Mapped[str] = mapped_column(String(50), default="Medium", nullable=False)
    employee_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Spec Property Aliases for Stage 1/2 field names
    @property
    def location(self) -> str:
        return self.preferred_location

    @location.setter
    def location(self, val: str):
        self.preferred_location = val

    @property
    def target_customer(self) -> str:
        return self.target_customers

    @target_customer.setter
    def target_customer(self, val: str):
        self.target_customers = val

    @property
    def business_experience_years(self) -> int:
        return self.experience_years

    @business_experience_years.setter
    def business_experience_years(self, val: int):
        self.experience_years = val

    @property
    def monthly_revenue(self) -> float:
        return self.expected_monthly_revenue

    @monthly_revenue.setter
    def monthly_revenue(self, val: float):
        self.expected_monthly_revenue = val

    @property
    def market_demand_score(self) -> int:
        return self.market_demand

    @market_demand_score.setter
    def market_demand_score(self, val: int):
        self.market_demand = val

    @property
    def employees_count(self) -> int:
        return self.employee_count

    @employees_count.setter
    def employees_count(self, val: int):
        self.employee_count = val

    # Relationships
    user: Mapped["User"] = relationship(back_populates="startup_ideas")
    prediction_result: Mapped[Optional["PredictionResult"]] = relationship(
        back_populates="startup_idea", uselist=False, cascade="all, delete-orphan"
    )
    reports: Mapped[List["Report"]] = relationship(
        back_populates="startup_idea", cascade="all, delete-orphan"
    )

    # Alias for owner relationship
    @property
    def owner(self) -> User:
        return self.user


# Class alias for BusinessIdea
BusinessIdea = StartupIdea


# ─── Prediction Result Model ─────────────────────────────────────────────────
class PredictionResult(Base, UUIDMixin):
    __tablename__ = "prediction_results"

    startup_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("startup_ideas.id", ondelete="CASCADE"),
        unique=False,
        nullable=False,
        index=True,
    )
    success_probability: Mapped[float] = mapped_column(Float, nullable=False)  # Percentage 0-100
    business_score: Mapped[float] = mapped_column(Float, nullable=False)     # Health score 0-100
    risk_level: Mapped[str] = mapped_column(String(50), nullable=False)         # Low, Medium, High
    estimated_roi: Mapped[float] = mapped_column(Float, nullable=False)        # Expected ROI %
    competition_score: Mapped[float] = mapped_column(Float, default=50.0, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=85.0, nullable=False)
    ai_recommendation: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Property Aliases
    @property
    def business_idea_id(self) -> uuid.UUID:
        return self.startup_id

    @business_idea_id.setter
    def business_idea_id(self, val: uuid.UUID):
        self.startup_id = val

    @property
    def business_health_score(self) -> float:
        return self.business_score

    @business_health_score.setter
    def business_health_score(self, val: float):
        self.business_score = val

    @property
    def roi_prediction(self) -> float:
        return self.estimated_roi

    @roi_prediction.setter
    def roi_prediction(self, val: float):
        self.estimated_roi = val

    # Relationships
    startup_idea: Mapped["StartupIdea"] = relationship(back_populates="prediction_result")
    explanations: Mapped[List["PredictionExplanation"]] = relationship(
        back_populates="prediction_result", cascade="all, delete-orphan"
    )

    @property
    def business_idea(self) -> StartupIdea:
        return self.startup_idea


# ─── Prediction Explanation Model (Stage 13 XAI) ─────────────────────────────
class PredictionExplanation(Base, UUIDMixin):
    __tablename__ = "prediction_explanations"

    prediction_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("prediction_results.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    model_name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # success, risk, roi, competition, combined
    explanation_method: Mapped[str] = mapped_column(String(100), nullable=False)     # SHAP TreeExplainer, SHAP LinearExplainer, etc.
    feature_contributions: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True) # Full list of features & SHAP values
    positive_factors: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)      # Ranked positive drivers
    negative_factors: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)      # Ranked negative drivers
    summary: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)               # Narrative insights & decision summary
    model_version: Mapped[str] = mapped_column(String(50), default="1.0.0", nullable=False)
    explanation_version: Mapped[str] = mapped_column(String(50), default="1.0.0", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    prediction_result: Mapped["PredictionResult"] = relationship(back_populates="explanations")


# ─── Franchise Model ─────────────────────────────────────────────────────────
class Franchise(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "franchises"

    franchise_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    industry: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    minimum_investment: Mapped[float] = mapped_column(Float, nullable=False)
    maximum_investment: Mapped[float] = mapped_column(Float, nullable=False)
    roi: Mapped[float] = mapped_column(Float, nullable=False)  # Annual expected ROI %
    risk_level: Mapped[str] = mapped_column(String(50), nullable=False)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country: Mapped[str] = mapped_column(String(100), default="India", nullable=False)
    website: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    contact_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    advantages: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    disadvantages: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    business_model: Mapped[Optional[str]] = mapped_column(String(100), default="Franchise", nullable=True)
    experience_required: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    market_demand: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    target_customer: Mapped[Optional[str]] = mapped_column(String(255), default="General Public", nullable=True)

    # Spec Aliases
    @property
    def name(self) -> str:
        return self.franchise_name

    @name.setter
    def name(self, val: str):
        self.franchise_name = val


# ─── Franchise Recommendation Model ──────────────────────────────────────────
class FranchiseRecommendation(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "franchise_recommendations"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    startup_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("startup_ideas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    franchise_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("franchises.id", ondelete="CASCADE"), nullable=False, index=True
    )
    match_score: Mapped[float] = mapped_column(Float, nullable=False)
    ranking_position: Mapped[int] = mapped_column(Integer, nullable=False)
    recommendation_type: Mapped[str] = mapped_column(String(50), default="PRIMARY", nullable=False)  # PRIMARY / ALTERNATIVE
    explanation: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship()
    startup_idea: Mapped["StartupIdea"] = relationship()
    franchise: Mapped["Franchise"] = relationship()

    @property
    def category(self) -> str:
        return self.industry

    @category.setter
    def category(self, val: str):
        self.industry = val

    @property
    def min_investment(self) -> float:
        return self.minimum_investment

    @min_investment.setter
    def min_investment(self, val: float):
        self.minimum_investment = val

    @property
    def max_investment(self) -> float:
        return self.maximum_investment

    @max_investment.setter
    def max_investment(self, val: float):
        self.maximum_investment = val

    @property
    def expected_roi(self) -> float:
        return self.roi

    @expected_roi.setter
    def expected_roi(self, val: float):
        self.roi = val

    @property
    def website_url(self) -> Optional[str]:
        return self.website

    @website_url.setter
    def website_url(self, val: Optional[str]):
        self.website = val


# ─── Marketing Strategy Model ────────────────────────────────────────────────
class MarketingStrategy(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "marketing_strategies"

    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )
    startup_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("startup_ideas.id", ondelete="CASCADE"), nullable=True, index=True
    )
    business_category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    strategy_name: Mapped[str] = mapped_column(String(255), default="Personalized AI Marketing Strategy", nullable=False)
    platform: Mapped[str] = mapped_column(String(100), default="Omnichannel", nullable=False)
    estimated_budget: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[str] = mapped_column(Text, default="Personalized AI Marketing & Promotion Strategy", nullable=False)
    expected_result: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Stage 9 Multi-channel strategy fields
    total_budget: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    strategy_type: Mapped[str] = mapped_column(String(50), default="BALANCED", nullable=False)  # LOW_BUDGET, BALANCED, AGGRESSIVE
    marketing_score: Mapped[float] = mapped_column(Float, default=85.0, nullable=False)
    recommended_channels: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    budget_allocation: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    campaign_ideas: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    content_strategy: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    kpis: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    thirty_day_plan: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)

    # Relationships
    user: Mapped[Optional["User"]] = relationship()
    startup_idea: Mapped[Optional["StartupIdea"]] = relationship()

    # Spec Aliases
    @property
    def channel(self) -> str:
        return self.platform

    @channel.setter
    def channel(self, val: str):
        self.platform = val

    @property
    def estimated_cost(self) -> Optional[str]:
        return self.estimated_budget

    @estimated_cost.setter
    def estimated_cost(self, val: Optional[str]):
        self.estimated_budget = val

    @property
    def estimated_reach(self) -> Optional[str]:
        return self.expected_result

    @estimated_reach.setter
    def estimated_reach(self, val: Optional[str]):
        self.expected_result = val


# ─── Report Model ────────────────────────────────────────────────────────────
class Report(Base, UUIDMixin):
    __tablename__ = "reports"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    startup_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("startup_ideas.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    pdf_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    report_data: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Spec Aliases
    @property
    def business_idea_id(self) -> Optional[uuid.UUID]:
        return self.startup_id

    @business_idea_id.setter
    def business_idea_id(self, val: Optional[uuid.UUID]):
        self.startup_id = val

    @property
    def file_path(self) -> Optional[str]:
        return self.pdf_path

    @file_path.setter
    def file_path(self, val: Optional[str]):
        self.pdf_path = val

    @property
    def created_at(self) -> datetime:
        return self.generated_at

    # Relationships
    user: Mapped["User"] = relationship(back_populates="reports")
    startup_idea: Mapped[Optional["StartupIdea"]] = relationship(back_populates="reports")


# ─── Refresh Token Model ─────────────────────────────────────────────────────
class RefreshToken(Base, UUIDMixin):
    __tablename__ = "refresh_tokens"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    token: Mapped[str] = mapped_column(String(500), unique=True, nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="refresh_tokens")


# ─── Password Reset Model ───────────────────────────────────────────────────
class PasswordReset(Base, UUIDMixin):
    __tablename__ = "password_resets"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    otp_or_token: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    expiry: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="password_resets")


# ─── Audit Log Model ─────────────────────────────────────────────────────────
class AuditLog(Base, UUIDMixin):
    __tablename__ = "audit_logs"

    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource: Mapped[str] = mapped_column(String(100), default="system", nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    details: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    user: Mapped[Optional["User"]] = relationship(back_populates="audit_logs")


# ─── OTP Verification Model ───────────────────────────────────────────────────
class OTPVerification(Base, UUIDMixin):
    __tablename__ = "otp_verifications"

    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    otp_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    purpose: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # EMAIL_VERIFICATION, PASSWORD_RESET
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    attempt_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_attempts: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relationships
    user: Mapped[Optional["User"]] = relationship(back_populates="otp_verifications")

