"""
STARTWISE AI — Pydantic V2 Schemas (Stage 3 Complete)
Request/response models, Create/Update schemas, and Paginated List responses for all entities.
"""

from datetime import datetime
from typing import Optional, List, Any
from uuid import UUID
import re

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


# ─── Shared Base ─────────────────────────────────────────────────────────────
class BaseResponse(BaseModel):
    model_config = {"from_attributes": True}


# ─── Auth Schemas ─────────────────────────────────────────────────────────────
class UserRegister(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    confirm_password: Optional[str] = None
    phone_number: Optional[str] = None
    phone: Optional[str] = None

    @field_validator("password")
    @classmethod
    def validate_strong_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit.")
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]", v):
            raise ValueError("Password must contain at least one special character.")
        return v

    @model_validator(mode="after")
    def check_passwords_match(self) -> "UserRegister":
        if self.confirm_password and self.password != self.confirm_password:
            raise ValueError("Passwords do not match.")
        return self


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 900


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class VerifyEmailRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")


class ResendOTPRequest(BaseModel):
    email: EmailStr
    purpose: str = Field("EMAIL_VERIFICATION", pattern=r"^(EMAIL_VERIFICATION|PASSWORD_RESET)$")


class VerifyResetOTPRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")


class ResetPasswordRequest(BaseModel):
    email: Optional[EmailStr] = None
    otp: Optional[str] = None
    otp_or_token: Optional[str] = None
    token: Optional[str] = None
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_password: Optional[str] = None

    @field_validator("new_password")
    @classmethod
    def validate_strong_new_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit.")
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]", v):
            raise ValueError("Password must contain at least one special character.")
        return v

    @model_validator(mode="after")
    def check_reset_passwords_match(self) -> "ResetPasswordRequest":
        if self.confirm_password and self.new_password != self.confirm_password:
            raise ValueError("Passwords do not match.")
        if not self.otp and not self.otp_or_token and not self.token:
            raise ValueError("Reset OTP or token is required.")
        return self


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1, max_length=128)
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_password: Optional[str] = None

    @field_validator("new_password")
    @classmethod
    def validate_strong_new_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit.")
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]", v):
            raise ValueError("Password must contain at least one special character.")
        return v

    @model_validator(mode="after")
    def check_passwords_valid(self) -> "ChangePasswordRequest":
        if self.confirm_password and self.new_password != self.confirm_password:
            raise ValueError("Passwords do not match.")
        if self.current_password == self.new_password:
            raise ValueError("New password must be different from your current password.")
        return self


class VerificationStatusResponse(BaseModel):
    email: str
    email_verified: bool
    email_verified_at: Optional[datetime] = None


class AuthRegisterResponse(BaseModel):
    success: bool = True
    message: str = "Verification code sent to your email."
    email: str
    requires_verification: bool = True


# ─── User Schemas ─────────────────────────────────────────────────────────────
class UserOut(BaseResponse):
    id: UUID
    full_name: str
    email: str
    role: str
    is_active: bool
    is_verified: bool
    email_verified: bool = False
    email_verified_at: Optional[datetime] = None
    avatar_url: Optional[str] = None
    profile_image: Optional[str] = None
    phone: Optional[str] = None
    phone_number: Optional[str] = None
    location: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone_number: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    profile_image: Optional[str] = None
    avatar_url: Optional[str] = None


# ─── Startup Idea Schemas ───────────────────────────────────────────────────
class StartupIdeaCreate(BaseModel):
    business_name: str = Field(..., min_length=2, max_length=255)
    business_category: str = Field(..., min_length=2, max_length=100)
    business_model: str = Field(..., min_length=2, max_length=255)
    investment_amount: float = Field(..., gt=0)
    preferred_location: str = Field(..., min_length=2, max_length=255)
    target_customers: str = Field(..., min_length=2, max_length=255)
    experience_years: int = Field(default=0, ge=0, le=50)
    expected_monthly_revenue: float = Field(default=0.0, ge=0)
    market_demand: int = Field(default=5, ge=1, le=10)
    competition_level: str = Field(default="Medium")
    employee_count: int = Field(default=1, ge=0)
    description: Optional[str] = None

    # Aliases
    location: Optional[str] = None
    target_customer: Optional[str] = None
    business_experience_years: Optional[int] = None
    monthly_revenue: Optional[float] = None
    market_demand_score: Optional[int] = None
    employees_count: Optional[int] = None

    @model_validator(mode="after")
    def populate_aliases(self) -> "StartupIdeaCreate":
        if self.location and not self.preferred_location:
            self.preferred_location = self.location
        if self.target_customer and not self.target_customers:
            self.target_customers = self.target_customer
        if self.business_experience_years is not None:
            self.experience_years = self.business_experience_years
        if self.monthly_revenue is not None:
            self.expected_monthly_revenue = self.monthly_revenue
        if self.market_demand_score is not None:
            self.market_demand = self.market_demand_score
        if self.employees_count is not None:
            self.employee_count = self.employees_count
        return self


class StartupIdeaUpdate(BaseModel):
    business_name: Optional[str] = Field(None, min_length=2, max_length=255)
    business_category: Optional[str] = None
    business_model: Optional[str] = None
    investment_amount: Optional[float] = Field(None, gt=0)
    preferred_location: Optional[str] = None
    target_customers: Optional[str] = None
    experience_years: Optional[int] = None
    expected_monthly_revenue: Optional[float] = None
    market_demand: Optional[int] = None
    competition_level: Optional[str] = None
    employee_count: Optional[int] = None
    description: Optional[str] = None


class StartupIdeaOut(BaseResponse):
    id: UUID
    user_id: UUID
    business_name: str
    business_category: str
    business_model: str
    investment_amount: float
    preferred_location: str
    target_customers: str
    experience_years: int
    expected_monthly_revenue: float
    market_demand: int
    competition_level: str
    employee_count: int
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Aliases
    location: Optional[str] = None
    target_customer: Optional[str] = None
    business_experience_years: Optional[int] = None
    monthly_revenue: Optional[float] = None
    market_demand_score: Optional[int] = None
    employees_count: Optional[int] = None


# Backward compatibility alias
BusinessIdeaCreate = StartupIdeaCreate
BusinessIdeaOut = StartupIdeaOut


# ─── Prediction Result Schemas ───────────────────────────────────────────────
class PredictionResultCreate(BaseModel):
    startup_id: UUID
    success_probability: float = Field(..., ge=0, le=100)
    business_score: float = Field(..., ge=0, le=100)
    risk_level: str
    estimated_roi: float
    competition_score: float = Field(default=50.0)
    confidence_score: float = Field(default=85.0)
    ai_recommendation: Optional[Any] = None


class PredictionResultOut(BaseResponse):
    id: UUID
    startup_id: UUID
    success_probability: float
    business_score: float
    risk_level: str
    estimated_roi: float
    competition_score: float
    confidence_score: float
    ai_recommendation: Optional[Any] = None
    created_at: datetime

    # Aliases
    business_idea_id: Optional[UUID] = None
    business_health_score: Optional[float] = None
    roi_prediction: Optional[float] = None


# ─── Franchise Schemas ───────────────────────────────────────────────────────
class FranchiseCreate(BaseModel):
    franchise_name: str = Field(..., min_length=2, max_length=255)
    industry: str = Field(..., min_length=2, max_length=100)
    minimum_investment: float = Field(..., ge=0)
    maximum_investment: float = Field(..., ge=0)
    roi: float = Field(..., ge=0)
    risk_level: str
    city: Optional[str] = None
    state: Optional[str] = None
    country: str = Field(default="India")
    website: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    advantages: Optional[Any] = None
    disadvantages: Optional[Any] = None


class FranchiseUpdate(BaseModel):
    franchise_name: Optional[str] = None
    industry: Optional[str] = None
    minimum_investment: Optional[float] = None
    maximum_investment: Optional[float] = None
    roi: Optional[float] = None
    risk_level: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class FranchiseOut(BaseResponse):
    id: UUID
    franchise_name: str
    industry: str
    minimum_investment: float
    maximum_investment: float
    roi: float
    risk_level: str
    city: Optional[str] = None
    state: Optional[str] = None
    country: str
    website: Optional[str] = None
    contact_email: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    advantages: Optional[Any] = None
    disadvantages: Optional[Any] = None
    is_active: bool
    created_at: datetime

    # Aliases
    name: Optional[str] = None
    category: Optional[str] = None
    min_investment: Optional[float] = None
    max_investment: Optional[float] = None
    expected_roi: Optional[float] = None
    website_url: Optional[str] = None


class FranchiseFilterParams(BaseModel):
    category: Optional[str] = None
    industry: Optional[str] = None
    max_investment: Optional[float] = None
    min_investment: Optional[float] = None
    risk_level: Optional[str] = None
    city: Optional[str] = None
    query: Optional[str] = None


# ─── Marketing Strategy Schemas ──────────────────────────────────────────────
class MarketingStrategyCreate(BaseModel):
    business_category: str
    strategy_name: str
    platform: str
    estimated_budget: Optional[str] = None
    description: str
    expected_result: Optional[str] = None


class MarketingStrategyOut(BaseResponse):
    id: UUID
    business_category: str
    strategy_name: str
    platform: str
    estimated_budget: Optional[str] = None
    description: str
    expected_result: Optional[str] = None
    created_at: datetime

    # Aliases
    channel: Optional[str] = None
    estimated_cost: Optional[str] = None
    estimated_reach: Optional[str] = None


# ─── Report Schemas ──────────────────────────────────────────────────────────
class ReportCreate(BaseModel):
    startup_id: Optional[UUID] = None
    title: str = Field(..., min_length=2, max_length=255)
    pdf_path: Optional[str] = None
    report_data: Optional[Any] = None


class ReportOut(BaseResponse):
    id: UUID
    user_id: UUID
    startup_id: Optional[UUID] = None
    title: str
    pdf_path: Optional[str] = None
    generated_at: datetime

    # Aliases
    business_idea_id: Optional[UUID] = None
    file_path: Optional[str] = None
    created_at: Optional[datetime] = None


# ─── Generic Responses ───────────────────────────────────────────────────────
class MessageResponse(BaseModel):
    message: str
    success: bool = True


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    per_page: int
    pages: int
