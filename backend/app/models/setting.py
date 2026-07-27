"""
System settings and role/permission management models.

Uses existing SystemSetting model (app/models/system.py).
This module adds Role and Permission management APIs.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import String, Boolean, Text, Index, ForeignKey, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.mixins import BaseModelMixin, PrimaryKeyMixin, TimestampMixin
from app.database.base import Base


class AppSetting(Base, BaseModelMixin, PrimaryKeyMixin, TimestampMixin):
    """
    Application-level configuration settings (key-value store).

    Extends the existing SystemSetting with categories and UI metadata.
    """
    __tablename__ = "app_settings"

    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True, default="general")

    # Value fields (only one used per setting)
    value_string: Mapped[str | None] = mapped_column(Text, nullable=True)
    value_int: Mapped[int | None] = mapped_column(Integer, nullable=True)
    value_bool: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    value_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Metadata
    data_type: Mapped[str] = mapped_column(String(20), nullable=False, default="string")  # string, int, bool, json
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_sensitive: Mapped[bool] = mapped_column(Boolean, default=False)   # mask in API output
    is_readonly: Mapped[bool] = mapped_column(Boolean, default=False)    # cannot be edited via API

    # Updated by tracking
    updated_by_user_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    __table_args__ = (
        Index("ix_app_setting_category", "category"),
    )


class UserSetting(Base, BaseModelMixin, PrimaryKeyMixin, TimestampMixin):
    """
    Per-user configuration preferences.
    """
    __tablename__ = "user_settings"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    key: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], viewonly=True)

    __table_args__ = (
        Index("ix_user_setting_user_key", "user_id", "key", unique=True),
    )
