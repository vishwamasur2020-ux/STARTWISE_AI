"""
STARTWISE AI — JWT Security Utilities
Handles token creation, verification, and bcrypt password hashing.
"""

from datetime import datetime, timedelta, timezone
from typing import Any
import bcrypt
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.exceptions import UnauthorizedException


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Hash password securely using bcrypt with 72-byte safe truncation."""
    pwd_bytes = plain_password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against bcrypt hash with fallback."""
    try:
        pwd_bytes = plain_password.encode('utf-8')[:72]
        hash_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(pwd_bytes, hash_bytes)
    except Exception:
        return pwd_context.verify(plain_password, hashed_password)


# ─── Token Creation ──────────────────────────────────────────────────────────
def create_access_token(subject: Any, extra_claims: dict = {}) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
        **extra_claims,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(subject: Any) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh",
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


# ─── Token Verification ───────────────────────────────────────────────────────
def verify_token(token: str, expected_type: str = "access") -> dict:
    """Decode and validate a JWT. Raises UnauthorizedException on failure."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("type") != expected_type:
            raise UnauthorizedException("Invalid token type.")
        return payload
    except JWTError as e:
        raise UnauthorizedException(f"Token verification failed: {e}")


def get_subject_from_token(token: str, expected_type: str = "access") -> str:
    payload = verify_token(token, expected_type)
    sub = payload.get("sub")
    if not sub:
        raise UnauthorizedException("Token missing subject claim.")
    return sub
