"""
Follow-up and Activity models for lead management lifecycle.

Models:
- FollowUp: Scheduled follow-ups with lead, customer, assigned user
- FollowUpTask: Sub-tasks within follow-ups (call, email, meeting, site visit)
- FollowUpOutcome: Result tracking and notes
- FollowUpAttachment: Attachments for follow-ups
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    String, Integer, DateTime, ForeignKey, Boolean,
    Text, Enum as SQLEnum, Index, Numeric, JSON
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.mixins import BaseModelMixin, PrimaryKeyMixin, TimestampMixin, SoftDeleteMixin
from app.database.base import Base
from app.utils.enums import (
    FollowUpStatus, FollowUpType, FollowUpOutcomeType,
    FollowUpTaskStatus, FollowUpTaskType
)


class FollowUp(Base, BaseModelMixin, PrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """
    Scheduled follow-up with lead or customer.
    
    Status machine: SCHEDULED → COMPLETED/CANCELLED/OVERDUE
    """
    __tablename__ = "followups"

    followup_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    """Auto-generated follow-up ID (e.g., FOLUP-000001)"""
    
    # References
    lead_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("leads.id", ondelete="CASCADE"), nullable=True, index=True)
    customer_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=True, index=True)
    assigned_to_user_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    created_by_user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    
    # Follow-up details
    type: Mapped[FollowUpType] = mapped_column(SQLEnum(FollowUpType), nullable=False, index=True)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Status tracking
    status: Mapped[FollowUpStatus] = mapped_column(
        SQLEnum(FollowUpStatus),
        nullable=False,
        default=FollowUpStatus.SCHEDULED,
        index=True
    )
    
    # Priority and flags
    priority: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_critical: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Attachments and links
    attachments_urls: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    
    # Relationships
    lead = relationship("Lead", back_populates="followups", foreign_keys=[lead_id])
    customer = relationship("Customer", back_populates="followups", foreign_keys=[customer_id])
    assigned_to = relationship("User", foreign_keys=[assigned_to_user_id], viewonly=True)
    created_by = relationship("User", foreign_keys=[created_by_user_id], viewonly=True)
    tasks = relationship("FollowUpTask", back_populates="followup", cascade="all, delete-orphan")
    outcomes = relationship("FollowUpOutcome", back_populates="followup", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("ix_followup_lead_scheduled", "lead_id", "scheduled_at"),
        Index("ix_followup_customer_scheduled", "customer_id", "scheduled_at"),
        Index("ix_followup_assigned_status", "assigned_to_user_id", "status"),
    )


class FollowUpTask(Base, BaseModelMixin, PrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """
    Task/activity within a follow-up.
    
    Status machine: PENDING → COMPLETED/CANCELLED/SKIPPED
    """
    __tablename__ = "followup_tasks"

    followup_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("followups.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Task details
    task_type: Mapped[FollowUpTaskType] = mapped_column(SQLEnum(FollowUpTaskType), nullable=False)
    task_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Status and timing
    status: Mapped[FollowUpTaskStatus] = mapped_column(
        SQLEnum(FollowUpTaskStatus),
        nullable=False,
        default=FollowUpTaskStatus.PENDING,
        index=True
    )
    
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Notes and result
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Flags
    is_required: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    followup = relationship("FollowUp", back_populates="tasks", viewonly=True)
    
    __table_args__ = (
        Index("ix_followup_task_followup_type", "followup_id", "task_type"),
        Index("ix_followup_task_status", "status"),
    )


class FollowUpOutcome(Base, BaseModelMixin, PrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """
    Outcome/result of a follow-up.
    
    Tracks: next step, conversion, lost reason, deal value, timeline
    """
    __tablename__ = "followup_outcomes"

    followup_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("followups.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Outcome classification
    outcome_type: Mapped[FollowUpOutcomeType] = mapped_column(
        SQLEnum(FollowUpOutcomeType),
        nullable=False,
        index=True
    )
    
    # Result details
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    next_step: Mapped[str | None] = mapped_column(Text, nullable=True)
    next_followup_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Deal tracking (optional)
    estimated_deal_value: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    conversion_probability: Mapped[int | None] = mapped_column(Integer, nullable=True)
    lost_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    # Reference to projects or units discussed
    discussed_projects: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    discussed_units: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    
    # Recorded by
    recorded_by_user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    followup = relationship("FollowUp", back_populates="outcomes", viewonly=True)
    recorded_by = relationship("User", foreign_keys=[recorded_by_user_id], viewonly=True)


class FollowUpAttachment(Base, BaseModelMixin, PrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """
    Attachment associated with a follow-up.
    """
    __tablename__ = "followup_attachments"

    followup_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("followups.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # File details
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_url: Mapped[str] = mapped_column(Text, nullable=False)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    # Metadata
    uploaded_by_user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Relationships
    uploaded_by = relationship("User", foreign_keys=[uploaded_by_user_id], viewonly=True)
