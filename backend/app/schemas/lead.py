from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import TimestampSchema

LEAD_SOURCE_OPTIONS = [
    "FACEBOOK",
    "INSTAGRAM",
    "GOOGLE_ADS",
    "WEBSITE",
    "WHATSAPP",
    "REFERRAL",
    "WALK_IN",
    "CALL",
    "MAGICBRICKS",
    "99ACRES",
    "HOUSING_COM",
]

LEAD_STATUS_OPTIONS = [
    "NEW",
    "CONTACTED",
    "FOLLOW_UP",
    "INTERESTED",
    "SITE_VISIT",
    "NEGOTIATION",
    "BOOKING",
    "LOST",
    "FUTURE",
]


class WebhookLeadIn(BaseModel):
    name: str
    email: EmailStr
    phone: str
    source: str | None = None
    campaign: str | None = None
    landing_page: str | None = None
    utm_source: str | None = None
    utm_medium: str | None = None


class LeadCreate(BaseModel):
    website_id: str | None = None
    name: str
    email: EmailStr
    phone: str
    source: str | None = None
    medium: str | None = None
    campaign_id: str | None = None
    status: str = "NEW"
    assigned_to: str | None = None
    budget: str | None = None
    preferred_location: str | None = None
    property_type: str | None = None
    notes: str | None = None
    interested_project: str | None = None
    assigned_to_name: str | None = None
    lead_score: int | None = Field(default=None, ge=0, le=100)
    extra_data: dict[str, Any] = Field(default_factory=dict)


class LeadUpdateStatus(BaseModel):
    status: str
    description: str | None = None


class LeadOut(TimestampSchema):
    website_id: str
    name: str
    email: EmailStr
    phone: str
    source: str | None
    medium: str | None
    campaign_id: str | None
    status: str
    assigned_to: str | None
    extra_data: dict[str, Any]


class LeadSearchResponse(BaseModel):
    items: list[dict[str, Any]]
    total: int
    page: int
    page_size: int


class LeadSavedViewCreate(BaseModel):
    name: str = Field(min_length=2, max_length=128)
    filters: dict[str, Any]
    is_public: bool = False


class LeadSavedViewOut(TimestampSchema):
    user_id: str
    name: str
    filters: dict[str, Any]
    is_public: bool


class LeadQueryFilters(BaseModel):
    q: str | None = None
    statuses: list[str] = Field(default_factory=list)
    source: str | None = None
    medium: str | None = None
    campaign_id: str | None = None
    assigned_to: str | None = None
    created_from: datetime | None = None
    created_to: datetime | None = None
    extra_field_filters: dict[str, str] = Field(default_factory=dict)
    sort_by: str = "created_at"
    sort_order: str = "desc"
    page: int = 1
    page_size: int = 50
