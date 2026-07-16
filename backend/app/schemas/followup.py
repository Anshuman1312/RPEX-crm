from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.common import TimestampSchema


class FollowUpCreate(BaseModel):
    lead_id: str
    assigned_to: str
    followup_date: datetime
    next_followup_date: datetime | None = None
    remark: str
    call_notes: str | None = None
    whatsapp_notes: str | None = None
    meeting_notes: str | None = None
    voice_recording_url: str | None = None
    sms_log: list[dict[str, Any]] = Field(default_factory=list)
    auto_reminder_enabled: bool = True
    status: str = "PENDING"


class FollowUpUpdate(BaseModel):
    next_followup_date: datetime | None = None
    remark: str | None = None
    call_notes: str | None = None
    whatsapp_notes: str | None = None
    meeting_notes: str | None = None
    voice_recording_url: str | None = None
    sms_log: list[dict[str, Any]] | None = None
    auto_reminder_enabled: bool | None = None
    status: str | None = None


class FollowUpOut(TimestampSchema):
    lead_id: str
    assigned_to: str
    followup_date: datetime
    next_followup_date: datetime | None
    remark: str
    call_notes: str | None
    whatsapp_notes: str | None
    meeting_notes: str | None
    voice_recording_url: str | None
    sms_log: list[dict[str, Any]]
    followup_history: list[dict[str, Any]]
    auto_reminder_enabled: bool
    status: str
