"""
STARTWISE AI — Auth Router (v1)
Full Authentication & Authorization Endpoints:
- POST /auth/register
- POST /auth/login
- POST /auth/refresh
- POST /auth/logout
- POST /auth/forgot-password
- POST /auth/reset-password
- GET  /auth/me
"""

from fastapi import APIRouter, Depends, Header
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
)
from app.services.auth_service import AuthService
from app.auth.dependencies import get_current_active_user
from app.models.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserOut, status_code=201)
async def register(payload: UserRegister, db: AsyncSession = Depends(get_db)):
    """Register a new user account."""
    service = AuthService(db)
    return await service.register(payload)


@router.post("/login", response_model=TokenPair)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate user credentials and return JWT Access Token & Refresh Token."""
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
async def forgot_password(payload: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    """Request a password reset OTP/token for an email address."""
    service = AuthService(db)
    return await service.forgot_password(payload)


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(payload: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    """Verify reset OTP/token and set a new password."""
    service = AuthService(db)
    return await service.reset_password(payload)


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_active_user)):
    """Return current authenticated user profile."""
    return UserOut.model_validate(current_user)
