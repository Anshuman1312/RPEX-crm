from __future__ import annotations

import base64
from typing import Any

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from sqlalchemy import String
from sqlalchemy.types import TypeDecorator


# ── Encrypted string type ──────────────────────────────────────────────────────

class EncryptedString(TypeDecorator[str]):
    """
    AES-256 (Fernet) encrypted VARCHAR column type.

    Values are transparently encrypted on write and decrypted on read.
    Use for highly sensitive fields: Aadhaar number, passport, bank account, etc.

    The encryption key is derived from settings.FIELD_ENCRYPTION_KEY using
    PBKDF2-HMAC-SHA256 with a fixed salt. Rotate the key by running a
    one-time migration that re-encrypts all rows.
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
                iterations=480_000,         # OWASP recommended minimum for PBKDF2-SHA256
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
            # Log and return None rather than crashing — allows key rotation recovery
            from loguru import logger
            logger.warning("EncryptedString: decryption failed (possible key rotation mismatch)")
            return None
