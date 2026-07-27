from __future__ import annotations

from typing import Optional

from sqlalchemy import String, Integer, Text, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.models.mixins import PrimaryKeyMixin, TimestampMixin


class SystemSetting(Base, PrimaryKeyMixin, TimestampMixin):
    """
    System-wide configuration and counters.

    Used for:
      - Sequential number counters (LEAD-000001, etc.)
      - Global configuration values
      - Feature flags
      - Rate limits
    """

    __tablename__ = "system_settings"

    # ── Primary key inherited from PrimaryKeyMixin ─────────────────────────────

    key: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    """Setting key (e.g., 'counter_LEAD', 'feature_whatsapp_enabled')"""

    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    """Human-readable description"""

    # ── Values (one will be non-null) ───────────────────────────────────────────

    str_value: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    """String value"""

    int_value: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    """Integer value (used for counters)"""

    float_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    """Float value"""

    bool_value: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    """Boolean value"""

    text_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    """Large text value (JSON configs, etc.)"""

    # ── Timestamps inherited from TimestampMixin ───────────────────────────────

    def __repr__(self) -> str:
        value = self.str_value or self.int_value or self.float_value or self.bool_value or self.text_value
        return f"<SystemSetting {self.key}={value}>"
