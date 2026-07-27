from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

import uuid


# ── Lead Activity ────────────────────────────────────────────────────────────

class LeadActivityResponse(BaseModel):
    """Lead activity response."""

    id: uuid.UUID
    activity_type: str
    subject: str
    description: Optional[str] = None
    outcome: Optional[str] = None
    performed_by_user_id: Optional[uuid.UUID] = None
    activity_date: datetime
    next_followup: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class LeadActivityCreate(BaseModel):
    """Create lead activity."""

    activity_type: str = Field(..., min_length=1, max_length=50)
    subject: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    outcome: Optional[str] = Field(None, max_length=100)
    activity_date: datetime
    next_followup: Optional[datetime] = None


# ── Lead ─────────────────────────────────────────────────────────────────────

class LeadResponse(BaseModel):
    """Full lead response."""

    id: uuid.UUID
    lead_number: str
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    source: str
    status: str
    priority: str
    assigned_to_user_id: Optional[uuid.UUID] = None
    assignment_date: Optional[datetime] = None
    company_name: Optional[str] = None
    designation: Optional[str] = None
    budget: Optional[int] = None
    notes: Optional[str] = None
    interested_in_project: Optional[uuid.UUID] = None
    preferred_unit_type: Optional[str] = None
    last_contacted_at: Optional[datetime] = None
    last_activity_at: Optional[datetime] = None
    next_followup_at: Optional[datetime] = None
    conversion_date: Optional[datetime] = None
    lost_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    activities: list[LeadActivityResponse] = []

    model_config = {"from_attributes": True}


class LeadListResponse(BaseModel):
    """Lead list item (less info than full response)."""

    id: uuid.UUID
    lead_number: str
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    source: str
    status: str
    priority: str
    assigned_to_user_id: Optional[uuid.UUID] = None
    company_name: Optional[str] = None
    last_contacted_at: Optional[datetime] = None
    next_followup_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class LeadCreate(BaseModel):
    """Create lead."""

    full_name: str = Field(..., min_length=2, max_length=200)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    source: str = Field(..., min_length=1, max_length=50)
    status: Optional[str] = Field(None, max_length=50)
    priority: Optional[str] = Field(None, max_length=50)
    company_name: Optional[str] = Field(None, max_length=255)
    designation: Optional[str] = Field(None, max_length=100)
    budget: Optional[int] = None
    notes: Optional[str] = Field(None, max_length=5000)
    interested_in_project: Optional[str] = None
    preferred_unit_type: Optional[str] = Field(None, max_length=50)
    assigned_to_user_id: Optional[str] = None


class LeadUpdate(BaseModel):
    """Update lead."""

    full_name: Optional[str] = Field(None, min_length=2, max_length=200)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    source: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = Field(None, max_length=50)
    priority: Optional[str] = Field(None, max_length=50)
    company_name: Optional[str] = Field(None, max_length=255)
    designation: Optional[str] = Field(None, max_length=100)
    budget: Optional[int] = None
    notes: Optional[str] = Field(None, max_length=5000)
    interested_in_project: Optional[str] = None
    preferred_unit_type: Optional[str] = Field(None, max_length=50)
    assigned_to_user_id: Optional[str] = None
    next_followup_at: Optional[datetime] = None


class LeadStatusUpdate(BaseModel):
    """Update lead status."""

    status: str = Field(..., min_length=1, max_length=50)
    notes: Optional[str] = Field(None, max_length=5000)


class LeadAssignRequest(BaseModel):
    """Assign lead to user."""

    assigned_to_user_id: str
    notes: Optional[str] = Field(None, max_length=5000)
