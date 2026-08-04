"""
STARTWISE AI — Auth Dependencies
FastAPI dependencies to extract, validate, and enforce RBAC rules for authenticated users.
"""

from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_subject_from_token
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.database.session import get_db
from app.models.models import User, UserRole
from app.repositories.user_repository import UserRepository

security = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Dependency: extracts and validates JWT access token from Authorization header."""
    token = None
    if credentials:
        token = credentials.credentials
    else:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

    if not token:
        raise UnauthorizedException("Authentication token missing or invalid Bearer format.")

    user_id = get_subject_from_token(token, expected_type="access")

    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)

    if not user:
        raise UnauthorizedException("User associated with token not found.")
    if not user.is_active:
        raise ForbiddenException("Account has been deactivated.")

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency: ensures user is active."""
    return current_user


async def get_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency: Role-Based Access Control (RBAC) restricting route to ADMIN role."""
    if current_user.role != UserRole.admin:
        raise ForbiddenException("Access denied. Admin role privilege required.")
    return current_user
