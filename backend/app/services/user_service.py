"""
STARTWISE AI — User Service
High-level service managing user profiles, role assignments, and user listings.
"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import User
from app.repositories.user_repository import UserRepository
from app.schemas.schemas import UserOut, UserUpdate
from app.core.exceptions import NotFoundException, ForbiddenException
from app.database.mixins import PaginationParams, PaginatedResult


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = UserRepository(db)

    async def get_user_by_id(self, user_id: str | UUID) -> UserOut:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found.")
        return UserOut.model_validate(user)

    async def update_user_profile(self, user: User, payload: UserUpdate) -> UserOut:
        update_data = payload.model_dump(exclude_none=True)
        if "phone_number" in update_data and "phone" not in update_data:
            update_data["phone"] = update_data["phone_number"]
        if "profile_image" in update_data and "avatar_url" not in update_data:
            update_data["avatar_url"] = update_data["profile_image"]

        updated = await self.repo.update(user, **update_data)
        return UserOut.model_validate(updated)

    async def list_all_users(self, page: int = 1, per_page: int = 20) -> PaginatedResult[UserOut]:
        params = PaginationParams(page=page, per_page=per_page)
        result = await self.repo.paginate(params, order_by=User.created_at.desc())
        
        user_outs = [UserOut.model_validate(u) for u in result.items]
        return PaginatedResult.create(items=user_outs, total=result.total, params=params)
