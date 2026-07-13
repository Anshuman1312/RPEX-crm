from pydantic import BaseModel

from app.schemas.common import TimestampSchema


class SEOKeywordCreate(BaseModel):
    keyword: str
    url: str
    target_position: int | None = None
    current_position: int | None = None
    traffic: int = 0
    clicks: int = 0
    impressions: int = 0
    campaign_id: str


class SEOKeywordOut(TimestampSchema):
    keyword: str
    url: str
    target_position: int | None
    current_position: int | None
    traffic: int
    clicks: int
    impressions: int
    campaign_id: str
