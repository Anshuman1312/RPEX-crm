from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class DocumentAssetCreate(BaseModel):
    customer_id: str | None = None
    booking_id: str | None = None
    category: str = Field(min_length=2, max_length=64)
    file_name: str = Field(min_length=1, max_length=255)
    storage_key: str = Field(min_length=1, max_length=255)
    content_type: str | None = Field(default=None, max_length=128)
    size_bytes: int | None = Field(default=None, ge=0)
    partner_user_id: str | None = None
    file_metadata: dict[str, Any] = Field(default_factory=dict)
