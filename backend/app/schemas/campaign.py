from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.common import TimestampSchema


class CampaignCreate(BaseModel):
    name: str = Field(min_length=2, max_length=128)
    type: str
    platform: str
    budget: Decimal = Decimal("0")
    start_date: date | None = None
    end_date: date | None = None


class CampaignOut(TimestampSchema):
    name: str
    type: str
    platform: str
    budget: Decimal
    start_date: date | None
    end_date: date | None
    created_by: str
