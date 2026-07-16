from typing import Any

from pydantic import BaseModel, Field

from app.schemas.common import TimestampSchema


class ProjectCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    developer_name: str = Field(min_length=2, max_length=200)
    sole_selling_partner: str | None = None
    location: str = Field(min_length=2, max_length=255)
    google_maps_url: str | None = None
    project_status: str = Field(default="PLANNING", max_length=64)
    total_inventory: int = Field(default=0, ge=0)
    sold_inventory: int = Field(default=0, ge=0)
    price_list: list[dict[str, Any]] = Field(default_factory=list)
    payment_plans: list[dict[str, Any]] = Field(default_factory=list)
    documents: list[dict[str, Any]] = Field(default_factory=list)
    gallery: list[dict[str, Any]] = Field(default_factory=list)
    videos: list[dict[str, Any]] = Field(default_factory=list)
    brochure: dict[str, Any] = Field(default_factory=dict)
    legal_status: str | None = None
    amenities: list[str] = Field(default_factory=list)
    nearby_landmarks: list[str] = Field(default_factory=list)


class ProjectOut(TimestampSchema):
    name: str
    developer_name: str
    sole_selling_partner: str | None
    location: str
    google_maps_url: str | None
    project_status: str
    total_inventory: int
    sold_inventory: int
    available_inventory: int
    price_list: list[dict[str, Any]]
    payment_plans: list[dict[str, Any]]
    documents: list[dict[str, Any]]
    gallery: list[dict[str, Any]]
    videos: list[dict[str, Any]]
    brochure: dict[str, Any]
    legal_status: str | None
    amenities: list[str]
    nearby_landmarks: list[str]
    created_by: str
