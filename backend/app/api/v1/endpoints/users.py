"""
STARTWISE AI — Users Router (v1)
Endpoints for user profile management and admin user management.
- GET   /users/me
- PATCH /users/profile
- GET   /users/all (Admin RBAC)
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.schemas import UserOut, UserUpdate, MessageResponse
from app.auth.dependencies import get_current_active_user, get_admin_user
from app.models.models import User
from app.repositories.user_repository import UserRepository

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserOut)
async def get_current_user_profile(current_user: User = Depends(get_current_active_user)):
    """Get the authenticated user's profile information."""
    return UserOut.model_validate(current_user)


@router.patch("/profile", response_model=UserOut)
async def update_user_profile(
    payload: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update profile attributes for the authenticated user."""
    repo = UserRepository(db)
    
    update_data = payload.model_dump(exclude_none=True)
    if "phone_number" in update_data and "phone" not in update_data:
        update_data["phone"] = update_data["phone_number"]
    if "profile_image" in update_data and "avatar_url" not in update_data:
        update_data["avatar_url"] = update_data["profile_image"]

    updated_user = await repo.update(current_user, **update_data)
    return UserOut.model_validate(updated_user)


@router.get("/all", response_model=list[UserOut])
async def list_users_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Admin Only: List registered users with pagination."""
    repo = UserRepository(db)
    users = await repo.get_all(skip=skip, limit=limit)
    return [UserOut.model_validate(u) for u in users]
