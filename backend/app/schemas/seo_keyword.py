from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field


class SEOKeywordCreate(BaseModel):
    keyword: str = Field(min_length=1, max_length=256)
    platform: str = Field(min_length=1, max_length=64)
    match_type: str = Field(default="BROAD", max_length=32)
    status: str = Field(default="ACTIVE", max_length=32)
    bid_amount: Decimal = Field(default=0, ge=0)
    campaign_id: str
