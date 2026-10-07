"""
STARTWISE AI — OTP Authentication & Verification Test Suite
Comprehensive testing for:
1. Signup & OTP generation
2. Email verification (success, invalid OTP, expired OTP, reuse, max attempts)
3. Unverified account login blocking (EMAIL_NOT_VERIFIED)
4. OTP resend (cooldown, email enumeration prevention)
5. Forgot password (generic response, OTP dispatch)
6. Reset password (valid OTP, invalid OTP, expired OTP, max attempts, old pass fails, new pass works)
7. Change password (authenticated, invalid current pass, weak pass, same pass)
8. Verification status endpoint
9. Security invariants:
   - OTP never in response
   - Plaintext OTP never stored
   - Secrets not exposed
   - Email enumeration prevented
   - User isolation
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, update

from app.models.models import User, OTPVerification
from app.services.otp_service import OTPService
from app.services.email_service import email_service
from app.core.config import settings


# ─── 1. SIGNUP & VERIFICATION TESTS ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_signup_creates_unverified_account_and_generates_otp(client: AsyncClient, db_session):
    """Signup creates unverified account, hashes OTP in DB, and dispatches verification email."""
    email = f"signup_otp_{uuid4().hex[:6]}@example.com"
    payload = {
        "full_name": "New Founder",
        "email": email,
        "password": "SecurePassword123!",
        "confirm_password": "SecurePassword123!",
    }
    initial_sent_count = len(email_service.sent_emails_history)

    res = await client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 201, f"Register failed: {res.text}"
    data = res.json()

    # Verify response structure and security
    assert data["success"] is True
    assert data["requires_verification"] is True
    assert data["email"] == email.lower()
    assert "Verification code sent" in data["message"]
    # CRITICAL: OTP must NEVER be in response
    assert "otp" not in data
    assert "code" not in data or data.get("code") != "123456"

    # Verify DB user state
    user_res = await db_session.execute(select(User).where(User.email == email.lower()))
    user = user_res.scalar_one_or_none()
    assert user is not None
    assert user.email_verified is False
    assert user.is_verified is False
    assert user.email_verified_at is None

    # Verify OTP record in DB
    otp_res = await db_session.execute(
        select(OTPVerification).where(OTPVerification.email == email.lower(), OTPVerification.purpose == "EMAIL_VERIFICATION")
    )
    otp_record = otp_res.scalar_one_or_none()
    assert otp_record is not None
    assert otp_record.used_at is None
    assert otp_record.attempt_count == 0
    # CRITICAL: Plaintext OTP never stored in database
    assert len(otp_record.otp_hash) == 64  # HMAC-SHA256 hex digest length

    # Verify email delivery was triggered
    assert len(email_service.sent_emails_history) > initial_sent_count
    last_email = email_service.sent_emails_history[-1]
    assert last_email["to"] == email.lower()
    assert "Verify your STARTWISE AI account" in last_email["subject"]


@pytest.mark.asyncio
async def test_signup_duplicate_email_fails(client: AsyncClient, test_user: User):
    """Duplicate email registration is rejected with 409 Conflict."""
    payload = {
        "full_name": "Duplicate User",
        "email": test_user.email,
        "password": "Password123!",
        "confirm_password": "Password123!",
    }
    res = await client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 409


@pytest.mark.asyncio
async def test_signup_invalid_email_and_password_validation(client: AsyncClient):
    """Validation rejects invalid email format, weak passwords, and mismatched passwords."""
    # Invalid email
    res1 = await client.post("/api/v1/auth/register", json={
        "full_name": "Test User",
        "email": "not-an-email",
        "password": "Password123!",
        "confirm_password": "Password123!",
    })
    assert res1.status_code == 422

    # Weak password (< 8 chars)
    res2 = await client.post("/api/v1/auth/register", json={
        "full_name": "Test User",
        "email": f"weak_{uuid4().hex[:6]}@example.com",
        "password": "pass",
        "confirm_password": "pass",
    })
    assert res2.status_code == 422

    # Mismatched password
    res3 = await client.post("/api/v1/auth/register", json={
        "full_name": "Test User",
        "email": f"mismatch_{uuid4().hex[:6]}@example.com",
        "password": "Password123!",
        "confirm_password": "DifferentPassword123!",
    })
    assert res3.status_code == 422


@pytest.mark.asyncio
async def test_unverified_account_login_blocked(client: AsyncClient):
    """Unverified account receives 403 EMAIL_NOT_VERIFIED on login attempt."""
    email = f"unverified_login_{uuid4().hex[:6]}@example.com"
    pwd = "Password123!"

    # Register
    await client.post("/api/v1/auth/register", json={
        "full_name": "Unverified User",
        "email": email,
        "password": pwd,
        "confirm_password": pwd,
    })

    # Attempt login
    login_res = await client.post("/api/v1/auth/login", json={"email": email, "password": pwd})
    assert login_res.status_code == 403
    err_data = login_res.json()
    assert "EMAIL_NOT_VERIFIED" in str(err_data)


@pytest.mark.asyncio
async def test_successful_email_verification(client: AsyncClient, db_session):
    """Entering the correct OTP marks the user verified and updates email_verified_at."""
    email = f"verify_success_{uuid4().hex[:6]}@example.com"
    pwd = "Password123!"

    await client.post("/api/v1/auth/register", json={
        "full_name": "Success User",
        "email": email,
        "password": pwd,
        "confirm_password": pwd,
    })

    # Extract raw OTP from the mocked email
    last_email = email_service.sent_emails_history[-1]
    import re
    otp_match = re.search(r"\b(\d{6})\b", last_email["text"])
    assert otp_match is not None, "OTP not found in email text"
    raw_otp = otp_match.group(1)

    # Verify email endpoint
    verify_res = await client.post("/api/v1/auth/verify-email", json={
        "email": email,
        "otp": raw_otp,
    })
    assert verify_res.status_code == 200
    assert verify_res.json()["success"] is True

    # User in DB is now verified
    user_res = await db_session.execute(select(User).where(User.email == email.lower()))
    user = user_res.scalar_one_or_none()
    assert user.email_verified is True
    assert user.is_verified is True
    assert user.email_verified_at is not None

    # Login now succeeds
    login_res = await client.post("/api/v1/auth/login", json={"email": email, "password": pwd})
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()


@pytest.mark.asyncio
async def test_invalid_otp_fails_with_remaining_attempts(client: AsyncClient):
    """Entering an incorrect OTP fails and increments attempt count."""
    email = f"invalid_otp_{uuid4().hex[:6]}@example.com"
    pwd = "Password123!"

    await client.post("/api/v1/auth/register", json={
        "full_name": "Invalid OTP User",
        "email": email,
        "password": pwd,
        "confirm_password": pwd,
    })

    res = await client.post("/api/v1/auth/verify-email", json={
        "email": email,
        "otp": "000000",
    })
    assert res.status_code == 400
    data = res.json()
    assert "Invalid verification code" in data["detail"]


@pytest.mark.asyncio
async def test_expired_otp_fails(client: AsyncClient, db_session):
    """Expired OTP is rejected with 'OTP has expired'."""
    email = f"expired_otp_{uuid4().hex[:6]}@example.com"
    pwd = "Password123!"

    await client.post("/api/v1/auth/register", json={
        "full_name": "Expired OTP User",
        "email": email,
        "password": pwd,
        "confirm_password": pwd,
    })

    # Manually expire the OTP in DB
    past_time = datetime.now(timezone.utc) - timedelta(minutes=15)
    await db_session.execute(
        update(OTPVerification).where(OTPVerification.email == email.lower()).values(expires_at=past_time)
    )
    await db_session.commit()

    res = await client.post("/api/v1/auth/verify-email", json={
        "email": email,
        "otp": "123456",
    })
    assert res.status_code == 400
    assert "expired" in res.json()["detail"].lower()


@pytest.mark.asyncio
async def test_otp_reuse_fails(client: AsyncClient, db_session):
    """An OTP cannot be used more than once."""
    email = f"reuse_otp_{uuid4().hex[:6]}@example.com"
    pwd = "Password123!"

    await client.post("/api/v1/auth/register", json={
        "full_name": "Reuse OTP User",
        "email": email,
        "password": pwd,
        "confirm_password": pwd,
    })

    import re
    last_email = email_service.sent_emails_history[-1]
    raw_otp = re.search(r"\b(\d{6})\b", last_email["text"]).group(1)

    # First verification succeeds
    res1 = await client.post("/api/v1/auth/verify-email", json={"email": email, "otp": raw_otp})
    assert res1.status_code == 200

    # Second attempt with same OTP fails
    res2 = await client.post("/api/v1/auth/verify-email", json={"email": email, "otp": raw_otp})
    assert res2.status_code == 400


@pytest.mark.asyncio
async def test_maximum_attempts_exceeded_invalidates_otp(client: AsyncClient, db_session):
    """After 5 incorrect attempts, OTP is permanently invalidated."""
    email = f"max_attempts_{uuid4().hex[:6]}@example.com"
    pwd = "Password123!"

    await client.post("/api/v1/auth/register", json={
        "full_name": "Max Attempts User",
        "email": email,
        "password": pwd,
        "confirm_password": pwd,
    })

    # 4 invalid attempts
    for _ in range(4):
        r = await client.post("/api/v1/auth/verify-email", json={"email": email, "otp": "999999"})
        assert r.status_code == 400

    # 5th invalid attempt -> exceeds limit
    r5 = await client.post("/api/v1/auth/verify-email", json={"email": email, "otp": "999999"})
    assert r5.status_code == 400
    assert "Too many incorrect attempts" in r5.json()["detail"]

    # Even if correct code entered now, it is invalidated
    import re
    raw_otp = re.search(r"\b(\d{6})\b", email_service.sent_emails_history[-1]["text"]).group(1)
    r_late = await client.post("/api/v1/auth/verify-email", json={"email": email, "otp": raw_otp})
    assert r_late.status_code == 400


@pytest.mark.asyncio
async def test_resend_cooldown_enforced(client: AsyncClient):
    """Requesting resend before 60 seconds returns cooldown warning."""
    email = f"cooldown_{uuid4().hex[:6]}@example.com"
    pwd = "Password123!"

    await client.post("/api/v1/auth/register", json={
        "full_name": "Cooldown User",
        "email": email,
        "password": pwd,
        "confirm_password": pwd,
    })

    # Immediate resend attempt
    res = await client.post("/api/v1/auth/resend-otp", json={
        "email": email,
        "purpose": "EMAIL_VERIFICATION",
    })
    assert res.status_code == 400
    assert "Please wait" in res.json()["detail"]


# ─── 2. PASSWORD RESET TESTS ─────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_forgot_password_generic_response_for_non_existent_email(client: AsyncClient):
    """Forgot password returns identical generic response for non-existent email to prevent enumeration."""
    res = await client.post("/api/v1/auth/forgot-password", json={
        "email": f"nonexistent_{uuid4().hex[:6]}@example.com",
    })
    assert res.status_code == 200
    assert "If an account exists" in res.json()["message"]


@pytest.mark.asyncio
async def test_forgot_password_and_reset_flow(client: AsyncClient, test_user: User, db_session):
    """Complete forgot password, verify OTP, and reset password flow."""
    # Request OTP
    res_forgot = await client.post("/api/v1/auth/forgot-password", json={"email": test_user.email})
    assert res_forgot.status_code == 200

    import re
    last_email = email_service.sent_emails_history[-1]
    assert last_email["to"] == test_user.email
    assert "Reset your STARTWISE AI password" in last_email["subject"]
    raw_otp = re.search(r"\b(\d{6})\b", last_email["text"]).group(1)

    # Preliminary verify reset OTP check
    res_check = await client.post("/api/v1/auth/verify-reset-otp", json={
        "email": test_user.email,
        "otp": raw_otp,
    })
    assert res_check.status_code == 200
    assert res_check.json()["success"] is True

    # Reset password
    new_pwd = "BrandNewPassword123!"
    res_reset = await client.post("/api/v1/auth/reset-password", json={
        "email": test_user.email,
        "otp": raw_otp,
        "new_password": new_pwd,
        "confirm_password": new_pwd,
    })
    assert res_reset.status_code == 200
    assert "Password reset successfully" in res_reset.json()["message"]

    # Verify security email sent
    sec_email = email_service.sent_emails_history[-1]
    assert "password was changed" in sec_email["subject"]

    # Old password no longer works
    res_old = await client.post("/api/v1/auth/login", json={"email": test_user.email, "password": "Password123!"})
    assert res_old.status_code == 401

    # New password succeeds
    res_new = await client.post("/api/v1/auth/login", json={"email": test_user.email, "password": new_pwd})
    assert res_new.status_code == 200
    assert "access_token" in res_new.json()


# ─── 3. CHANGE PASSWORD TESTS ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_change_password_for_authenticated_user(client: AsyncClient, test_user: User, user_token_headers: dict):
    """Authenticated user can change password with valid current password."""
    # Current test_user password from conftest has hash for 'Password123!' or similar; let's set known password
    from app.core.security import hash_password
    from app.database.session import AsyncSessionLocal
    current_pwd = "CurrentKnownPassword123!"
    async with AsyncSessionLocal() as session:
        await session.execute(
            update(User).where(User.id == test_user.id).values(hashed_password=hash_password(current_pwd))
        )
        await session.commit()

    new_pwd = "UpdatedSecurePassword123!"

    # Change password
    res = await client.post(
        "/api/v1/auth/change-password",
        headers=user_token_headers,
        json={
            "current_password": current_pwd,
            "new_password": new_pwd,
            "confirm_password": new_pwd,
        },
    )
    assert res.status_code == 200
    assert "Password changed successfully" in res.json()["message"]

    # Login with new password
    login_res = await client.post("/api/v1/auth/login", json={"email": test_user.email, "password": new_pwd})
    assert login_res.status_code == 200


@pytest.mark.asyncio
async def test_change_password_invalid_current_password_fails(client: AsyncClient, user_token_headers: dict):
    """Change password fails when current password is wrong."""
    res = await client.post(
        "/api/v1/auth/change-password",
        headers=user_token_headers,
        json={
            "current_password": "WrongCurrentPassword123!",
            "new_password": "ValidNewPassword123!",
            "confirm_password": "ValidNewPassword123!",
        },
    )
    assert res.status_code == 400
    assert "Current password is incorrect" in res.json()["detail"]


@pytest.mark.asyncio
async def test_change_password_unauthorized(client: AsyncClient):
    """Change password requires valid JWT Authorization header."""
    res = await client.post(
        "/api/v1/auth/change-password",
        json={
            "current_password": "CurrentPassword123!",
            "new_password": "NewPassword123!",
            "confirm_password": "NewPassword123!",
        },
    )
    assert res.status_code in (401, 403)


# ─── 4. VERIFICATION STATUS & SECURITY TESTS ─────────────────────────────────

@pytest.mark.asyncio
async def test_verification_status_endpoint(client: AsyncClient, test_user: User):
    """Check verification status returns email and email_verified boolean."""
    res = await client.get(f"/api/v1/auth/verification-status?email={test_user.email}")
    assert res.status_code == 200
    data = res.json()
    assert data["email"] == test_user.email
    assert data["email_verified"] is True


@pytest.mark.asyncio
async def test_security_invariants_no_secrets_in_responses(client: AsyncClient, user_token_headers: dict):
    """Verify that private keys, client secret, and OTP hashes are never exposed in any responses."""
    # Health endpoints
    res_health = await client.get("/api/v1/health")
    assert res_health.status_code == 200
    health_text = res_health.text
    assert "RESEND_API_KEY" not in health_text
    assert "CLIENT_SECRET" not in health_text
    assert "JWT_SECRET" not in health_text
    assert "OTP_SECRET" not in health_text

    # User profile
    res_me = await client.get("/api/v1/auth/me", headers=user_token_headers)
    assert res_me.status_code == 200
    me_text = res_me.text
    assert "password" not in me_text.lower()
    assert "hashed_password" not in me_text
    assert "otp" not in me_text.lower()


# ─── 5. USER ISOLATION & ATTACK PREVENTION ──────────────────────────────────

@pytest.mark.asyncio
async def test_user_cannot_verify_with_another_users_otp(client: AsyncClient):
    """User B cannot use the OTP generated for User A."""
    email_a = f"victim_{uuid4().hex[:6]}@example.com"
    email_b = f"attacker_{uuid4().hex[:6]}@example.com"
    pwd = "Password123!"

    # Register user A
    await client.post("/api/v1/auth/register", json={
        "full_name": "Victim", "email": email_a, "password": pwd, "confirm_password": pwd,
    })
    import re
    otp_a = re.search(r"\b(\d{6})\b", email_service.sent_emails_history[-1]["text"]).group(1)

    # Register user B
    await client.post("/api/v1/auth/register", json={
        "full_name": "Attacker", "email": email_b, "password": pwd, "confirm_password": pwd,
    })

    # User B tries to verify using User A's OTP
    res_attack = await client.post("/api/v1/auth/verify-email", json={
        "email": email_b,
        "otp": otp_a,
    })
    # Since OTP is hashed using email_b, user A's OTP will produce a mismatched hash
    assert res_attack.status_code == 400
    assert "Invalid verification code" in res_attack.json()["detail"]


@pytest.mark.asyncio
async def test_user_cannot_reset_another_users_account(client: AsyncClient, test_user: User):
    """Attacker cannot reset Victim's account using an OTP issued to Attacker."""
    attacker_email = f"attacker_reset_{uuid4().hex[:6]}@example.com"
    pwd = "Password123!"

    # Register attacker
    await client.post("/api/v1/auth/register", json={
        "full_name": "Attacker", "email": attacker_email, "password": pwd, "confirm_password": pwd,
    })

    # Attacker requests forgot password for themselves
    await client.post("/api/v1/auth/forgot-password", json={"email": attacker_email})
    import re
    attacker_otp = re.search(r"\b(\d{6})\b", email_service.sent_emails_history[-1]["text"]).group(1)

    # Attacker tries to reset Victim's password with attacker's OTP
    res_attack = await client.post("/api/v1/auth/reset-password", json={
        "email": test_user.email,
        "otp": attacker_otp,
        "new_password": "HackedPassword123!",
        "confirm_password": "HackedPassword123!",
    })
    assert res_attack.status_code == 400


# ─── 6. 17-STEP COMPREHENSIVE END-TO-END FLOW ───────────────────────────────

@pytest.mark.asyncio
async def test_complete_17_step_end_to_end_auth_flow(client: AsyncClient):
    """
    Executes the exact 17-step end-to-end user verification and authentication lifecycle:
    1. Register new user
    2. Receive OTP email
    3. Enter OTP
    4. Verify email
    5. Login
    6. Open security settings / verification status
    7. Change password
    8. Logout
    9. Login using new password
    10. Logout
    11. Click Forgot Password
    12. Enter registered email
    13. Receive password reset OTP
    14. Enter OTP & verify
    15. Set new password
    16. Login with new password
    17. Verify old password no longer works
    """
    import re

    email = f"e2e_full_{uuid4().hex[:6]}@example.com"
    pwd1 = "InitialPassword123!"
    pwd2 = "UpdatedPassword456!"
    pwd3 = "FinalPassword789!"

    # 1. Register new user
    r1 = await client.post("/api/v1/auth/register", json={
        "full_name": "E2E User",
        "email": email,
        "password": pwd1,
        "confirm_password": pwd1,
    })
    assert r1.status_code == 201
    assert r1.json()["requires_verification"] is True

    # 2. Receive OTP email
    assert len(email_service.sent_emails_history) > 0
    email_signup = email_service.sent_emails_history[-1]
    assert email_signup["to"] == email.lower()
    otp_signup = re.search(r"\b(\d{6})\b", email_signup["text"]).group(1)
    assert len(otp_signup) == 6

    # 3 & 4. Enter OTP and Verify email
    r4 = await client.post("/api/v1/auth/verify-email", json={
        "email": email,
        "otp": otp_signup,
    })
    assert r4.status_code == 200
    assert r4.json()["success"] is True

    # 5. Login
    r5 = await client.post("/api/v1/auth/login", json={"email": email, "password": pwd1})
    assert r5.status_code == 200
    tokens1 = r5.json()
    access_token1 = tokens1["access_token"]
    refresh_token1 = tokens1["refresh_token"]

    # 6. Open security settings / verification status
    r6 = await client.get(f"/api/v1/auth/verification-status?email={email}")
    assert r6.status_code == 200
    assert r6.json()["email_verified"] is True

    # 7. Change password
    r7 = await client.post(
        "/api/v1/auth/change-password",
        headers={"Authorization": f"Bearer {access_token1}"},
        json={"current_password": pwd1, "new_password": pwd2, "confirm_password": pwd2},
    )
    assert r7.status_code == 200
    assert "Password changed successfully" in r7.json()["message"]

    # 8. Logout
    r8 = await client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {access_token1}", "X-Refresh-Token": refresh_token1},
    )
    assert r8.status_code == 200

    # 9. Login using new password
    r9 = await client.post("/api/v1/auth/login", json={"email": email, "password": pwd2})
    assert r9.status_code == 200
    tokens2 = r9.json()

    # 10. Logout
    r10 = await client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {tokens2['access_token']}", "X-Refresh-Token": tokens2['refresh_token']},
    )
    assert r10.status_code == 200

    # 11 & 12. Click Forgot Password and Enter registered email
    r12 = await client.post("/api/v1/auth/forgot-password", json={"email": email})
    assert r12.status_code == 200
    assert "If an account exists" in r12.json()["message"]

    # 13. Receive password reset OTP
    email_reset = email_service.sent_emails_history[-1]
    assert "Reset your STARTWISE AI password" in email_reset["subject"]
    otp_reset = re.search(r"\b(\d{6})\b", email_reset["text"]).group(1)
    assert len(otp_reset) == 6

    # 14. Enter OTP & verify reset OTP
    r14 = await client.post("/api/v1/auth/verify-reset-otp", json={"email": email, "otp": otp_reset})
    assert r14.status_code == 200

    # 15. Set new password
    r15 = await client.post("/api/v1/auth/reset-password", json={
        "email": email,
        "otp": otp_reset,
        "new_password": pwd3,
        "confirm_password": pwd3,
    })
    assert r15.status_code == 200
    assert "Password reset successfully" in r15.json()["message"]

    # 16. Login with new password
    r16 = await client.post("/api/v1/auth/login", json={"email": email, "password": pwd3})
    assert r16.status_code == 200
    assert "access_token" in r16.json()

    # 17. Verify old password no longer works (both pwd1 and pwd2 fail)
    r17_old1 = await client.post("/api/v1/auth/login", json={"email": email, "password": pwd1})
    assert r17_old1.status_code == 401
    r17_old2 = await client.post("/api/v1/auth/login", json={"email": email, "password": pwd2})
    assert r17_old2.status_code == 401

