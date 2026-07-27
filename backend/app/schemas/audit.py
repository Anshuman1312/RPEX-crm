"""
Schemas for audit log queries and responses.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


class AuditLogResponse(BaseModel):
    """Response schema for an audit log entry."""
    id: UUID
    created_at: datetime
    user_id: Optional[UUID]
    user_email: Optional[str]
    user_role: Optional[str]
    action: str
    entity_type: str
    entity_id: Optional[UUID]
    entity_display: Optional[str]
    description: str
    old_value: Optional[dict]
    new_value: Optional[dict]
    changes: Optional[dict]
    ip_address: Optional[str]
    correlation_id: Optional[str]
    request_path: Optional[str]
    request_method: Optional[str]
    status: str
    error_message: Optional[str]
    extra_data: dict

    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    """Simplified audit log for list views."""
    id: UUID
    created_at: datetime
    user_email: Optional[str]
    action: str
    entity_type: str
    entity_display: Optional[str]
    description: str
    status: str
    ip_address: Optional[str]

    class Config:
        from_attributes = True


class AuditLogFilter(BaseModel):
    """Filter parameters for audit log queries."""
    user_id: Optional[UUID] = None
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None
    action: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    search: Optional[str] = None


class AuditLogStats(BaseModel):
    """Audit log statistics."""
    total_entries: int
    success_count: int
    failure_count: int
    by_action: dict = Field(default_factory=dict)
    by_entity_type: dict = Field(default_factory=dict)
    by_user: List[dict] = Field(default_factory=list)
    most_active_hours: List[dict] = Field(default_factory=list)
