"""
STARTWISE AI — OTP Service
Handles cryptographically secure OTP generation, HMAC-SHA256 hashing,
timing-safe validation, expiration verification, attempt limiting, and cooldown enforcement.
"""

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import BadRequestException
from app.models.models import OTPVerification
from app.repositories.otp_repository import OTPRepository
from app.core.logging import get_logger

logger = get_logger(__name__)


class OTPService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.otp_repo = OTPRepository(db)

    @staticmethod
    def generate_otp() -> str:
        """Generate a cryptographically secure 6-digit OTP."""
        return f"{secrets.randbelow(900000) + 100000}"

    @staticmethod
    def hash_otp(otp: str, email: str = "") -> str:
        """
        Secure server-side HMAC-SHA256 hashing bound to normalized email.
        Never stores plaintext OTP in the database.
        """
        normalized_email = email.lower().strip()
        secret_key = ""
        if settings.OTP_SECRET:
            if hasattr(settings.OTP_SECRET, "get_secret_value"):
                secret_key = settings.OTP_SECRET.get_secret_value()
            else:
                secret_key = str(settings.OTP_SECRET)
        if not secret_key:
            secret_key = settings.JWT_SECRET_KEY

        key_bytes = secret_key.encode("utf-8")
        msg = f"{otp}:{normalized_email}".encode("utf-8")
        return hmac.new(key_bytes, msg, hashlib.sha256).hexdigest()

    async def check_resend_cooldown(self, email: str, purpose: str) -> None:
        """
        Enforce minimum cooldown between OTP requests to prevent spam.
        Raises BadRequestException if requested too soon.
        """
        latest = await self.otp_repo.get_latest_otp(email, purpose)
        if latest:
            now = datetime.now(timezone.utc)
            last_sent = latest.last_sent_at if latest.last_sent_at.tzinfo else latest.last_sent_at.replace(tzinfo=timezone.utc)
            elapsed = (now - last_sent).total_seconds()
            if elapsed < settings.OTP_RESEND_COOLDOWN_SECONDS:
                remaining = int(settings.OTP_RESEND_COOLDOWN_SECONDS - elapsed)
                logger.warning(f"OTP cooldown triggered for {email} ({remaining}s remaining)")
                raise BadRequestException("Please wait before requesting another code.")

    async def check_rate_limit(self, email: str) -> None:
        """
        Enforce rate limiting: maximum sends per time window.
        """
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(minutes=settings.OTP_RATE_LIMIT_WINDOW_MINUTES)
        count = await self.otp_repo.count_recent_sends(email, window_start)
        if count >= settings.OTP_MAX_SENDS_PER_WINDOW:
            logger.warning(f"OTP rate limit exceeded for {email} ({count} sends in window)")
            raise BadRequestException("Maximum verification requests exceeded. Please try again later.")

    async def create_otp(
        self,
        email: str,
        purpose: str,
        user_id: Optional[UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Tuple[str, OTPVerification]:
        """
        Validate cooldown and rate limit, invalidate previous active codes,
        and generate a new secure OTP with metadata.
        Returns (raw_otp, record). The raw OTP must only be emailed and NEVER returned to the client.
        """
        normalized_email = email.lower().strip()
        await self.check_rate_limit(normalized_email)
        await self.check_resend_cooldown(normalized_email, purpose)

        # Invalidate any prior active OTPs for this email + purpose
        await self.otp_repo.invalidate_active_otps(normalized_email, purpose)

        raw_otp = self.generate_otp()
        hashed = self.hash_otp(raw_otp, normalized_email)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)

        record = await self.otp_repo.create_otp_record(
            email=normalized_email,
            otp_hash=hashed,
            purpose=purpose,
            expires_at=expires_at,
            user_id=user_id,
            max_attempts=settings.OTP_MAX_ATTEMPTS,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return raw_otp, record

    async def verify_otp(
        self,
        email: str,
        otp: str,
        purpose: str,
    ) -> Tuple[bool, str, Optional[OTPVerification]]:
        """
        Verify the OTP against the database record with attempt limiting and expiration checks.
        Returns (success: bool, message: str, record: Optional[OTPVerification]).
        """
        normalized_email = email.lower().strip()
        record = await self.otp_repo.get_latest_active_otp(normalized_email, purpose)

        if not record:
            return False, "OTP has expired. Please request a new code.", None

        if record.used_at is not None:
            return False, "This verification code has already been used.", record

        # Check attempt count
        if record.attempt_count >= record.max_attempts:
            await self.otp_repo.invalidate(record)
            return False, "Too many incorrect attempts. Please request a new OTP.", record

        # Check expiration
        now = datetime.now(timezone.utc)
        record_expiry = record.expires_at if record.expires_at.tzinfo else record.expires_at.replace(tzinfo=timezone.utc)
        if now > record_expiry:
            return False, "OTP has expired. Please request a new code.", record

        # Timing-safe comparison of the hash
        expected_hash = self.hash_otp(otp.strip(), normalized_email)
        is_valid = secrets.compare_digest(record.otp_hash, expected_hash)

        if not is_valid:
            attempts = await self.otp_repo.increment_attempt(record)
            if attempts >= record.max_attempts:
                return False, "Too many incorrect attempts. Please request a new OTP.", record
            remaining = record.max_attempts - attempts
            return False, f"Invalid verification code. {remaining} attempt(s) remaining.", record

        # OTP is valid — mark as used
        await self.otp_repo.mark_used(record)
        return True, "Verification successful.", record

    async def verify_otp_without_consuming(
        self,
        email: str,
        otp: str,
        purpose: str,
    ) -> Tuple[bool, str, Optional[OTPVerification]]:
        """
        Validate OTP for a preliminary check (e.g., verify-reset-otp) without setting used_at.
        Still increments attempt count on invalid attempt.
        """
        normalized_email = email.lower().strip()
        record = await self.otp_repo.get_latest_active_otp(normalized_email, purpose)

        if not record:
            return False, "OTP has expired. Please request a new code.", None

        if record.used_at is not None:
            return False, "This verification code has already been used.", record

        if record.attempt_count >= record.max_attempts:
            return False, "Too many incorrect attempts. Please request a new OTP.", record

        now = datetime.now(timezone.utc)
        record_expiry = record.expires_at if record.expires_at.tzinfo else record.expires_at.replace(tzinfo=timezone.utc)
        if now > record_expiry:
            return False, "OTP has expired. Please request a new code.", record

        expected_hash = self.hash_otp(otp.strip(), normalized_email)
        is_valid = secrets.compare_digest(record.otp_hash, expected_hash)

        if not is_valid:
            attempts = await self.otp_repo.increment_attempt(record)
            if attempts >= record.max_attempts:
                return False, "Too many incorrect attempts. Please request a new OTP.", record
            remaining = record.max_attempts - attempts
            return False, f"Invalid verification code. {remaining} attempt(s) remaining.", record

        return True, "Verification code is valid.", record
