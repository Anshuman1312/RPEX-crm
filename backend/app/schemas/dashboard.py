"""
Schemas for dashboard widgets and system settings.
"""

from __future__ import annotations

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Any
from uuid import UUID

from pydantic import BaseModel, Field


# ── Dashboard Widget Schemas ──────────────────────────────────────────

class LeadPipelineWidget(BaseModel):
    """Lead pipeline summary widget."""
    total_leads: int
    new_today: int
    contacted: int
    qualified: int
    converted_this_month: int
    lost_this_month: int
    conversion_rate: float
    overdue_followups: int


class RevenueSnapshotWidget(BaseModel):
    """Revenue snapshot widget."""
    invoiced_this_month: Decimal
    collected_this_month: Decimal
    pending_amount: Decimal
    overdue_amount: Decimal
    collection_rate: float
    total_receivable: Decimal


class BookingSnapshotWidget(BaseModel):
    """Booking snapshot widget."""
    total_bookings: int
    initiated_count: int
    confirmed_count: int
    approved_count: int
    cancelled_this_month: int
    total_booking_value: Decimal


class TaskSummaryWidget(BaseModel):
    """Task summary widget."""
    my_pending: int
    my_in_progress: int
    my_overdue: int
    due_today: int
    due_this_week: int
    completed_today: int


class TeamActivityWidget(BaseModel):
    """Recent team activity widget."""
    activities_today: int
    followups_today: int
    tasks_completed_today: int
    new_leads_today: int
    bookings_today: int


class UpcomingItem(BaseModel):
    """Single upcoming item (followup or task)."""
    id: UUID
    type: str  # "followup" or "task"
    title: str
    entity_type: Optional[str]
    entity_name: Optional[str]
    scheduled_at: Optional[datetime]
    due_date: Optional[datetime]
    priority: int
    is_overdue: bool


class RecentLead(BaseModel):
    """Recent lead for dashboard list."""
    id: UUID
    lead_number: str
    full_name: str
    status: str
    source: str
    created_at: datetime
    assigned_to_name: Optional[str]


class RecentBooking(BaseModel):
    """Recent booking for dashboard list."""
    id: UUID
    booking_number: str
    customer_name: str
    project_name: str
    booking_amount: Decimal
    status: str
    created_at: datetime


class InventorySnapshotWidget(BaseModel):
    """Inventory availability snapshot."""
    total_units: int
    available_units: int
    booked_units: int
    sold_units: int
    availability_rate: float


class DashboardResponse(BaseModel):
    """Full dashboard data response."""
    # Meta
    user_id: UUID
    user_name: str
    generated_at: datetime
    period_label: str  # "Today", "This Week", "This Month"

    # Widgets
    lead_pipeline: LeadPipelineWidget
    revenue_snapshot: RevenueSnapshotWidget
    booking_snapshot: BookingSnapshotWidget
    task_summary: TaskSummaryWidget
    team_activity: TeamActivityWidget
    inventory_snapshot: InventorySnapshotWidget

    # Lists
    upcoming_items: List[UpcomingItem] = Field(default_factory=list)
    recent_leads: List[RecentLead] = Field(default_factory=list)
    recent_bookings: List[RecentBooking] = Field(default_factory=list)


# ── Settings Schemas ──────────────────────────────────────────────────

class AppSettingResponse(BaseModel):
    """Response schema for app setting."""
    id: UUID
    key: str
    label: str
    category: str
    data_type: str
    value: Optional[Any]  # resolved from the right value_* column
    description: Optional[str]
    is_sensitive: bool
    is_readonly: bool
    updated_at: datetime

    class Config:
        from_attributes = True


class AppSettingUpdate(BaseModel):
    """Update an app setting value."""
    value: Any  # validated at service layer based on data_type


class AppSettingCreate(BaseModel):
    """Create a new app setting."""
    key: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z0-9_.]+$")
    label: str = Field(..., min_length=1, max_length=200)
    category: str = Field("general", max_length=50)
    data_type: str = Field("string", pattern=r"^(string|int|bool|json)$")
    value: Optional[Any] = None
    description: Optional[str] = None
    is_sensitive: bool = False
    is_readonly: bool = False


class UserSettingResponse(BaseModel):
    """Response schema for a user setting."""
    key: str
    value: Any
    updated_at: datetime

    class Config:
        from_attributes = True


class UserSettingUpdate(BaseModel):
    """Update user setting."""
    key: str
    value: Any


class UserSettingsBulkUpdate(BaseModel):
    """Bulk update user settings."""
    settings: List[UserSettingUpdate]


# ── Role & Permission Schemas ─────────────────────────────────────────

class RoleResponse(BaseModel):
    """Response schema for role."""
    id: UUID
    name: str
    description: Optional[str]
    is_system: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PermissionResponse(BaseModel):
    """Response schema for permission."""
    id: UUID
    scope: str
    action: str
    description: Optional[str]

    class Config:
        from_attributes = True


class RolePermissionUpdate(BaseModel):
    """Update permissions for a role."""
    permission_ids: List[UUID]
