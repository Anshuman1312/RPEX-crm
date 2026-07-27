"""
Notification models for in-app alerts and communication.

Models:
- Notification: Core notification entity
- NotificationPreference: User notification settings per channel/type
- NotificationTemplate: Reusable message templates
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    String, Integer, DateTime, ForeignKey, Boolean,
    Text, Enum as SQLEnum, Index, JSON
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.mixins import BaseModelMixin, PrimaryKeyMixin, TimestampMixin, SoftDeleteMixin
from app.database.base import Base
from app.utils.enums import NotificationType, NotificationChannel


class Notification(Base, BaseModelMixin, PrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """
    Notification sent to a user.

    Lifecycle: UNREAD → READ → ARCHIVED
    """
    __tablename__ = "notifications"

    # Recipient
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True
    )

    # Content
    type: Mapped[NotificationType] = mapped_column(
        SQLEnum(NotificationType), nullable=False, index=True
    )
    channel: Mapped[NotificationChannel] = mapped_column(
        SQLEnum(NotificationChannel), nullable=False, default=NotificationChannel.IN_APP
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)

    # Context reference (polymorphic)
    entity_type: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    entity_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True, index=True)

    # State
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Delivery tracking
    is_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    delivery_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Priority
    priority: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 0=Low, 1=Medium, 2=High, 3=Critical

    # Extra data (action URLs, deep-links, etc.)
    action_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    extra_data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], viewonly=True)

    __table_args__ = (
        Index("ix_notification_user_read", "user_id", "is_read"),
        Index("ix_notification_user_type", "user_id", "type"),
        Index("ix_notification_entity", "entity_type", "entity_id"),
    )


class NotificationPreference(Base, BaseModelMixin, PrimaryKeyMixin, TimestampMixin):
    """
    User notification preferences per type and channel.
    Controls which notifications a user wants and where.
    """
    __tablename__ = "notification_preferences"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True
    )

    # Notification type this preference applies to
    notification_type: Mapped[NotificationType] = mapped_column(
        SQLEnum(NotificationType), nullable=False
    )

    # Per-channel enable/disable
    in_app_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    email_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    sms_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    push_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    whatsapp_enabled: Mapped[bool] = mapped_column(Boolean, default=False)

    # Quiet hours (no notifications outside these hours)
    quiet_hours_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    quiet_hours_start: Mapped[int | None] = mapped_column(Integer, nullable=True)  # Hour 0-23
    quiet_hours_end: Mapped[int | None] = mapped_column(Integer, nullable=True)    # Hour 0-23

    # Frequency limits
    max_per_day: Mapped[int | None] = mapped_column(Integer, nullable=True)  # None = unlimited

    # Relationships
    user = relationship("User", foreign_keys=[user_id], viewonly=True)

    __table_args__ = (
        Index("ix_notif_pref_user_type", "user_id", "notification_type", unique=True),
    )


class NotificationTemplate(Base, BaseModelMixin, PrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """
    Reusable notification message template.
    Supports variable substitution: {{ lead_name }}, {{ booking_number }}, etc.
    """
    __tablename__ = "notification_templates"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    notification_type: Mapped[NotificationType] = mapped_column(
        SQLEnum(NotificationType), nullable=False, index=True
    )
    channel: Mapped[NotificationChannel] = mapped_column(
        SQLEnum(NotificationChannel), nullable=False
    )

    # Template content with variable placeholders
    title_template: Mapped[str] = mapped_column(String(255), nullable=False)
    body_template: Mapped[str] = mapped_column(Text, nullable=False)

    # Available variables documented
    variables: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
