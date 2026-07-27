"""
Task and Activity models for workflow and project management.

Models:
- Task: Main task entity with status, priority, due dates
- TaskChecklist: Sub-checklist items within tasks
- TaskComment: Comments and notes on tasks
- TaskAttachment: File attachments for tasks
- Activity: General activity log for system events
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import (
    String, Integer, DateTime, ForeignKey, Boolean,
    Text, Enum as SQLEnum, Index, Numeric, JSON
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.mixins import BaseModelMixin, PrimaryKeyMixin, TimestampMixin, SoftDeleteMixin
from app.database.base import Base
from app.utils.enums import TaskStatus, TaskPriority


class Task(Base, BaseModelMixin, PrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """
    Task entity for workflow and project management.
    
    Status machine: PENDING → IN_PROGRESS → COMPLETED/CANCELLED/ON_HOLD
    """
    __tablename__ = "tasks"

    task_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    """Auto-generated task ID (e.g., TASK-000001)"""
    
    # Task details
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Classification
    task_type: Mapped[str] = mapped_column(String(50), nullable=False, default="general")  # general, lead_follow_up, project, booking, etc.
    category: Mapped[str] = mapped_column(String(50), nullable=False, default="other")  # workflow, reminder, documentation, etc.
    
    # Status and priority
    status: Mapped[TaskStatus] = mapped_column(
        SQLEnum(TaskStatus),
        nullable=False,
        default=TaskStatus.PENDING,
        index=True
    )
    priority: Mapped[TaskPriority] = mapped_column(
        SQLEnum(TaskPriority),
        nullable=False,
        default=TaskPriority.MEDIUM,
        index=True
    )
    
    # Assignments and ownership
    assigned_to_user_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_by_user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    
    # Timing
    due_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, index=True)
    start_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Estimation and tracking
    estimated_hours: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    actual_hours: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 0-100%
    
    # Context references
    lead_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("leads.id", ondelete="SET NULL"), nullable=True, index=True)
    customer_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("customers.id", ondelete="SET NULL"), nullable=True, index=True)
    project_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True)
    booking_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("bookings.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Metadata
    tags: Mapped[list] = mapped_column(JSON, default=list, nullable=False)  # Tags for filtering
    attachments_urls: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    is_urgent: Mapped[bool] = mapped_column(Boolean, default=False)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    assigned_to = relationship("User", foreign_keys=[assigned_to_user_id], viewonly=True)
    created_by = relationship("User", foreign_keys=[created_by_user_id], viewonly=True)
    lead = relationship("Lead", foreign_keys=[lead_id], viewonly=True)
    customer = relationship("Customer", foreign_keys=[customer_id], viewonly=True)
    project = relationship("Project", foreign_keys=[project_id], viewonly=True)
    booking = relationship("Booking", foreign_keys=[booking_id], viewonly=True)
    checklists = relationship("TaskChecklist", back_populates="task", cascade="all, delete-orphan")
    comments = relationship("TaskComment", back_populates="task", cascade="all, delete-orphan")
    attachments = relationship("TaskAttachment", back_populates="task", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("ix_task_assigned_status", "assigned_to_user_id", "status"),
        Index("ix_task_due_date_status", "due_date", "status"),
        Index("ix_task_lead_status", "lead_id", "status"),
        Index("ix_task_customer_status", "customer_id", "status"),
    )


class TaskChecklist(Base, BaseModelMixin, PrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """
    Checklist item within a task.
    """
    __tablename__ = "task_checklists"

    task_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    item_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    completed_by_user_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    task = relationship("Task", back_populates="checklists", viewonly=True)
    completed_by = relationship("User", foreign_keys=[completed_by_user_id], viewonly=True)


class TaskComment(Base, BaseModelMixin, PrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """
    Comment or note on a task.
    """
    __tablename__ = "task_comments"

    task_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    content: Mapped[str] = mapped_column(Text, nullable=False)
    commented_by_user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    
    # Metadata
    is_internal: Mapped[bool] = mapped_column(Boolean, default=False)  # Internal notes only
    mentions: Mapped[list] = mapped_column(JSON, default=list, nullable=False)  # List of mentioned user IDs
    
    # Relationships
    task = relationship("Task", back_populates="comments", viewonly=True)
    commented_by = relationship("User", foreign_keys=[commented_by_user_id], viewonly=True)
    
    __table_args__ = (
        Index("ix_task_comment_task_created", "task_id", "created_at"),
    )


class TaskAttachment(Base, BaseModelMixin, PrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """
    Attachment (file) associated with a task.
    """
    __tablename__ = "task_attachments"

    task_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_url: Mapped[str] = mapped_column(Text, nullable=False)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)  # In bytes
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    uploaded_by_user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Relationships
    task = relationship("Task", back_populates="attachments", viewonly=True)
    uploaded_by = relationship("User", foreign_keys=[uploaded_by_user_id], viewonly=True)


class Activity(Base, BaseModelMixin, PrimaryKeyMixin, TimestampMixin):
    """
    Activity log for system events and user actions.
    """
    __tablename__ = "activities"

    # Event details
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # lead, customer, booking, task, etc.
    entity_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # created, updated, deleted, status_changed, etc.
    
    description: Mapped[str] = mapped_column(Text, nullable=False)
    old_value: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # Previous state
    new_value: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # New state
    
    # Actor
    performed_by_user_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    
    # Metadata
    ip_address: Mapped[str | None] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    # Relationships
    performed_by = relationship("User", foreign_keys=[performed_by_user_id], viewonly=True)
    
    __table_args__ = (
        Index("ix_activity_entity", "entity_type", "entity_id"),
        Index("ix_activity_performed_by", "performed_by_user_id", "created_at"),
        Index("ix_activity_action", "action", "created_at"),
    )
