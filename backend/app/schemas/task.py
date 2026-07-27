"""
Schemas for task and activity management operations.

Includes: Task CRUD, checklist management, comments, activity tracking.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, validator

from app.utils.enums import TaskStatus, TaskPriority


# ── Task Checklist Schemas ────────────────────────────────────────────

class TaskChecklistCreate(BaseModel):
    """Create checklist item."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class TaskChecklistUpdate(BaseModel):
    """Update checklist item."""
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None


class TaskChecklistResponse(BaseModel):
    """Response schema for task checklist item."""
    id: UUID
    item_number: int
    title: str
    description: Optional[str]
    is_completed: bool
    completed_by_user_id: Optional[UUID]
    completed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ── Task Comment Schemas ──────────────────────────────────────────────

class TaskCommentCreate(BaseModel):
    """Create task comment."""
    content: str = Field(..., min_length=1)
    is_internal: bool = False
    mentions: List[str] = Field(default_factory=list)


class TaskCommentResponse(BaseModel):
    """Response schema for task comment."""
    id: UUID
    content: str
    commented_by_user_id: UUID
    is_internal: bool
    mentions: List[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── Task Attachment Schemas ──────────────────────────────────────────

class TaskAttachmentResponse(BaseModel):
    """Response schema for task attachment."""
    id: UUID
    filename: str
    file_url: str
    file_size: Optional[int]
    mime_type: Optional[str]
    uploaded_by_user_id: UUID
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ── Task CRUD Schemas ─────────────────────────────────────────────────

class TaskCreate(BaseModel):
    """Create task."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    task_type: str = Field("general", max_length=50)
    category: str = Field("other", max_length=50)
    priority: TaskPriority = TaskPriority.MEDIUM
    assigned_to_user_id: Optional[UUID] = None
    due_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    estimated_hours: Optional[Decimal] = None
    lead_id: Optional[UUID] = None
    customer_id: Optional[UUID] = None
    project_id: Optional[UUID] = None
    booking_id: Optional[UUID] = None
    tags: List[str] = Field(default_factory=list)
    is_urgent: bool = False
    is_recurring: bool = False
    checklists: List[TaskChecklistCreate] = Field(default_factory=list)


class TaskUpdate(BaseModel):
    """Update task."""
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[TaskPriority] = None
    assigned_to_user_id: Optional[UUID] = None
    due_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    estimated_hours: Optional[Decimal] = None
    progress: Optional[int] = Field(None, ge=0, le=100)
    tags: Optional[List[str]] = None
    is_urgent: Optional[bool] = None


class TaskStatusUpdate(BaseModel):
    """Update task status."""
    status: TaskStatus
    notes: Optional[str] = None


class TaskResponse(BaseModel):
    """Response schema for task with details."""
    id: UUID
    task_number: str
    title: str
    description: Optional[str]
    task_type: str
    category: str
    status: TaskStatus
    priority: TaskPriority
    assigned_to_user_id: Optional[UUID]
    created_by_user_id: UUID
    due_date: Optional[datetime]
    start_date: Optional[datetime]
    completed_at: Optional[datetime]
    estimated_hours: Optional[Decimal]
    actual_hours: Optional[Decimal]
    progress: int
    lead_id: Optional[UUID]
    customer_id: Optional[UUID]
    project_id: Optional[UUID]
    booking_id: Optional[UUID]
    tags: List[str]
    is_urgent: bool
    is_recurring: bool
    checklists: List[TaskChecklistResponse] = Field(default_factory=list)
    comments: List[TaskCommentResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """List response for tasks (simplified)."""
    id: UUID
    task_number: str
    title: str
    status: TaskStatus
    priority: TaskPriority
    assigned_to_user_id: Optional[UUID]
    due_date: Optional[datetime]
    progress: int
    is_urgent: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ── Task Assignment ───────────────────────────────────────────────────

class TaskAssignRequest(BaseModel):
    """Assign task to user."""
    assigned_to_user_id: Optional[UUID] = None


# ── Task Progress ────────────────────────────────────────────────────

class TaskProgressUpdate(BaseModel):
    """Update task progress."""
    progress: int = Field(..., ge=0, le=100)
    actual_hours: Optional[Decimal] = None
    notes: Optional[str] = None


# ── Checklist Operations ──────────────────────────────────────────────

class TaskChecklistCompleteRequest(BaseModel):
    """Mark checklist item as complete."""
    pass


# ── Statistics and Reporting ──────────────────────────────────────────

class TaskStatistics(BaseModel):
    """Task statistics."""
    total_tasks: int
    pending_count: int
    in_progress_count: int
    completed_count: int
    cancelled_count: int
    on_hold_count: int
    overdue_count: int
    completion_rate: float  # percentage
    by_priority: dict = Field(default_factory=dict)  # {priority: count}
    by_status: dict = Field(default_factory=dict)  # {status: count}
    by_category: dict = Field(default_factory=dict)  # {category: count}
    average_completion_hours: Optional[float]


class UserTaskLoad(BaseModel):
    """User's task workload."""
    user_id: UUID
    total_assigned: int
    pending_count: int
    in_progress_count: int
    completed_today: int
    overdue_count: int
    by_priority: dict = Field(default_factory=dict)


# ── Activity Schemas ──────────────────────────────────────────────────

class ActivityCreate(BaseModel):
    """Create activity log."""
    entity_type: str
    entity_id: UUID
    action: str
    description: str
    old_value: Optional[dict] = None
    new_value: Optional[dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class ActivityResponse(BaseModel):
    """Response schema for activity."""
    id: UUID
    entity_type: str
    entity_id: UUID
    action: str
    description: str
    old_value: Optional[dict]
    new_value: Optional[dict]
    performed_by_user_id: Optional[UUID]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ── Bulk Operations ───────────────────────────────────────────────────

class TaskBulkStatusUpdate(BaseModel):
    """Bulk update status for multiple tasks."""
    task_ids: List[UUID]
    status: TaskStatus
    notes: Optional[str] = None


class TaskBulkAssign(BaseModel):
    """Bulk assign multiple tasks to user."""
    task_ids: List[UUID]
    assigned_to_user_id: Optional[UUID] = None
