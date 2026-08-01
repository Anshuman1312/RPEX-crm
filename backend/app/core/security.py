from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from jose import JWTError, ExpiredSignatureError, jwt

from app.core.config import settings


# ── Token exceptions ───────────────────────────────────────────────────────────

class TokenError(Exception):
    """Raised when a JWT token is invalid or expired."""
    pass

_PBKDF2_ITERATIONS = 29000
_PBKDF2_SALT_BYTES = 16


# ── Password utilities ─────────────────────────────────────────────────────────

def hash_password(plain_password: str) -> str:
    """Return a PBKDF2-SHA256 hash of the given plaintext password."""
    salt = secrets.token_bytes(_PBKDF2_SALT_BYTES)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        plain_password.encode("utf-8"),
        salt,
        _PBKDF2_ITERATIONS,
    )
    return f"pbkdf2_sha256${_PBKDF2_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify either a PBKDF2 hash or a legacy bcrypt hash."""
    if hashed_password.startswith("pbkdf2_sha256$"):
        try:
            _, iterations_text, salt_hex, digest_hex = hashed_password.split("$", 3)
            iterations = int(iterations_text)
            salt = bytes.fromhex(salt_hex)
            expected = bytes.fromhex(digest_hex)
            actual = hashlib.pbkdf2_hmac(
                "sha256",
                plain_password.encode("utf-8"),
                salt,
                iterations,
            )
            return hmac.compare_digest(actual, expected)
        except Exception:
            return False

    if hashed_password.startswith(("$2a$", "$2b$", "$2y$")):
        try:
            return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
        except Exception:
            return False

    return False


# ── JWT utilities ──────────────────────────────────────────────────────────────

def create_access_token(
    subject: str | Any,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """Create a short-lived JWT access token."""
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": str(subject),
        "iat": now,
        "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        "type": "access",
        "jti": secrets.token_hex(32),
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(subject: str | Any) -> str:
    """Create a long-lived JWT refresh token with a unique JTI for revocation."""
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": str(subject),
        "iat": now,
        "exp": now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        "type": "refresh",
        "jti": secrets.token_hex(32),   # unique identifier — stored in Redis for revocation
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a JWT access token.

    Raises:
        app.core.exceptions.TokenExpiredException: if the token has expired.
        app.core.exceptions.InvalidTokenException: if the token is invalid.
    """
    from app.core.exceptions import TokenExpiredException, InvalidTokenException

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "access":
            raise InvalidTokenException()
        return payload
    except ExpiredSignatureError:
        raise TokenExpiredException()
    except JWTError:
        raise InvalidTokenException()


def decode_refresh_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a JWT refresh token.

    Raises:
        app.core.exceptions.TokenExpiredException: if the token has expired.
        app.core.exceptions.InvalidTokenException: if the token is invalid.
    """
    from app.core.exceptions import TokenExpiredException, InvalidTokenException

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            raise InvalidTokenException()
        return payload
    except ExpiredSignatureError:
        raise TokenExpiredException()
    except JWTError:
        raise InvalidTokenException()


# ── Token storage helpers ──────────────────────────────────────────────────────

def hash_token(token: str) -> str:
    """SHA-256 hash of a token — safe to store in the database."""
    return hashlib.sha256(token.encode()).hexdigest()


def generate_secure_token(nbytes: int = 32) -> str:
    """Cryptographically secure URL-safe random token (e.g. for password reset)."""
    return secrets.token_urlsafe(nbytes)


def generate_otp(length: int = 6) -> str:
    """Cryptographically secure numeric OTP."""
    return "".join(str(secrets.randbelow(10)) for _ in range(length))


# ── Unified decode (used by deps.py / main-branch auth) ───────────────────────

def decode_token(token: str) -> dict[str, Any]:
    """
    Decode and validate any JWT token (access or refresh).

    Raises:
        TokenError: if the token is invalid or expired.
    """
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError as exc:
        raise TokenError("Invalid or expired token") from exc
