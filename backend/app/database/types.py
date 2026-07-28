from __future__ import annotations

import base64
import uuid
from typing import Any

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from sqlalchemy import String, JSON, CHAR
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import TypeDecorator


# ── GUID / UUID Type ──────────────────────────────────────────────────────────

class GUID(TypeDecorator):
    """
    Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses CHAR(32), 
    storing as stringified hex values.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value: Any, dialect: Any) -> Any:
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                return "%.32x" % value.int

    def process_result_value(self, value: Any, dialect: Any) -> uuid.UUID | None:
        if value is None:
            return value
        if not isinstance(value, uuid.UUID):
            value = uuid.UUID(value)
        return value


# ── JSON Type Alias ───────────────────────────────────────────────────────────

# Maps JSONType used in models to SQLAlchemy's JSON type
JSONType = JSON


# ── Encrypted String Type ─────────────────────────────────────────────────────

class EncryptedString(TypeDecorator[str]):
    """
    AES-256 (Fernet) encrypted VARCHAR column type.
    """
    impl = String
    cache_ok = True

    _fernet: Fernet | None = None

    @classmethod
    def _get_fernet(cls) -> Fernet:
        if cls._fernet is None:
            from app.core.config import settings

            raw_key = settings.FIELD_ENCRYPTION_KEY.encode()
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b"rpex_crm_field_encryption_v1",
                iterations=480_000,
            )
            derived = base64.urlsafe_b64encode(kdf.derive(raw_key))
            cls._fernet = Fernet(derived)
        return cls._fernet

    def process_bind_param(self, value: str | None, dialect: Any) -> str | None:
        """Encrypt before persisting to the database."""
        if value is None:
            return None
        return self._get_fernet().encrypt(value.encode()).decode()

    def process_result_value(self, value: str | None, dialect: Any) -> str | None:
        """Decrypt after reading from the database."""
        if value is None:
            return None
        try:
            return self._get_fernet().decrypt(value.encode()).decode()
        except InvalidToken:
            from loguru import logger
            logger.warning("EncryptedString: decryption failed (possible key rotation mismatch)")
            return None