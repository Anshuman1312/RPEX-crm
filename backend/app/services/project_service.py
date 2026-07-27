from __future__ import annotations

from datetime import datetime
from typing import Optional, List, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project, Block, Building, Floor, Unit, UnitAvailabilityLog, ProjectAmenity
from app.repositories.project_repository import (
    ProjectRepository,
    BlockRepository,
    BuildingRepository,
    FloorRepository,
    UnitRepository,
    UnitAvailabilityLogRepository,
    ProjectAmenityRepository,
)
from app.utils.filters import SortDirection
from app.utils.numbering import NumberingService
from app.core.exceptions import (
    ConflictException,
    NotFoundException,
    ValidationException,
)
from loguru import logger


class ProjectService:
    """Service for project management business logic."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.project_repo = ProjectRepository(session)
        self.block_repo = BlockRepository(session)
        self.building_repo = BuildingRepository(session)
        self.floor_repo = FloorRepository(session)
        self.unit_repo = UnitRepository(session)
        self.amenity_repo = ProjectAmenityRepository(session)
        self.availability_log_repo = UnitAvailabilityLogRepository(session)
        self.numbering_service = NumberingService(session)

    # ── Project CRUD ──────────────────────────────────────────────────────

    async def create_project(
        self,
        name: str,
        location: str,
        city: str,
        state: str,
        description: Optional[str] = None,
        postal_code: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        developer_id: Optional[str] = None,
        launch_date: Optional[datetime] = None,
        completion_date: Optional[datetime] = None,
        status: str = "PLANNING",
        construction_status: int = 0,
        total_units: int = 0,
        total_area_sqft: Optional[float] = None,
        total_land_area_sqft: Optional[float] = None,
        amenities: Optional[str] = None,
        unit_types: Optional[str] = None,
        avg_price_per_sqft: Optional[float] = None,
        brochure_url: Optional[str] = None,
        created_by: str = "system",
    ) -> Project:
        """Create new project."""
        # Generate project number
        project_number = await self.numbering_service.get_next_number("PROJ")

        project = Project(
            project_number=project_number,
            name=name,
            location=location,
            city=city,
            state=state,
            description=description,
            postal_code=postal_code,
            latitude=latitude,
            longitude=longitude,
            developer_id=developer_id,
            launch_date=launch_date,
            completion_date=completion_date,
            status=status,
            construction_status=construction_status,
            total_units=total_units,
            total_area_sqft=total_area_sqft,
            total_land_area_sqft=total_land_area_sqft,
            amenities=amenities,
            unit_types=unit_types,
            avg_price_per_sqft=avg_price_per_sqft,
            brochure_url=brochure_url,
            created_by=created_by,
        )

        self.session.add(project)
        await self.session.flush()

        logger.info(f"Project created | id={project.id} | number={project_number} | city={city}")

        return project

    async def get_project(self, project_id: str) -> Project:
        """Get project by ID with blocks."""
        project = await self.project_repo.get_with_blocks(project_id)
        if not project or project.is_deleted:
            raise NotFoundException(f"Project {project_id} not found")
        return project

    async def list_projects(
        self,
        search: Optional[str] = None,
        statuses: Optional[List[str]] = None,
        cities: Optional[List[str]] = None,
        skip: int = 0,
        limit: int = 50,
        sort_by: str = "created_at",
        sort_direction: SortDirection = SortDirection.DESC,
    ) -> Tuple[List[Project], int]:
        """List projects with filtering."""
        return await self.project_repo.list_with_filter(
            search=search,
            statuses=statuses,
            cities=cities,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_direction=sort_direction,
        )

    async def update_project(self, project_id: str, **kwargs) -> Project:
        """Update project fields."""
        project = await self.project_repo.get_by_id(project_id)
        if not project or project.is_deleted:
            raise NotFoundException(f"Project {project_id} not found")

        # Update allowed fields
        allowed_fields = {
            "name", "description", "location", "city", "state", "postal_code",
            "latitude", "longitude", "completion_date", "construction_status",
            "sold_units", "available_units", "avg_price_per_sqft", "brochure_url"
        }

        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                setattr(project, field, value)

        project.updated_at = datetime.utcnow()

        logger.info(f"Project updated | id={project_id}")

        return project

    async def change_status(self, project_id: str, status: str) -> Project:
        """Change project status."""
        project = await self.project_repo.get_by_id(project_id)
        if not project or project.is_deleted:
            raise NotFoundException(f"Project {project_id} not found")

        old_status = project.status
        project.status = status
        project.updated_at = datetime.utcnow()

        logger.info(f"Project status changed | id={project_id} | {old_status} → {status}")

        return project

    async def delete_project(self, project_id: str) -> None:
        """Soft delete a project."""
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundException(f"Project {project_id} not found")

        await self.project_repo.soft_delete(project_id)

        logger.info(f"Project deleted | id={project_id}")

    # ── Block Management ──────────────────────────────────────────────────

    async def add_block(
        self,
        project_id: str,
        block_name: str,
        description: Optional[str] = None,
        total_units: int = 0,
        total_floors: int = 0,
        created_by: str = "system",
    ) -> Block:
        """Add block to project."""
        project = await self.project_repo.get_by_id(project_id)
        if not project or project.is_deleted:
            raise NotFoundException(f"Project {project_id} not found")

        block = Block(
            project_id=project_id,
            block_name=block_name,
            description=description,
            total_units=total_units,
            total_floors=total_floors,
            created_by=created_by,
        )

        self.session.add(block)

        logger.info(f"Block added | project_id={project_id} | name={block_name}")

        return block

    async def get_blocks(self, project_id: str) -> List[Block]:
        """Get all blocks in a project."""
        project = await self.project_repo.get_by_id(project_id)
        if not project or project.is_deleted:
            raise NotFoundException(f"Project {project_id} not found")

        return await self.block_repo.get_project_blocks(project_id)

    # ── Unit Management ──────────────────────────────────────────────────

    async def add_unit(
        self,
        project_id: str,
        floor_id: str,
        unit_number: str,
        unit_type: str,
        carpet_area_sqft: float,
        built_up_area_sqft: float,
        price: float,
        bedroom_count: Optional[int] = None,
        bathroom_count: Optional[int] = None,
        balcony_count: int = 0,
        furnishing_type: Optional[str] = None,
        facing: Optional[str] = None,
        description: Optional[str] = None,
        amenities: Optional[str] = None,
        images_urls: Optional[str] = None,
        created_by: str = "system",
    ) -> Unit:
        """Add unit to project."""
        project = await self.project_repo.get_by_id(project_id)
        if not project or project.is_deleted:
            raise NotFoundException(f"Project {project_id} not found")

        floor = await self.floor_repo.get_by_id(floor_id)
        if not floor:
            raise NotFoundException(f"Floor {floor_id} not found")

        # Check for duplicate unit number
        existing = await self.unit_repo.get_by_unit_number(project_id, unit_number)
        if existing:
            raise ConflictException(f"Unit {unit_number} already exists in this project")

        unit = Unit(
            project_id=project_id,
            floor_id=floor_id,
            unit_number=unit_number,
            unit_type=unit_type,
            bedroom_count=bedroom_count,
            bathroom_count=bathroom_count,
            balcony_count=balcony_count,
            carpet_area_sqft=carpet_area_sqft,
            built_up_area_sqft=built_up_area_sqft,
            price=price,
            furnishing_type=furnishing_type,
            facing=facing,
            description=description,
            amenities=amenities,
            images_urls=images_urls,
            created_by=created_by,
        )

        self.session.add(unit)

        logger.info(f"Unit added | project_id={project_id} | unit={unit_number}")

        return unit

    async def get_unit(self, unit_id: str) -> Unit:
        """Get unit with availability logs."""
        unit = await self.unit_repo.get_with_logs(unit_id)
        if not unit:
            raise NotFoundException(f"Unit {unit_id} not found")
        return unit

    async def list_units(
        self,
        project_id: Optional[str] = None,
        search: Optional[str] = None,
        unit_types: Optional[List[str]] = None,
        statuses: Optional[List[str]] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_area: Optional[float] = None,
        max_area: Optional[float] = None,
        bedrooms: Optional[List[int]] = None,
        skip: int = 0,
        limit: int = 50,
        sort_by: str = "created_at",
        sort_direction: SortDirection = SortDirection.DESC,
    ) -> Tuple[List[Unit], int]:
        """List units with advanced filtering."""
        return await self.unit_repo.list_with_filter(
            project_id=project_id,
            search=search,
            unit_types=unit_types,
            statuses=statuses,
            min_price=min_price,
            max_price=max_price,
            min_area=min_area,
            max_area=max_area,
            bedrooms=bedrooms,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_direction=sort_direction,
        )

    async def update_unit(self, unit_id: str, **kwargs) -> Unit:
        """Update unit details."""
        unit = await self.unit_repo.get_by_id(unit_id)
        if not unit:
            raise NotFoundException(f"Unit {unit_id} not found")

        allowed_fields = {
            "bedroom_count", "bathroom_count", "balcony_count",
            "carpet_area_sqft", "built_up_area_sqft", "price",
            "furnishing_type", "facing", "description", "amenities", "images_urls"
        }

        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                setattr(unit, field, value)

        unit.updated_at = datetime.utcnow()

        logger.info(f"Unit updated | id={unit_id}")

        return unit

    async def change_unit_status(
        self,
        unit_id: str,
        new_status: str,
        reason: Optional[str] = None,
        booking_id: Optional[str] = None,
        changed_by_user_id: str = "system",
    ) -> Unit:
        """Change unit status and create availability log."""
        unit = await self.unit_repo.get_by_id(unit_id)
        if not unit:
            raise NotFoundException(f"Unit {unit_id} not found")

        old_status = unit.status
        unit.status = new_status
        unit.updated_at = datetime.utcnow()

        # Create availability log
        log = UnitAvailabilityLog(
            unit_id=unit_id,
            old_status=old_status,
            new_status=new_status,
            changed_by_user_id=changed_by_user_id,
            reason=reason,
            related_booking_id=booking_id,
            created_by=changed_by_user_id,
        )

        self.session.add(log)

        logger.info(f"Unit status changed | id={unit_id} | {old_status} → {new_status}")

        return unit

    # ── Statistics ────────────────────────────────────────────────────────

    async def get_project_statistics(self, project_id: str) -> dict:
        """Get project statistics."""
        project = await self.project_repo.get_by_id(project_id)
        if not project or project.is_deleted:
            raise NotFoundException(f"Project {project_id} not found")

        units_by_status = await self.unit_repo.count_by_status(project_id)
        units_by_type = await self.unit_repo.count_by_type(project_id)

        return {
            "project_id": str(project.id),
            "total_units": project.total_units,
            "sold_units": project.sold_units,
            "available_units": project.available_units,
            "units_by_status": units_by_status,
            "units_by_type": units_by_type,
            "construction_status": project.construction_status,
            "avg_price_per_sqft": float(project.avg_price_per_sqft) if project.avg_price_per_sqft else None,
        }

    async def get_global_statistics(self) -> dict:
        """Get global project statistics."""
        by_status = await self.project_repo.count_by_status()
        by_city = await self.project_repo.count_by_city()

        return {
            "by_status": by_status,
            "by_city": by_city,
            "total": sum(by_status.values()),
        }
