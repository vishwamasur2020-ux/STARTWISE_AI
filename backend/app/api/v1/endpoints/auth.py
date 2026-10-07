"""
STARTWISE AI — Auth Router
Authentication & Verification Endpoints:
- POST /auth/register
- POST /auth/verify-email
- POST /auth/resend-otp
- POST /auth/login
- POST /auth/refresh
- POST /auth/logout
- POST /auth/forgot-password
- POST /auth/verify-reset-otp
- POST /auth/reset-password
- POST /auth/change-password
- GET  /auth/verification-status
- GET  /auth/me
"""

from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database.session import get_db
from app.schemas.schemas import (
    UserRegister,
    UserLogin,
    TokenPair,
    RefreshTokenRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    UserOut,
    MessageResponse,
    VerifyEmailRequest,
    ResendOTPRequest,
    VerifyResetOTPRequest,
    ChangePasswordRequest,
    VerificationStatusResponse,
    AuthRegisterResponse,
)
from app.services.auth_service import AuthService
from app.auth.dependencies import get_current_active_user
from app.models.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_client_ip(request: Request) -> Optional[str]:
    """Helper to extract remote client IP."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


def get_user_agent(request: Request) -> Optional[str]:
    """Helper to extract client User-Agent."""
    return request.headers.get("User-Agent")


@router.post("/register", response_model=AuthRegisterResponse, status_code=201)
async def register(
    payload: UserRegister,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user account in unverified state and dispatch 6-digit OTP verification email.
    """
    service = AuthService(db)
    return await service.register(
        payload=payload,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(
    payload: VerifyEmailRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Verify account email with the 6-digit OTP received during signup.
    """
    service = AuthService(db)
    return await service.verify_email(
        payload=payload,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )


@router.post("/resend-otp", response_model=MessageResponse)
async def resend_otp(
    payload: ResendOTPRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Resend verification or password reset OTP subject to 60s cooldown and rate limiting.
    """
    service = AuthService(db)
    return await service.resend_otp(
        payload=payload,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )


@router.post("/login", response_model=TokenPair)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Authenticate user credentials.
    Returns 403 with EMAIL_NOT_VERIFIED if user has not verified their email.
    """
    service = AuthService(db)
    return await service.login(payload.email, payload.password)


@router.post("/refresh", response_model=TokenPair)
async def refresh_token(payload: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """Exchange a valid refresh token for a new access token and rotated refresh token."""
    service = AuthService(db)
    return await service.refresh_access_token(payload.refresh_token)


@router.post("/logout", response_model=MessageResponse)
async def logout(
    payload: Optional[RefreshTokenRequest] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Revoke user refresh tokens and log out."""
    service = AuthService(db)
    ref_token = payload.refresh_token if payload else None
    return await service.logout(user_id=str(current_user.id), refresh_token=ref_token)


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    payload: ForgotPasswordRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Request password reset OTP for an email address.
    Returns generic response to prevent email enumeration.
    """
    service = AuthService(db)
    return await service.forgot_password(
        payload=payload,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )


@router.post("/verify-reset-otp", response_model=MessageResponse)
async def verify_reset_otp(
    payload: VerifyResetOTPRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Validate password reset OTP code before setting new password.
    """
    service = AuthService(db)
    return await service.verify_reset_otp(
        payload=payload,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    payload: ResetPasswordRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Verify reset OTP, update password, and revoke active sessions.
    """
    service = AuthService(db)
    return await service.reset_password(
        payload=payload,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    payload: ChangePasswordRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Change password for the authenticated user after validating their current password.
    """
    service = AuthService(db)
    return await service.change_password(
        user=current_user,
        payload=payload,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )


@router.get("/verification-status", response_model=VerificationStatusResponse)
async def get_verification_status(
    email: str = Query(..., description="Email address to check"),
    db: AsyncSession = Depends(get_db),
):
    """Check whether an account email has been verified."""
    service = AuthService(db)
    return await service.get_verification_status(email)


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_active_user)):
    """Return current authenticated user profile."""
    return UserOut.model_validate(current_user)
