from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


# ── Sort Direction ───────────────────────────────────────────────────────────

class SortDirection(str, Enum):
    """Sort order."""

    ASC = "asc"
    DESC = "desc"


# ── Common Filter Models ─────────────────────────────────────────────────────

class DateRangeFilter(BaseModel):
    """Date range filter."""

    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None


class StatusFilter(BaseModel):
    """Status filter (for entities with status)."""

    statuses: list[str] = Field(default_factory=list)


class TextSearchFilter(BaseModel):
    """Full-text search filter."""

    query: Optional[str] = None
    fields: list[str] = Field(
        default_factory=list,
        description="Fields to search in (if empty, searches all indexed fields)",
    )


class SortBy(BaseModel):
    """Sort specification."""

    field: str = Field(..., min_length=1)
    direction: SortDirection = SortDirection.ASC


# ── Lead Filters ─────────────────────────────────────────────────────────────

class LeadFilterParams(BaseModel):
    """Lead search and filter parameters."""

    # Search
    search: Optional[str] = Field(None, description="Search in name, email, phone")
    
    # Status
    statuses: Optional[list[str]] = None
    
    # Source
    sources: Optional[list[str]] = None
    
    # Date range
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    
    # Assignment
    assigned_to_user_id: Optional[str] = None
    
    # Priority
    priorities: Optional[list[str]] = None
    
    # Interested projects
    project_ids: Optional[list[str]] = None
    
    # Sort
    sort_by: str = "created_at"
    sort_direction: SortDirection = SortDirection.DESC


# ── Customer Filters ─────────────────────────────────────────────────────────

class CustomerFilterParams(BaseModel):
    """Customer search and filter parameters."""

    # Search
    search: Optional[str] = Field(None, description="Search in name, email, phone")
    
    # Status
    statuses: Optional[list[str]] = None
    
    # Type
    customer_types: Optional[list[str]] = None
    
    # Date range
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    
    # KYC status
    kyc_verified: Optional[bool] = None
    
    # Sort
    sort_by: str = "created_at"
    sort_direction: SortDirection = SortDirection.DESC


# ── Project Filters ──────────────────────────────────────────────────────────

class ProjectFilterParams(BaseModel):
    """Project search and filter parameters."""

    # Search
    search: Optional[str] = Field(None, description="Search in name, location")
    
    # Status
    statuses: Optional[list[str]] = None
    
    # Type
    project_types: Optional[list[str]] = None
    
    # Date range
    launch_after: Optional[datetime] = None
    launch_before: Optional[datetime] = None
    
    # Completion status
    is_completed: Optional[bool] = None
    
    # Sort
    sort_by: str = "created_at"
    sort_direction: SortDirection = SortDirection.DESC


# ── Booking Filters ──────────────────────────────────────────────────────────

class BookingFilterParams(BaseModel):
    """Booking search and filter parameters."""

    # Search
    search: Optional[str] = Field(None, description="Search in customer name, booking ref")
    
    # Status
    statuses: Optional[list[str]] = None
    
    # Project
    project_id: Optional[str] = None
    
    # Unit
    unit_id: Optional[str] = None
    
    # Date range
    booked_after: Optional[datetime] = None
    booked_before: Optional[datetime] = None
    
    # Payment status
    payment_statuses: Optional[list[str]] = None
    
    # Sort
    sort_by: str = "created_at"
    sort_direction: SortDirection = SortDirection.DESC


# ── Payment Filters ──────────────────────────────────────────────────────────

class PaymentFilterParams(BaseModel):
    """Payment search and filter parameters."""

    # Booking
    booking_id: Optional[str] = None
    
    # Status
    statuses: Optional[list[str]] = None
    
    # Date range
    paid_after: Optional[datetime] = None
    paid_before: Optional[datetime] = None
    due_after: Optional[datetime] = None
    due_before: Optional[datetime] = None
    
    # Amount range
    amount_min: Optional[float] = None
    amount_max: Optional[float] = None
    
    # Method
    payment_methods: Optional[list[str]] = None
    
    # Sort
    sort_by: str = "due_date"
    sort_direction: SortDirection = SortDirection.ASC


# ── Task Filters ─────────────────────────────────────────────────────────────

class TaskFilterParams(BaseModel):
    """Task search and filter parameters."""

    # Search
    search: Optional[str] = Field(None, description="Search in title, description")
    
    # Status
    statuses: Optional[list[str]] = None
    
    # Assigned to
    assigned_to_user_id: Optional[str] = None
    
    # Priority
    priorities: Optional[list[str]] = None
    
    # Date range
    due_after: Optional[datetime] = None
    due_before: Optional[datetime] = None
    
    # Is overdue
    is_overdue: Optional[bool] = None
    
    # Sort
    sort_by: str = "due_date"
    sort_direction: SortDirection = SortDirection.ASC


# ── Notification Filters ────────────────────────────────────────────────────

class NotificationFilterParams(BaseModel):
    """Notification search and filter parameters."""

    # Read status
    is_read: Optional[bool] = None
    
    # Type
    notification_types: Optional[list[str]] = None
    
    # Date range
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    
    # Sort
    sort_by: str = "created_at"
    sort_direction: SortDirection = SortDirection.DESC
