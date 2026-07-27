"""
Schemas for notification management operations.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field

from app.utils.enums import NotificationType, NotificationChannel


# ── Notification Schemas ──────────────────────────────────────────────

class NotificationCreate(BaseModel):
    """Create a notification (internal use / admin)."""
    user_id: UUID
    type: NotificationType
    channel: NotificationChannel = NotificationChannel.IN_APP
    title: str = Field(..., min_length=1, max_length=255)
    body: str = Field(..., min_length=1)
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None
    priority: int = Field(0, ge=0, le=3)
    action_url: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


class NotificationResponse(BaseModel):
    """Response schema for a notification."""
    id: UUID
    user_id: UUID
    type: NotificationType
    channel: NotificationChannel
    title: str
    body: str
    entity_type: Optional[str]
    entity_id: Optional[UUID]
    is_read: bool
    read_at: Optional[datetime]
    is_archived: bool
    priority: int
    action_url: Optional[str]
    metadata: dict
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Simplified notification for list view."""
    id: UUID
    type: NotificationType
    title: str
    body: str
    is_read: bool
    priority: int
    entity_type: Optional[str]
    entity_id: Optional[UUID]
    action_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationMarkRead(BaseModel):
    """Mark notification(s) as read."""
    notification_ids: List[UUID]


class NotificationMarkArchived(BaseModel):
    """Archive notification(s)."""
    notification_ids: List[UUID]


class NotificationBulkSend(BaseModel):
    """Bulk send notifications to multiple users."""
    user_ids: List[UUID]
    type: NotificationType
    channel: NotificationChannel = NotificationChannel.IN_APP
    title: str
    body: str
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None
    priority: int = Field(0, ge=0, le=3)
    action_url: Optional[str] = None


# ── Notification Preference Schemas ───────────────────────────────────

class NotificationPreferenceUpdate(BaseModel):
    """Update notification preference."""
    in_app_enabled: Optional[bool] = None
    email_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None
    whatsapp_enabled: Optional[bool] = None
    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start: Optional[int] = Field(None, ge=0, le=23)
    quiet_hours_end: Optional[int] = Field(None, ge=0, le=23)
    max_per_day: Optional[int] = Field(None, ge=1, le=1000)


class NotificationPreferenceResponse(BaseModel):
    """Response schema for notification preference."""
    id: UUID
    user_id: UUID
    notification_type: NotificationType
    in_app_enabled: bool
    email_enabled: bool
    sms_enabled: bool
    push_enabled: bool
    whatsapp_enabled: bool
    quiet_hours_enabled: bool
    quiet_hours_start: Optional[int]
    quiet_hours_end: Optional[int]
    max_per_day: Optional[int]
    updated_at: datetime

    class Config:
        from_attributes = True


# ── Notification Template Schemas ─────────────────────────────────────

class NotificationTemplateCreate(BaseModel):
    """Create notification template."""
    name: str = Field(..., min_length=1, max_length=100)
    notification_type: NotificationType
    channel: NotificationChannel
    title_template: str = Field(..., min_length=1, max_length=255)
    body_template: str = Field(..., min_length=1)
    variables: List[str] = Field(default_factory=list)


class NotificationTemplateUpdate(BaseModel):
    """Update notification template."""
    title_template: Optional[str] = None
    body_template: Optional[str] = None
    variables: Optional[List[str]] = None
    is_active: Optional[bool] = None


class NotificationTemplateResponse(BaseModel):
    """Response schema for notification template."""
    id: UUID
    name: str
    notification_type: NotificationType
    channel: NotificationChannel
    title_template: str
    body_template: str
    variables: List[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── Statistics ────────────────────────────────────────────────────────

class NotificationStatistics(BaseModel):
    """Notification statistics."""
    total_sent: int
    unread_count: int
    read_count: int
    archived_count: int
    by_type: dict = Field(default_factory=dict)
    by_channel: dict = Field(default_factory=dict)
    by_priority: dict = Field(default_factory=dict)


class UnreadCountResponse(BaseModel):
    """Unread notification count for a user."""
    user_id: UUID
    unread_count: int
    critical_count: int
    high_priority_count: int
