"""
STARTWISE AI — User Repository
Extends BaseRepository for User model and authentication token operations.
"""

from datetime import datetime, timezone
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, update, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import User, RefreshToken, PasswordReset
from app.repositories.base_repository import BaseRepository
from app.core.logging import get_logger

logger = get_logger(__name__)


class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.email.ilike(email.strip()))
        )
        return result.scalar_one_or_none()

    async def search_users(self, query: str, skip: int = 0, limit: int = 20) -> List[User]:
        q = f"%{query}%"
        stmt = select(User).where(
            or_(User.full_name.ilike(q), User.email.ilike(q))
        ).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    # ─── Refresh Token Operations ──────────────────────────────────────────────
    async def save_refresh_token(self, user_id: UUID, token: str, expires_at: datetime) -> RefreshToken:
        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            revoked=False,
        )
        self.db.add(refresh_token)
        await self.db.flush()
        return refresh_token

    async def get_refresh_token(self, token: str) -> Optional[RefreshToken]:
        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.token == token,
                RefreshToken.revoked == False,
                RefreshToken.expires_at > datetime.now(timezone.utc),
            )
        )
        return result.scalar_one_or_none()

    async def revoke_refresh_token(self, token: str) -> None:
        await self.db.execute(
            update(RefreshToken)
            .where(RefreshToken.token == token)
            .values(revoked=True)
        )
        await self.db.flush()

    async def revoke_all_user_refresh_tokens(self, user_id: Any) -> None:
        from uuid import UUID as PyUUID
        uid = getattr(user_id, "id", user_id)
        if isinstance(uid, str):
            try:
                uid = PyUUID(uid)
            except Exception:
                pass
        await self.db.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == uid)
            .values(revoked=True)
        )
        await self.db.flush()

    # ─── Password Reset Operations ─────────────────────────────────────────────
    async def create_password_reset(
        self, user_id: UUID, otp_or_token: str, expiry: datetime
    ) -> PasswordReset:
        reset_entry = PasswordReset(
            user_id=user_id,
            otp_or_token=otp_or_token,
            expiry=expiry,
            used=False,
        )
        self.db.add(reset_entry)
        await self.db.flush()
        return reset_entry

    async def get_valid_password_reset(self, otp_or_token: str) -> Optional[PasswordReset]:
        result = await self.db.execute(
            select(PasswordReset).where(
                PasswordReset.otp_or_token == otp_or_token,
                PasswordReset.used == False,
                PasswordReset.expiry > datetime.now(timezone.utc),
            )
        )
        return result.scalar_one_or_none()

    async def mark_password_reset_used(self, reset_entry: PasswordReset) -> None:
        reset_entry.used = True
        await self.db.flush()
