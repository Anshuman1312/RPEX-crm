from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, Boolean, Numeric, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.database.base import Base
from app.models.mixins import BaseModelMixin, PrimaryKeyMixin, TimestampMixin
from app.utils.enums import ProjectStatus, UnitStatus, UnitType


class Project(Base, BaseModelMixin, PrimaryKeyMixin, TimestampMixin):
    """
    Real estate project entity.
    
    Attributes:
        project_number: Unique sequential ID (PROJ-000001)
        name: Project name
        description: Project description
        location: Project location/address
        city: City
        state: State
        postal_code: Zip code
        latitude/longitude: Geographic coordinates
        developer_id: FK to Company/Vendor
        launch_date: Project launch date
        completion_date: Expected completion date
        status: PLANNING/APPROVED/ONGOING/COMPLETED/CANCELLED
        construction_status: Percentage complete (0-100)
        total_units: Total units in project
        sold_units: Units sold
        available_units: Available units
        total_area_sqft: Total built-up area
        total_land_area_sqft: Land area
        amenities: JSON array of amenities
        unit_types: JSON array of unit types available
        avg_price_per_sqft: Average price per sqft
        brochure_url: Project brochure
        relationships:
            blocks: Block[] - Blocks/wings in project
            units: Unit[] - All units
            bookings: Booking[] - Bookings
    """

    __tablename__ = "projects"

    # ── Identifiers ────────────────────────────────────────────────────────
    project_number = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # ── Location ───────────────────────────────────────────────────────────
    location = Column(String(500), nullable=False)
    city = Column(String(100), nullable=False, index=True)
    state = Column(String(100), nullable=False)
    postal_code = Column(String(20), nullable=True)
    latitude = Column(Numeric(10, 8), nullable=True)
    longitude = Column(Numeric(11, 8), nullable=True)
    
    # ── Developer & Timeline ──────────────────────────────────────────────
    developer_id = Column(PG_UUID(as_uuid=True), ForeignKey("vendors.id", ondelete="SET NULL"), nullable=True)
    launch_date = Column(DateTime, nullable=True)
    completion_date = Column(DateTime, nullable=True)
    
    # ── Status & Progress ────────────────────────────────────────────────────
    status = Column(String(50), nullable=False, default=ProjectStatus.PLANNING.value, index=True)
    construction_status = Column(Integer, default=0)  # 0-100 percentage
    
    # ── Units ──────────────────────────────────────────────────────────────
    total_units = Column(Integer, default=0)
    sold_units = Column(Integer, default=0)
    available_units = Column(Integer, default=0)
    
    # ── Area ───────────────────────────────────────────────────────────────
    total_area_sqft = Column(Numeric(12, 2), nullable=True)
    total_land_area_sqft = Column(Numeric(12, 2), nullable=True)
    
    # ── Features & Pricing ────────────────────────────────────────────────
    amenities = Column(String(2000), nullable=True)  # JSON array as string
    unit_types = Column(String(500), nullable=True)   # JSON array as string
    avg_price_per_sqft = Column(Numeric(10, 2), nullable=True)
    brochure_url = Column(String(500), nullable=True)
    
    # ── Relationships ──────────────────────────────────────────────────────
    blocks = relationship(
        "Block",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="select"
    )
    units = relationship(
        "Unit",
        back_populates="project",
        foreign_keys="Unit.project_id",
        lazy="select"
    )
    
    def __repr__(self) -> str:
        return f"<Project {self.project_number}: {self.name}>"


class Block(Base, BaseModelMixin, PrimaryKeyMixin, TimestampMixin):
    """
    Block/Wing within a project.
    
    Attributes:
        project_id: FK to Project
        block_name: Block name (A, B, Tower 1, etc.)
        description: Block description
        total_units: Units in this block
        total_floors: Number of floors
        construction_status: Percentage complete
        status: PLANNING/APPROVED/ONGOING/COMPLETED/CANCELLED
        relationships:
            project: Project - Parent project
            buildings: Building[] - Buildings in block
    """

    __tablename__ = "blocks"

    project_id = Column(PG_UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    
    block_name = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    
    total_units = Column(Integer, default=0)
    total_floors = Column(Integer, default=0)
    construction_status = Column(Integer, default=0)  # 0-100
    status = Column(String(50), nullable=False, default=ProjectStatus.PLANNING.value)
    
    # ── Relationships ──────────────────────────────────────────────────────
    project = relationship("Project", back_populates="blocks")
    buildings = relationship(
        "Building",
        back_populates="block",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    def __repr__(self) -> str:
        return f"<Block {self.block_name}>"


class Building(Base, BaseModelMixin, PrimaryKeyMixin, TimestampMixin):
    """
    Building within a block.
    
    Attributes:
        block_id: FK to Block
        building_name: Building identifier
        total_floors: Number of floors
        units_per_floor: Units on each floor
        status: PLANNING/APPROVED/ONGOING/COMPLETED/CANCELLED
        relationships:
            block: Block - Parent block
            floors: Floor[] - Floors in building
    """

    __tablename__ = "buildings"

    block_id = Column(PG_UUID(as_uuid=True), ForeignKey("blocks.id", ondelete="CASCADE"), nullable=False, index=True)
    
    building_name = Column(String(50), nullable=False)
    total_floors = Column(Integer, default=0)
    units_per_floor = Column(Integer, default=0)
    status = Column(String(50), nullable=False, default=ProjectStatus.PLANNING.value)
    
    # ── Relationships ──────────────────────────────────────────────────────
    block = relationship("Block", back_populates="buildings")
    floors = relationship(
        "Floor",
        back_populates="building",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    def __repr__(self) -> str:
        return f"<Building {self.building_name}>"


class Floor(Base, BaseModelMixin, PrimaryKeyMixin, TimestampMixin):
    """
    Floor within a building.
    
    Attributes:
        building_id: FK to Building
        floor_number: Floor number
        total_units: Units on this floor
        status: PLANNING/APPROVED/ONGOING/COMPLETED/CANCELLED
        relationships:
            building: Building - Parent building
            units: Unit[] - Units on floor
    """

    __tablename__ = "floors"

    building_id = Column(PG_UUID(as_uuid=True), ForeignKey("buildings.id", ondelete="CASCADE"), nullable=False, index=True)
    
    floor_number = Column(Integer, nullable=False)
    total_units = Column(Integer, default=0)
    status = Column(String(50), nullable=False, default=ProjectStatus.PLANNING.value)
    
    # ── Relationships ──────────────────────────────────────────────────────
    building = relationship("Building", back_populates="floors")
    units = relationship(
        "Unit",
        back_populates="floor",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    def __repr__(self) -> str:
        return f"<Floor {self.floor_number}>"


class Unit(Base, BaseModelMixin, PrimaryKeyMixin, TimestampMixin):
    """
    Individual property unit.
    
    Attributes:
        project_id: FK to Project
        floor_id: FK to Floor
        unit_number: Unit identifier (101, 102, etc.)
        unit_type: FLAT/VILLA/PLOT/COMMERCIAL
        bedroom_count: Number of bedrooms
        bathroom_count: Number of bathrooms
        balcony_count: Number of balconies
        carpet_area_sqft: Carpet area
        built_up_area_sqft: Built-up area
        price: Unit price
        status: AVAILABLE/SOLD/RESERVED/HOLD/UNDER_OFFER/CANCELLED
        furnishing_type: UNFURNISHED/SEMI_FURNISHED/FULLY_FURNISHED
        facing: NORTH/SOUTH/EAST/WEST/NE/NW/SE/SW
        description: Unit description
        amenities: JSON array of amenities
        images_urls: JSON array of image URLs
        relationships:
            project: Project - Parent project
            floor: Floor - Parent floor
            booking: Booking - Booking (if booked)
            availability_logs: UnitAvailabilityLog[] - Status change history
    """

    __tablename__ = "units"

    # ── Foreign Keys ───────────────────────────────────────────────────────
    project_id = Column(PG_UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    floor_id = Column(PG_UUID(as_uuid=True), ForeignKey("floors.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # ── Identifiers ────────────────────────────────────────────────────────
    unit_number = Column(String(50), nullable=False)
    unit_type = Column(String(50), nullable=False, index=True)  # FLAT/VILLA/PLOT/COMMERCIAL
    
    # ── Configuration ──────────────────────────────────────────────────────
    bedroom_count = Column(Integer, nullable=True)
    bathroom_count = Column(Integer, nullable=True)
    balcony_count = Column(Integer, default=0)
    
    # ── Dimensions ────────────────────────────────────────────────────────
    carpet_area_sqft = Column(Numeric(10, 2), nullable=False)
    built_up_area_sqft = Column(Numeric(10, 2), nullable=False)
    
    # ── Pricing ────────────────────────────────────────────────────────────
    price = Column(Numeric(15, 2), nullable=False)
    
    # ── Status ────────────────────────────────────────────────────────────
    status = Column(String(50), nullable=False, default=UnitStatus.AVAILABLE.value, index=True)
    furnishing_type = Column(String(50), nullable=True)  # UNFURNISHED/SEMI_FURNISHED/FULLY_FURNISHED
    facing = Column(String(50), nullable=True)  # NORTH/SOUTH/EAST/WEST/NE/NW/SE/SW
    
    # ── Details ────────────────────────────────────────────────────────────
    description = Column(Text, nullable=True)
    amenities = Column(String(1000), nullable=True)  # JSON array as string
    images_urls = Column(String(2000), nullable=True)  # JSON array as string
    
    # ── Relationships ──────────────────────────────────────────────────────
    project = relationship("Project", back_populates="units", foreign_keys=[project_id])
    floor = relationship("Floor", back_populates="units")
    availability_logs = relationship(
        "UnitAvailabilityLog",
        back_populates="unit",
        cascade="all, delete-orphan",
        lazy="select"
    )
    bookings = relationship(
        "Booking",
        back_populates="unit",
        foreign_keys="Booking.unit_id",
        lazy="select",
    )
    
    def __repr__(self) -> str:
        return f"<Unit {self.unit_number}: {self.unit_type}>"


class UnitAvailabilityLog(Base, BaseModelMixin, PrimaryKeyMixin, TimestampMixin):
    """
    Tracks unit status changes for audit trail.
    
    Attributes:
        unit_id: FK to Unit
        old_status: Previous status
        new_status: New status
        changed_by_user_id: FK to User who changed status
        reason: Reason for change
        related_booking_id: FK to Booking (if applicable)
        relationships:
            unit: Unit - Parent unit
            changed_by_user: User - User who made change
    """

    __tablename__ = "unit_availability_logs"

    unit_id = Column(PG_UUID(as_uuid=True), ForeignKey("units.id", ondelete="CASCADE"), nullable=False, index=True)
    
    old_status = Column(String(50), nullable=True)
    new_status = Column(String(50), nullable=False)
    changed_by_user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reason = Column(String(500), nullable=True)
    related_booking_id = Column(PG_UUID(as_uuid=True), ForeignKey("bookings.id", ondelete="SET NULL"), nullable=True)
    
    # ── Relationships ──────────────────────────────────────────────────────
    unit = relationship("Unit", back_populates="availability_logs")
    changed_by_user = relationship("User", foreign_keys=[changed_by_user_id], lazy="select")
    
    def __repr__(self) -> str:
        return f"<UnitAvailabilityLog {self.unit_id}: {self.old_status}→{self.new_status}>"


class ProjectAmenity(Base, BaseModelMixin, PrimaryKeyMixin, TimestampMixin):
    """
    Amenities available in project.
    
    Attributes:
        project_id: FK to Project
        amenity_type: GYM/POOL/SECURITY/PARKING/GARDEN/CLUBHOUSE/PLAYGROUND/LIBRARY
        description: Amenity description
        status: PLANNED/ACTIVE/INACTIVE
    """

    __tablename__ = "project_amenities"

    project_id = Column(PG_UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    
    amenity_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="ACTIVE")
    
    def __repr__(self) -> str:
        return f"<ProjectAmenity {self.amenity_type}>"
