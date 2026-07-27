from __future__ import annotations

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field

from app.utils.enums import ProjectStatus, UnitType, UnitStatus


# ── Project Amenity Schemas ────────────────────────────────────────────────

class ProjectAmenityCreate(BaseModel):
    """Create project amenity."""
    amenity_type: str
    description: Optional[str] = None
    status: str = "ACTIVE"


class ProjectAmenityResponse(BaseModel):
    """Project amenity response."""
    id: str
    project_id: str
    amenity_type: str
    description: Optional[str]
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Unit Availability Log Schemas ────────────────────────────────────────────

class UnitAvailabilityLogResponse(BaseModel):
    """Unit availability log response."""
    id: str
    unit_id: str
    old_status: Optional[str]
    new_status: str
    changed_by_user_id: Optional[str]
    reason: Optional[str]
    related_booking_id: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Floor Schemas ──────────────────────────────────────────────────────────

class FloorCreate(BaseModel):
    """Create floor."""
    floor_number: int
    total_units: int = 0
    status: str = ProjectStatus.PLANNING.value


class FloorResponse(BaseModel):
    """Floor response."""
    id: str
    building_id: str
    floor_number: int
    total_units: int
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Building Schemas ───────────────────────────────────────────────────────

class BuildingCreate(BaseModel):
    """Create building."""
    building_name: str
    total_floors: int
    units_per_floor: int
    status: str = ProjectStatus.PLANNING.value


class BuildingResponse(BaseModel):
    """Building response."""
    id: str
    block_id: str
    building_name: str
    total_floors: int
    units_per_floor: int
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Block Schemas ──────────────────────────────────────────────────────────

class BlockCreate(BaseModel):
    """Create block."""
    block_name: str
    description: Optional[str] = None
    total_units: int = 0
    total_floors: int = 0
    construction_status: int = 0
    status: str = ProjectStatus.PLANNING.value


class BlockResponse(BaseModel):
    """Block response."""
    id: str
    project_id: str
    block_name: str
    description: Optional[str]
    total_units: int
    total_floors: int
    construction_status: int
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Unit Schemas ───────────────────────────────────────────────────────────

class UnitCreate(BaseModel):
    """Create unit."""
    floor_id: str
    unit_number: str
    unit_type: str
    bedroom_count: Optional[int] = None
    bathroom_count: Optional[int] = None
    balcony_count: int = 0
    carpet_area_sqft: float
    built_up_area_sqft: float
    price: float
    furnishing_type: Optional[str] = None
    facing: Optional[str] = None
    description: Optional[str] = None
    amenities: Optional[str] = None
    images_urls: Optional[str] = None


class UnitUpdate(BaseModel):
    """Update unit."""
    bedroom_count: Optional[int] = None
    bathroom_count: Optional[int] = None
    balcony_count: Optional[int] = None
    carpet_area_sqft: Optional[float] = None
    built_up_area_sqft: Optional[float] = None
    price: Optional[float] = None
    furnishing_type: Optional[str] = None
    facing: Optional[str] = None
    description: Optional[str] = None
    amenities: Optional[str] = None
    images_urls: Optional[str] = None


class UnitStatusUpdate(BaseModel):
    """Update unit status."""
    status: str
    reason: Optional[str] = None
    booking_id: Optional[str] = None


class UnitListResponse(BaseModel):
    """Unit list response (subset for list view)."""
    id: str
    project_id: str
    unit_number: str
    unit_type: str
    bedroom_count: Optional[int]
    bathroom_count: Optional[int]
    carpet_area_sqft: float
    built_up_area_sqft: float
    price: float
    status: str
    furnishing_type: Optional[str]
    facing: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class UnitResponse(BaseModel):
    """Full unit response."""
    id: str
    project_id: str
    floor_id: str
    unit_number: str
    unit_type: str
    bedroom_count: Optional[int]
    bathroom_count: Optional[int]
    balcony_count: int
    carpet_area_sqft: float
    built_up_area_sqft: float
    price: float
    status: str
    furnishing_type: Optional[str]
    facing: Optional[str]
    description: Optional[str]
    amenities: Optional[str]
    images_urls: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    # Related data
    availability_logs: List[UnitAvailabilityLogResponse] = []

    model_config = {"from_attributes": True}


# ── Project Schemas ───────────────────────────────────────────────────────

class ProjectCreate(BaseModel):
    """Create project."""
    name: str
    description: Optional[str] = None
    location: str
    city: str
    state: str
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    developer_id: Optional[str] = None
    launch_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    status: str = ProjectStatus.PLANNING.value
    construction_status: int = 0
    total_units: int = 0
    total_area_sqft: Optional[float] = None
    total_land_area_sqft: Optional[float] = None
    amenities: Optional[str] = None
    unit_types: Optional[str] = None
    avg_price_per_sqft: Optional[float] = None
    brochure_url: Optional[str] = None


class ProjectUpdate(BaseModel):
    """Update project."""
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    completion_date: Optional[datetime] = None
    construction_status: Optional[int] = None
    sold_units: Optional[int] = None
    available_units: Optional[int] = None
    avg_price_per_sqft: Optional[float] = None
    brochure_url: Optional[str] = None


class ProjectStatusUpdate(BaseModel):
    """Update project status."""
    status: str
    reason: Optional[str] = None


class ProjectListResponse(BaseModel):
    """Project list response (subset for list view)."""
    id: str
    project_number: str
    name: str
    location: str
    city: str
    status: str
    construction_status: int
    total_units: int
    sold_units: int
    available_units: int
    avg_price_per_sqft: Optional[float]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectResponse(BaseModel):
    """Full project response."""
    id: str
    project_number: str
    name: str
    description: Optional[str]
    location: str
    city: str
    state: str
    postal_code: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    developer_id: Optional[str]
    launch_date: Optional[datetime]
    completion_date: Optional[datetime]
    status: str
    construction_status: int
    total_units: int
    sold_units: int
    available_units: int
    total_area_sqft: Optional[float]
    total_land_area_sqft: Optional[float]
    amenities: Optional[str]
    unit_types: Optional[str]
    avg_price_per_sqft: Optional[float]
    brochure_url: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    # Related data
    blocks: List[BlockResponse] = []

    model_config = {"from_attributes": True}
