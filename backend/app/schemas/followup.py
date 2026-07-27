"""
Schemas for follow-up management operations.

Includes: FollowUp CRUD, task management, outcome tracking, filtering.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr, validator

from app.utils.enums import (
    FollowUpStatus, FollowUpType, FollowUpOutcomeType,
    FollowUpTaskStatus, FollowUpTaskType
)


# ── Follow-Up Task Schemas ─────────────────────────────────────────────

class FollowUpTaskCreate(BaseModel):
    """Create task within follow-up."""
    task_type: FollowUpTaskType
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    is_required: bool = False


class FollowUpTaskUpdate(BaseModel):
    """Update follow-up task."""
    title: Optional[str] = None
    description: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    notes: Optional[str] = None
    is_required: Optional[bool] = None


class FollowUpTaskResponse(BaseModel):
    """Response schema for follow-up task."""
    id: UUID
    task_type: FollowUpTaskType
    task_number: int
    title: str
    description: Optional[str]
    status: FollowUpTaskStatus
    scheduled_at: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    notes: Optional[str]
    result_notes: Optional[str]
    is_required: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── Follow-Up Outcome Schemas ──────────────────────────────────────────

class FollowUpOutcomeCreate(BaseModel):
    """Record outcome of a follow-up."""
    outcome_type: FollowUpOutcomeType
    summary: str = Field(..., min_length=1)
    next_step: Optional[str] = None
    next_followup_date: Optional[datetime] = None
    estimated_deal_value: Optional[Decimal] = None
    conversion_probability: Optional[int] = Field(None, ge=0, le=100)
    lost_reason: Optional[str] = None
    discussed_projects: List[str] = Field(default_factory=list)
    discussed_units: List[str] = Field(default_factory=list)


class FollowUpOutcomeResponse(BaseModel):
    """Response schema for follow-up outcome."""
    id: UUID
    outcome_type: FollowUpOutcomeType
    summary: str
    next_step: Optional[str]
    next_followup_date: Optional[datetime]
    estimated_deal_value: Optional[Decimal]
    conversion_probability: Optional[int]
    lost_reason: Optional[str]
    discussed_projects: List[str]
    discussed_units: List[str]
    recorded_by_user_id: UUID
    recorded_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# ── Follow-Up CRUD Schemas ────────────────────────────────────────────

class FollowUpCreate(BaseModel):
    """Create follow-up."""
    type: FollowUpType
    subject: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    scheduled_at: datetime
    assigned_to_user_id: Optional[UUID] = None
    lead_id: Optional[UUID] = None
    customer_id: Optional[UUID] = None
    priority: int = Field(0, ge=0, le=2)
    is_critical: bool = False
    notes: Optional[str] = None
    tasks: List[FollowUpTaskCreate] = Field(default_factory=list)

    @validator("lead_id", "customer_id", pre=True)
    def at_least_one_reference(cls, v, values):
        """Ensure at least lead or customer is provided."""
        if "lead_id" in values and "customer_id" in values:
            if not values.get("lead_id") and not v:
                raise ValueError("Either lead_id or customer_id must be provided")
        return v


class FollowUpUpdate(BaseModel):
    """Update follow-up."""
    subject: Optional[str] = None
    description: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    assigned_to_user_id: Optional[UUID] = None
    priority: Optional[int] = None
    is_critical: Optional[bool] = None
    notes: Optional[str] = None


class FollowUpStatusUpdate(BaseModel):
    """Update follow-up status."""
    status: FollowUpStatus
    notes: Optional[str] = None


class FollowUpResponse(BaseModel):
    """Response schema for follow-up with details."""
    id: UUID
    followup_number: str
    type: FollowUpType
    subject: str
    description: Optional[str]
    scheduled_at: datetime
    completed_at: Optional[datetime]
    status: FollowUpStatus
    priority: int
    is_critical: bool
    notes: Optional[str]
    lead_id: Optional[UUID]
    customer_id: Optional[UUID]
    assigned_to_user_id: Optional[UUID]
    created_by_user_id: UUID
    tasks: List[FollowUpTaskResponse] = Field(default_factory=list)
    outcomes: List[FollowUpOutcomeResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FollowUpListResponse(BaseModel):
    """List response for follow-ups (simplified)."""
    id: UUID
    followup_number: str
    type: FollowUpType
    subject: str
    scheduled_at: datetime
    status: FollowUpStatus
    priority: int
    is_critical: bool
    lead_id: Optional[UUID]
    customer_id: Optional[UUID]
    assigned_to_user_id: Optional[UUID]
    task_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


# ── Follow-Up Assignment ───────────────────────────────────────────────

class FollowUpAssignRequest(BaseModel):
    """Assign follow-up to user."""
    assigned_to_user_id: UUID


# ── Follow-Up Task Status Update ───────────────────────────────────────

class FollowUpTaskStatusUpdate(BaseModel):
    """Update task status."""
    status: FollowUpTaskStatus
    result_notes: Optional[str] = None


class FollowUpTaskCompleteRequest(BaseModel):
    """Mark task as complete."""
    result_notes: Optional[str] = None


# ── Statistics and Reporting ───────────────────────────────────────────

class FollowUpStatistics(BaseModel):
    """Follow-up statistics."""
    total_followups: int
    scheduled_count: int
    completed_count: int
    overdue_count: int
    cancelled_count: int
    completion_rate: float  # percentage
    average_response_time_hours: Optional[float]  # Average time from scheduled to completed
    by_type: dict = Field(default_factory=dict)  # {FollowUpType: count}
    by_status: dict = Field(default_factory=dict)  # {FollowUpStatus: count}
    by_outcome: dict = Field(default_factory=dict)  # {FollowUpOutcomeType: count}
    total_deal_value: Decimal = Decimal("0")


class LeadFollowUpSummary(BaseModel):
    """Summary of follow-ups for a lead."""
    lead_id: UUID
    total_followups: int
    scheduled_count: int
    completed_count: int
    last_followup_date: Optional[datetime]
    next_followup_date: Optional[datetime]
    outcome_summary: dict = Field(default_factory=dict)  # {outcome_type: count}


class UserFollowUpLoad(BaseModel):
    """User's follow-up workload."""
    user_id: UUID
    total_assigned: int
    scheduled_count: int
    overdue_count: int
    completed_today: int
    by_priority: dict = Field(default_factory=dict)  # {priority: count}


# ── Bulk Operations ───────────────────────────────────────────────────

class FollowUpBulkStatusUpdate(BaseModel):
    """Bulk update status for multiple follow-ups."""
    followup_ids: List[UUID]
    status: FollowUpStatus
    notes: Optional[str] = None


class FollowUpBulkAssign(BaseModel):
    """Bulk assign multiple follow-ups to user."""
    followup_ids: List[UUID]
    assigned_to_user_id: UUID
