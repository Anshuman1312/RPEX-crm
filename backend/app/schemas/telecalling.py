from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class TelecallingCallCreate(BaseModel):
    call_date: datetime | None = None
    telecaller_id: str | None = None
    lead_id: str | None = None
    customer_id: str | None = None
    customer_name: str | None = Field(default=None, max_length=200)
    phone: str = Field(min_length=5, max_length=20)
    direction: str = Field(default="OUTBOUND", max_length=16)
    status: str = Field(default="INITIATED", max_length=30)
    call_duration_sec: int | None = Field(default=None, ge=0)
    call_recording_url: str | None = None
    daily_target: int | None = Field(default=None, ge=0)
    notes: str | None = None
