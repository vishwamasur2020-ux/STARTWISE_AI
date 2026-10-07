"""
STARTWISE AI — OTP Repository
Encapsulates database operations for OTP verifications table.
"""

from datetime import datetime, timezone
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, update, func, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import OTPVerification
from app.repositories.base_repository import BaseRepository
from app.core.logging import get_logger

logger = get_logger(__name__)


class OTPRepository(BaseRepository[OTPVerification]):
    def __init__(self, db: AsyncSession):
        super().__init__(OTPVerification, db)

    async def create_otp_record(
        self,
        email: str,
        otp_hash: str,
        purpose: str,
        expires_at: datetime,
        user_id: Optional[UUID] = None,
        max_attempts: int = 5,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> OTPVerification:
        """Create and persist a new hashed OTP verification record."""
        now = datetime.now(timezone.utc)
        record = OTPVerification(
            email=email.lower().strip(),
            otp_hash=otp_hash,
            purpose=purpose,
            expires_at=expires_at,
            user_id=user_id,
            attempt_count=0,
            max_attempts=max_attempts,
            created_at=now,
            last_sent_at=now,
            used_at=None,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.db.add(record)
        await self.db.flush()
        return record

    async def get_latest_active_otp(
        self,
        email: str,
        purpose: str,
    ) -> Optional[OTPVerification]:
        """Fetch the most recent unused, non-expired OTP record for the email and purpose."""
        now = datetime.now(timezone.utc)
        stmt = (
            select(OTPVerification)
            .where(
                func.lower(OTPVerification.email) == email.lower().strip(),
                OTPVerification.purpose == purpose,
                OTPVerification.used_at.is_(None),
                OTPVerification.expires_at > now,
            )
            .order_by(desc(OTPVerification.created_at))
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_latest_otp(
        self,
        email: str,
        purpose: str,
    ) -> Optional[OTPVerification]:
        """Fetch the latest OTP record (used, unused, or expired) for cooldown checks."""
        stmt = (
            select(OTPVerification)
            .where(
                func.lower(OTPVerification.email) == email.lower().strip(),
                OTPVerification.purpose == purpose,
            )
            .order_by(desc(OTPVerification.created_at))
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def count_recent_sends(
        self,
        email: str,
        since: datetime,
    ) -> int:
        """Count total OTPs generated for an email within a time window for rate limiting."""
        stmt = (
            select(func.count(OTPVerification.id))
            .where(
                func.lower(OTPVerification.email) == email.lower().strip(),
                OTPVerification.created_at >= since,
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar() or 0

    async def invalidate_active_otps(
        self,
        email: str,
        purpose: str,
    ) -> None:
        """Expire all prior unused OTPs for the given email and purpose."""
        now = datetime.now(timezone.utc)
        stmt = (
            update(OTPVerification)
            .where(
                func.lower(OTPVerification.email) == email.lower().strip(),
                OTPVerification.purpose == purpose,
                OTPVerification.used_at.is_(None),
                OTPVerification.expires_at > now,
            )
            .values(expires_at=now)
        )
        await self.db.execute(stmt)
        await self.db.flush()

    async def mark_used(self, otp_record: OTPVerification) -> None:
        """Mark OTP as used so it can never be used again."""
        otp_record.used_at = datetime.now(timezone.utc)
        await self.db.flush()

    async def increment_attempt(self, otp_record: OTPVerification) -> int:
        """Increment incorrect attempt count and persist."""
        otp_record.attempt_count += 1
        if otp_record.attempt_count >= otp_record.max_attempts:
            # Invalidate immediately on exceeding max attempts
            otp_record.expires_at = datetime.now(timezone.utc)
        await self.db.flush()
        return otp_record.attempt_count
