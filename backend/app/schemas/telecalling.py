from datetime import date

from pydantic import BaseModel, Field


class TelecallingCallCreate(BaseModel):
    call_date: date
    telecaller_id: str
    lead_id: str | None = None
    customer_name: str = Field(min_length=2, max_length=200)
    status: str = Field(default="NOT_CONNECTED", max_length=32)
    call_duration_sec: int = Field(default=0, ge=0)
    call_recording_url: str | None = Field(default=None, max_length=1024)
    daily_target: int = Field(default=0, ge=0)
    notes: str | None = None
