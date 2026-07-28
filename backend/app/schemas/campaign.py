from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


class CampaignCreate(BaseModel):
    name: str = Field(min_length=2, max_length=128)
    type: str = Field(min_length=1, max_length=64)
    platform: str = Field(min_length=1, max_length=64)
    budget: Decimal = Field(default=Decimal("0"), ge=0)
    start_date: date | None = None
    end_date: date | None = None
    extra_data: dict[str, Any] = Field(default_factory=dict)
