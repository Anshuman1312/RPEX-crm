"""
Audit log model — immutable record of all significant system events.

AuditLog entries are never updated or deleted; they form a tamper-evident trail.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import String, Text, Index, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.mixins import PrimaryKeyMixin
from app.database.base import Base


class AuditLog(Base, PrimaryKeyMixin):
    """
    Immutable audit log entry.

    No soft-delete, no updated_at — records are write-once.
    Captures: WHO did WHAT to WHICH entity, WHEN and from WHERE.
    """
    __tablename__ = "audit_logs"

    # When
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, index=True
    )

    # Who
    user_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True, index=True
    )
    user_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    user_role: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # What
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    # e.g. "lead.created", "booking.status_changed", "user.login", "invoice.sent"

    # Which entity
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    entity_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True, index=True)
    entity_display: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Human-readable identifier (e.g. "LEAD-000123", "John Smith")

    # Change details
    description: Mapped[str] = mapped_column(Text, nullable=False)
    old_value: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    new_value: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    changes: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    # changes = {"field": {"from": old, "to": new}, ...}

    # Where / context
    ip_address: Mapped[str | None] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    correlation_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    request_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    request_method: Mapped[str | None] = mapped_column(String(10), nullable=True)

    # Outcome
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="success", index=True)
    # "success", "failure", "warning"
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Extra metadata
    extra_data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    __table_args__ = (
        Index("ix_audit_entity", "entity_type", "entity_id"),
        Index("ix_audit_user_action", "user_id", "action"),
        Index("ix_audit_created_action", "created_at", "action"),
    )
