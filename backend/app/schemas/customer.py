from datetime import date
from typing import Any

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import TimestampSchema


class CustomerCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=128)
    email: EmailStr | None = None
    phone: str = Field(min_length=7, max_length=30)
    alternate_phone: str | None = Field(default=None, max_length=30)
    address: str | None = None
    city: str | None = Field(default=None, max_length=64)
    state: str | None = Field(default=None, max_length=64)
    country: str | None = Field(default=None, max_length=64)
    pincode: str | None = Field(default=None, max_length=20)
    birth_date: date | None = None
    anniversary_date: date | None = None
    partner_user_id: str | None = None
    extra_data: dict[str, Any] = Field(default_factory=dict)


class CustomerOut(TimestampSchema):
    full_name: str
    email: EmailStr | None
    phone: str
    alternate_phone: str | None
    address: str | None
    city: str | None
    state: str | None
    country: str | None
    pincode: str | None
    birth_date: date | None
    anniversary_date: date | None
    partner_user_id: str | None
    created_by: str
    extra_data: dict[str, Any]
