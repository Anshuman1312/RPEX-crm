from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import TimestampSchema


class FollowUpCreate(BaseModel):
    lead_id: str
    assigned_to: str
    followup_date: datetime
    remark: str
    status: str = "PENDING"


class FollowUpOut(TimestampSchema):
    lead_id: str
    assigned_to: str
    followup_date: datetime
    remark: str
    status: str
