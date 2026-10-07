"""
STARTWISE AI — Auth Service
Production-ready business logic for authentication and account verification:
- Registration & OTP dispatch
- Email verification with attempt limiting & expiry
- Login with unverified account guard
- Resend OTP with 60s cooldown & rate limiting
- Forgot password with email enumeration protection
- Password reset OTP verification and token revocation
- Change password with current password validation
- Verification status checks
- DB Refresh Token rotation & logout
- Security Audit Logging
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    get_subject_from_token,
)
from app.core.exceptions import (
    ConflictException,
    UnauthorizedException,
    NotFoundException,
    BadRequestException,
    ForbiddenException,
    EmailNotVerifiedException,
)
from app.repositories.user_repository import UserRepository
from app.repositories.otp_repository import OTPRepository
from app.services.otp_service import OTPService
from app.services.email_service import email_service
from app.services.email_template_service import EmailTemplateService
from app.schemas.schemas import (
    UserRegister,
    TokenPair,
    UserOut,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    MessageResponse,
    VerifyEmailRequest,
    ResendOTPRequest,
    VerifyResetOTPRequest,
    ChangePasswordRequest,
    VerificationStatusResponse,
    AuthRegisterResponse,
)
from app.models.models import User, AuditLog
from app.core.logging import get_logger

logger = get_logger(__name__)


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.otp_repo = OTPRepository(db)
        self.otp_service = OTPService(db)

    async def _audit_log(
        self,
        action: str,
        user_id: Optional[UUID] = None,
        resource: str = "auth",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[dict] = None,
    ) -> None:
        """Record a security audit log event."""
        try:
            log = AuditLog(
                user_id=user_id,
                action=action,
                resource=resource,
                ip_address=ip_address,
                user_agent=user_agent,
                details=details or {},
            )
            self.db.add(log)
            await self.db.flush()
        except Exception as e:
            logger.warning(f"Failed to record audit log for action '{action}': {e}")

    async def register(
        self,
        payload: UserRegister,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuthRegisterResponse:
        """
        Register a new user account:
        1. Checks email uniqueness
        2. Creates account in unverified state (email_verified=False)
        3. Generates cryptographically secure 6-digit OTP
        4. Hashes and stores OTP in otp_verifications table
        5. Sends verification email via Resend email service
        6. Logs EMAIL_VERIFICATION_REQUESTED audit event
        7. Returns safe response indicating code was sent (never returns raw OTP)
        """
        normalized_email = payload.email.lower().strip()
        existing = await self.user_repo.get_by_email(normalized_email)
        if existing:
            raise ConflictException("An account with this email address already exists.")

        phone_val = payload.phone_number or payload.phone

        user = await self.user_repo.create(
            full_name=payload.full_name,
            email=normalized_email,
            hashed_password=hash_password(payload.password),
            phone=phone_val,
            is_active=True,
            is_verified=False,
        )
        # Ensure email_verified flag is explicitly False
        user.email_verified = False
        user.email_verified_at = None
        await self.db.flush()

        logger.info(f"New user registered in unverified state: {user.email} (ID: {user.id})")

        # Generate and dispatch OTP
        raw_otp, _ = await self.otp_service.create_otp(
            email=normalized_email,
            purpose="EMAIL_VERIFICATION",
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        subject, text_body, html_body = EmailTemplateService.get_verification_email(
            name=user.full_name,
            otp=raw_otp,
        )
        await email_service.send_email(
            to_email=user.email,
            subject=subject,
            text_content=text_body,
            html_content=html_body,
        )

        await self._audit_log(
            action="EMAIL_VERIFICATION_REQUESTED",
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
            details={"email": user.email, "purpose": "EMAIL_VERIFICATION"},
        )
        await self.db.commit()

        return AuthRegisterResponse(
            success=True,
            message="Verification code sent to your email.",
            email=user.email,
            requires_verification=True,
        )

    async def verify_email(
        self,
        payload: VerifyEmailRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> MessageResponse:
        """
        Verify account email with 6-digit OTP:
        1. Validates OTP attempt limit and expiration
        2. Compares secure hash in constant time
        3. Updates user email_verified=True, email_verified_at=now
        4. Marks OTP record as used
        5. Logs EMAIL_VERIFIED audit event
        """
        normalized_email = payload.email.lower().strip()
        is_valid, message, record = await self.otp_service.verify_otp(
            email=normalized_email,
            otp=payload.otp,
            purpose="EMAIL_VERIFICATION",
        )

        if not is_valid:
            action = "OTP_EXPIRED" if "expired" in message.lower() else "OTP_FAILED"
            await self._audit_log(
                action=action,
                user_id=record.user_id if record else None,
                ip_address=ip_address,
                user_agent=user_agent,
                details={"email": normalized_email, "reason": message},
            )
            await self.db.commit()
            raise BadRequestException(message)

        # Update user verification status
        user = await self.user_repo.get_by_email(normalized_email)
        if user:
            user.email_verified = True
            user.is_verified = True
            user.email_verified_at = datetime.now(timezone.utc)
            await self.db.flush()

        await self._audit_log(
            action="EMAIL_VERIFIED",
            user_id=user.id if user else (record.user_id if record else None),
            ip_address=ip_address,
            user_agent=user_agent,
            details={"email": normalized_email},
        )
        await self.db.commit()

        return MessageResponse(
            success=True,
            message="Email verified successfully.",
        )

    async def resend_otp(
        self,
        payload: ResendOTPRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> MessageResponse:
        """
        Resend OTP for email verification or password reset with cooldown & rate limit.
        Does not reveal if an arbitrary email is registered (enumeration prevention).
        """
        normalized_email = payload.email.lower().strip()
        user = await self.user_repo.get_by_email(normalized_email)

        if payload.purpose == "EMAIL_VERIFICATION":
            if not user or user.email_verified:
                # Return generic success to avoid enumeration
                return MessageResponse(
                    success=True,
                    message="If an account exists for this email, a verification code has been sent.",
                )

            raw_otp, _ = await self.otp_service.create_otp(
                email=user.email,
                purpose="EMAIL_VERIFICATION",
                user_id=user.id,
                ip_address=ip_address,
                user_agent=user_agent,
            )

            subject, text_body, html_body = EmailTemplateService.get_verification_email(
                name=user.full_name,
                otp=raw_otp,
            )
            await email_service.send_email(
                to_email=user.email,
                subject=subject,
                text_content=text_body,
                html_content=html_body,
            )

            await self._audit_log(
                action="EMAIL_VERIFICATION_REQUESTED",
                user_id=user.id,
                ip_address=ip_address,
                user_agent=user_agent,
                details={"email": user.email, "type": "resend"},
            )
            await self.db.commit()
            return MessageResponse(
                success=True,
                message="Verification code sent to your email.",
            )

        elif payload.purpose == "PASSWORD_RESET":
            return await self.forgot_password(
                ForgotPasswordRequest(email=normalized_email),
                ip_address=ip_address,
                user_agent=user_agent,
            )
        else:
            raise BadRequestException("Invalid OTP purpose.")

    async def login(self, email: str, password: str) -> TokenPair:
        """
        Authenticate credentials:
        - Validates credentials
        - Blocks unverified accounts with EMAIL_NOT_VERIFIED controlled response
        - Returns TokenPair for verified active users
        """
        normalized_email = email.lower().strip()
        user = await self.user_repo.get_by_email(normalized_email)

        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password.")

        if not user.is_active:
            raise UnauthorizedException("Account has been deactivated. Please contact support.")

        # Check account email verification status
        is_verified = getattr(user, "email_verified", False) or user.is_verified
        if not is_verified:
            logger.info(f"Login attempted for unverified account: {user.email}")
            # Try to send or ensure an OTP is available without throwing on cooldown
            try:
                raw_otp, _ = await self.otp_service.create_otp(
                    email=user.email,
                    purpose="EMAIL_VERIFICATION",
                    user_id=user.id,
                )
                subject, text_body, html_body = EmailTemplateService.get_verification_email(
                    name=user.full_name,
                    otp=raw_otp,
                )
                await email_service.send_email(
                    to_email=user.email,
                    subject=subject,
                    text_content=text_body,
                    html_content=html_body,
                )
                await self.db.commit()
            except Exception:
                pass  # Cooldown or rate limit active; allow redirect to /verify-email

            raise EmailNotVerifiedException(
                email=user.email,
                message="Email not verified. Please verify your email before logging in.",
            )

        access_token = create_access_token(
            subject=str(user.id),
            extra_claims={"role": user.role.value, "email": user.email},
        )
        refresh_token = create_refresh_token(subject=str(user.id))

        refresh_expiry = datetime.now(timezone.utc) + timedelta(days=7)
        await self.user_repo.save_refresh_token(
            user_id=user.id,
            token=refresh_token,
            expires_at=refresh_expiry,
        )

        logger.info(f"User logged in successfully: {user.email}")
        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=900,
        )

    async def refresh_access_token(self, refresh_token: str) -> TokenPair:
        """Exchange valid refresh token for a new access token & rotate refresh token."""
        db_token = await self.user_repo.get_refresh_token(refresh_token)
        if not db_token:
            raise UnauthorizedException("Refresh token is invalid, expired, or has been revoked.")

        user_id = get_subject_from_token(refresh_token, expected_type="refresh")
        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise UnauthorizedException("Invalid refresh token or inactive user.")

        # Revoke old refresh token (Token Rotation)
        await self.user_repo.revoke_refresh_token(refresh_token)

        # Issue new token pair
        new_access_token = create_access_token(
            subject=str(user.id),
            extra_claims={"role": user.role.value, "email": user.email},
        )
        new_refresh_token = create_refresh_token(subject=str(user.id))

        new_refresh_expiry = datetime.now(timezone.utc) + timedelta(days=7)
        await self.user_repo.save_refresh_token(
            user_id=user.id,
            token=new_refresh_token,
            expires_at=new_refresh_expiry,
        )

        logger.info(f"Token refreshed for user: {user.email}")
        return TokenPair(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=900,
        )

    async def logout(self, user_id: str, refresh_token: str | None = None) -> MessageResponse:
        """Revoke user's refresh token(s) upon logout."""
        if refresh_token:
            await self.user_repo.revoke_refresh_token(refresh_token)
        else:
            await self.user_repo.revoke_all_user_refresh_tokens(UserOut.id if hasattr(user_id, 'id') else user_id)
        logger.info(f"User logged out: {user_id}")
        return MessageResponse(message="Successfully logged out. Tokens have been revoked.", success=True)

    async def forgot_password(
        self,
        payload: ForgotPasswordRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> MessageResponse:
        """
        Request password reset OTP:
        - Prevents email enumeration: returns identical generic response whether email exists or not.
        - Generates 6-digit OTP, stores secure hash, and sends reset email.
        - Logs PASSWORD_RESET_REQUESTED audit event.
        """
        normalized_email = payload.email.lower().strip()
        user = await self.user_repo.get_by_email(normalized_email)

        # Return generic message to prevent email enumeration
        generic_response = MessageResponse(
            message="If an account exists for this email, a verification code has been sent.",
            success=True,
        )

        if not user:
            logger.info(f"Password reset requested for non-existent email: {normalized_email}")
            return generic_response

        raw_otp, _ = await self.otp_service.create_otp(
            email=user.email,
            purpose="PASSWORD_RESET",
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        subject, text_body, html_body = EmailTemplateService.get_password_reset_email(
            name=user.full_name,
            otp=raw_otp,
        )
        await email_service.send_email(
            to_email=user.email,
            subject=subject,
            text_content=text_body,
            html_content=html_body,
        )

        await self._audit_log(
            action="PASSWORD_RESET_REQUESTED",
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
            details={"email": user.email},
        )
        await self.db.commit()

        return generic_response

    async def verify_reset_otp(
        self,
        payload: VerifyResetOTPRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> MessageResponse:
        """Validate reset OTP code without consuming it immediately."""
        normalized_email = payload.email.lower().strip()
        is_valid, message, record = await self.otp_service.verify_otp_without_consuming(
            email=normalized_email,
            otp=payload.otp,
            purpose="PASSWORD_RESET",
        )
        if not is_valid:
            action = "OTP_EXPIRED" if "expired" in message.lower() else "OTP_FAILED"
            await self._audit_log(
                action=action,
                user_id=record.user_id if record else None,
                ip_address=ip_address,
                user_agent=user_agent,
                details={"email": normalized_email, "reason": message},
            )
            await self.db.commit()
            raise BadRequestException(message)

        return MessageResponse(
            success=True,
            message="Verification code is valid.",
        )

    async def reset_password(
        self,
        payload: ResetPasswordRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> MessageResponse:
        """
        Verify password reset OTP, hash and set new password,
        invalidate all reset OTPs and active refresh tokens,
        send security notification email, and record audit log.
        """
        otp_val = payload.otp or payload.otp_or_token or payload.token
        email_val = payload.email

        if not otp_val:
            raise BadRequestException("Reset OTP is required.")

        user: Optional[User] = None

        if email_val:
            normalized_email = email_val.lower().strip()
            is_valid, message, record = await self.otp_service.verify_otp(
                email=normalized_email,
                otp=otp_val,
                purpose="PASSWORD_RESET",
            )
            if not is_valid:
                action = "OTP_EXPIRED" if "expired" in message.lower() else "OTP_FAILED"
                await self._audit_log(
                    action=action,
                    user_id=record.user_id if record else None,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    details={"email": normalized_email, "reason": message},
                )
                await self.db.commit()
                raise BadRequestException(message)

            user = await self.user_repo.get_by_email(normalized_email)
        else:
            # Fallback legacy lookup via PasswordReset table
            reset_entry = await self.user_repo.get_valid_password_reset(otp_val)
            if not reset_entry:
                raise BadRequestException("Invalid or expired password reset token/OTP.")
            user = await self.user_repo.get_by_id(reset_entry.user_id)
            await self.user_repo.mark_password_reset_used(reset_entry)

        if not user:
            raise NotFoundException("User account not found.")

        # Update password hash
        user.hashed_password = hash_password(payload.new_password)

        # Invalidate all active password-reset OTPs for this user
        await self.otp_repo.invalidate_active_otps(user.email, "PASSWORD_RESET")

        # Invalidate all active refresh tokens for the user
        await self.user_repo.revoke_all_user_refresh_tokens(user.id)

        # Record audit log
        await self._audit_log(
            action="PASSWORD_RESET_COMPLETED",
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
            details={"email": user.email},
        )

        # Dispatch security notification email
        subj, txt, html = EmailTemplateService.get_password_changed_notification(name=user.full_name)
        await email_service.send_email(to_email=user.email, subject=subj, text_content=txt, html_content=html)

        await self.db.commit()
        logger.info(f"Password reset successfully completed for user: {user.email}")

        return MessageResponse(
            message="Password reset successfully.",
            success=True,
        )

    async def change_password(
        self,
        user: User,
        payload: ChangePasswordRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> MessageResponse:
        """
        Change password for an authenticated user:
        1. Verifies current password
        2. Validates strong new password != current password
        3. Updates password hash
        4. Revokes active refresh tokens
        5. Logs PASSWORD_CHANGED audit event
        6. Sends security alert email
        """
        if not verify_password(payload.current_password, user.hashed_password):
            raise BadRequestException("Current password is incorrect.")

        if verify_password(payload.new_password, user.hashed_password):
            raise BadRequestException("New password must be different from current password.")

        user.hashed_password = hash_password(payload.new_password)
        await self.user_repo.revoke_all_user_refresh_tokens(user.id)

        await self._audit_log(
            action="PASSWORD_CHANGED",
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
            details={"email": user.email},
        )

        subj, txt, html = EmailTemplateService.get_password_changed_notification(name=user.full_name)
        await email_service.send_email(to_email=user.email, subject=subj, text_content=txt, html_content=html)

        await self.db.commit()
        logger.info(f"Password changed for user: {user.email}")

        return MessageResponse(
            message="Password changed successfully.",
            success=True,
        )

    async def get_verification_status(self, email: str) -> VerificationStatusResponse:
        """Check verification status of an account."""
        user = await self.user_repo.get_by_email(email.lower().strip())
        if not user:
            return VerificationStatusResponse(email=email, email_verified=False, email_verified_at=None)

        is_verified = getattr(user, "email_verified", False) or user.is_verified
        return VerificationStatusResponse(
            email=user.email,
            email_verified=is_verified,
            email_verified_at=user.email_verified_at,
        )
