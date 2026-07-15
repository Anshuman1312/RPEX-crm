from typing import Any

from pydantic import BaseModel, Field

from app.schemas.common import TimestampSchema


class DocumentAssetCreate(BaseModel):
    customer_id: str | None = None
    booking_id: str | None = None
    category: str = Field(min_length=2, max_length=64)
    file_name: str = Field(min_length=1, max_length=255)
    storage_key: str = Field(min_length=1, max_length=512)
    content_type: str | None = Field(default=None, max_length=128)
    size_bytes: int = Field(default=0, ge=0)
    partner_user_id: str | None = None
    file_metadata: dict[str, Any] = Field(default_factory=dict)


class DocumentAssetOut(TimestampSchema):
    customer_id: str | None
    booking_id: str | None
    category: str
    file_name: str
    storage_key: str
    content_type: str | None
    size_bytes: int
    uploaded_by: str
    partner_user_id: str | None
    file_metadata: dict[str, Any]
