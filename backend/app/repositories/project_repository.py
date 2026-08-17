from __future__ import annotations

from datetime import datetime
from typing import Optional, List, Tuple

from sqlalchemy import and_, or_, func, select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.project import Project, Block, Building, Floor, Unit, UnitAvailabilityLog, ProjectAmenity
from app.repositories.base import BaseRepository
from app.utils.filters import SortDirection


class ProjectRepository(BaseRepository[Project]):
    """Repository for Project entity with advanced filtering."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Project)

    async def get_by_project_number(self, project_number: str) -> Optional[Project]:
        """Get project by project number."""
        stmt = select(Project).where(Project.project_number == project_number)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_name(self, name: str) -> Optional[Project]:
        """Get project by name."""
        stmt = select(Project).where(Project.name.ilike(f"%{name}%"))
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_city(self, city: str) -> List[Project]:
        """Get all projects in a city."""
        stmt = (
            select(Project)
            .where(and_(Project.city == city, Project.is_deleted == False))
            .order_by(Project.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_with_blocks(self, project_id: str) -> Optional[Project]:
        """Get project with blocks (eager loading)."""
        stmt = (
            select(Project)
            .where(Project.id == project_id)
            .options(selectinload(Project.blocks))
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_with_filter(
        self,
        search: Optional[str] = None,
        statuses: Optional[List[str]] = None,
        cities: Optional[List[str]] = None,
        skip: int = 0,
        limit: int = 50,
        sort_by: str = "created_at",
        sort_direction: SortDirection = SortDirection.DESC,
    ) -> Tuple[List[Project], int]:
        """
        List projects with advanced filtering.
        
        Args:
            search: Search by name, location, city
            statuses: Filter by status
            cities: Filter by city
            skip: Pagination offset
            limit: Pagination limit
            sort_by: Sort column
            sort_direction: ASC or DESC
            
        Returns:
            Tuple of (projects, total_count)
        """
        filters = []

        # Text search
        if search:
            search_pattern = f"%{search}%"
            filters.append(
                or_(
                    Project.name.ilike(search_pattern),
                    Project.location.ilike(search_pattern),
                    Project.city.ilike(search_pattern),
                    Project.project_number.ilike(search_pattern),
                )
            )

        # Status filter
        if statuses:
            filters.append(Project.status.in_(statuses))

        # City filter
        if cities:
            filters.append(Project.city.in_(cities))

        # Soft delete
        filters.append(Project.is_deleted == False)

        # Count total
        count_stmt = select(func.count()).select_from(Project)
        if filters:
            count_stmt = count_stmt.where(and_(*filters))
        total = await self.session.scalar(count_stmt)

        # Fetch paginated results
        stmt = select(Project).where(and_(*filters) if filters else True)

        # Sort
        sort_column = getattr(Project, sort_by, Project.created_at)
        if sort_direction == SortDirection.ASC:
            stmt = stmt.order_by(sort_column.asc())
        else:
            stmt = stmt.order_by(sort_column.desc())

        stmt = stmt.offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        projects = result.scalars().all()

        return projects, total or 0

    async def get_by_status(self, status: str) -> List[Project]:
        """Get all projects with specific status."""
        stmt = (
            select(Project)
            .where(and_(Project.status == status, Project.is_deleted == False))
            .order_by(Project.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_by_status(self) -> dict:
        """Get count of projects by status."""
        stmt = (
            select(Project.status, func.count(Project.id).label("count"))
            .where(Project.is_deleted == False)
            .group_by(Project.status)
        )
        result = await self.session.execute(stmt)
        rows = result.all()
        return {status: count for status, count in rows}

    async def count_by_city(self) -> dict:
        """Get count of projects by city."""
        stmt = (
            select(Project.city, func.count(Project.id).label("count"))
            .where(Project.is_deleted == False)
            .group_by(Project.city)
        )
        result = await self.session.execute(stmt)
        rows = result.all()
        return {city: count for city, count in rows}


class BlockRepository(BaseRepository[Block]):
    """Repository for Block entity."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Block)

    async def get_project_blocks(self, project_id: str) -> List[Block]:
        """Get all blocks in a project."""
        stmt = (
            select(Block)
            .where(Block.project_id == project_id)
            .order_by(Block.created_at.asc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_project_and_name(self, project_id: str, block_name: str) -> Optional[Block]:
        """Get block by project and name."""
        stmt = select(Block).where(
            and_(
                Block.project_id == project_id,
                Block.block_name == block_name,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()


class BuildingRepository(BaseRepository[Building]):
    """Repository for Building entity."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Building)

    async def get_block_buildings(self, block_id: str) -> List[Building]:
        """Get all buildings in a block."""
        stmt = (
            select(Building)
            .where(Building.block_id == block_id)
            .order_by(Building.created_at.asc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


class FloorRepository(BaseRepository[Floor]):
    """Repository for Floor entity."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Floor)

    async def get_building_floors(self, building_id: str) -> List[Floor]:
        """Get all floors in a building."""
        stmt = (
            select(Floor)
            .where(Floor.building_id == building_id)
            .order_by(Floor.floor_number.asc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_building_and_number(self, building_id: str, floor_number: int) -> Optional[Floor]:
        """Get floor by building and floor number."""
        stmt = select(Floor).where(
            and_(
                Floor.building_id == building_id,
                Floor.floor_number == floor_number,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()


class UnitRepository(BaseRepository[Unit]):
    """Repository for Unit entity with advanced filtering."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Unit)

    async def get_by_unit_number(self, project_id: str, unit_number: str) -> Optional[Unit]:
        """Get unit by project and unit number."""
        stmt = select(Unit).where(
            and_(
                Unit.project_id == project_id,
                Unit.unit_number == unit_number,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_floor(self, floor_id: str) -> List[Unit]:
        """Get all units on a floor."""
        stmt = (
            select(Unit)
            .where(Unit.floor_id == floor_id)
            .order_by(Unit.unit_number.asc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_project_units(self, project_id: str) -> List[Unit]:
        """Get all units in a project."""
        stmt = (
            select(Unit)
            .where(Unit.project_id == project_id)
            .order_by(Unit.unit_number.asc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_with_logs(self, unit_id: str) -> Optional[Unit]:
        """Get unit with availability logs (eager loading)."""
        stmt = (
            select(Unit)
            .where(Unit.id == unit_id)
            .options(selectinload(Unit.availability_logs))
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_with_filter(
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
        """
        List units with advanced filtering.
        
        Args:
            project_id: Filter by project
            search: Search by unit number
            unit_types: Filter by type (FLAT, VILLA, etc.)
            statuses: Filter by status (AVAILABLE, SOLD, etc.)
            min_price/max_price: Price range
            min_area/max_area: Area range in sqft
            bedrooms: Filter by bedroom count
            skip: Pagination offset
            limit: Pagination limit
            sort_by: Sort column
            sort_direction: ASC or DESC
            
        Returns:
            Tuple of (units, total_count)
        """
        filters = []

        if project_id:
            filters.append(Unit.project_id == project_id)

        if search:
            filters.append(Unit.unit_number.ilike(f"%{search}%"))

        if unit_types:
            filters.append(Unit.unit_type.in_(unit_types))

        if statuses:
            filters.append(Unit.status.in_(statuses))

        if min_price:
            filters.append(Unit.price >= min_price)

        if max_price:
            filters.append(Unit.price <= max_price)

        if min_area:
            filters.append(Unit.carpet_area_sqft >= min_area)

        if max_area:
            filters.append(Unit.carpet_area_sqft <= max_area)

        if bedrooms:
            filters.append(Unit.bedroom_count.in_(bedrooms))

        # Count total
        count_stmt = select(func.count()).select_from(Unit)
        if filters:
            count_stmt = count_stmt.where(and_(*filters))
        total = await self.session.scalar(count_stmt)

        # Fetch paginated results
        stmt = select(Unit).where(and_(*filters) if filters else True)

        # Sort
        sort_column = getattr(Unit, sort_by, Unit.created_at)
        if sort_direction == SortDirection.ASC:
            stmt = stmt.order_by(sort_column.asc())
        else:
            stmt = stmt.order_by(sort_column.desc())

        stmt = stmt.offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        units = result.scalars().all()

        return units, total or 0

    async def count_by_status(self, project_id: str) -> dict:
        """Get count of units by status in a project."""
        stmt = (
            select(Unit.status, func.count(Unit.id).label("count"))
            .where(Unit.project_id == project_id)
            .group_by(Unit.status)
        )
        result = await self.session.execute(stmt)
        rows = result.all()
        return {status: count for status, count in rows}

    async def count_by_type(self, project_id: str) -> dict:
        """Get count of units by type in a project."""
        stmt = (
            select(Unit.unit_type, func.count(Unit.id).label("count"))
            .where(Unit.project_id == project_id)
            .group_by(Unit.unit_type)
        )
        result = await self.session.execute(stmt)
        rows = result.all()
        return {utype: count for utype, count in rows}


class UnitAvailabilityLogRepository(BaseRepository[UnitAvailabilityLog]):
    """Repository for Unit Availability Log."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, UnitAvailabilityLog)

    async def get_unit_logs(self, unit_id: str) -> List[UnitAvailabilityLog]:
        """Get all logs for a unit."""
        stmt = (
            select(UnitAvailabilityLog)
            .where(UnitAvailabilityLog.unit_id == unit_id)
            .order_by(UnitAvailabilityLog.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


class ProjectAmenityRepository(BaseRepository[ProjectAmenity]):
    """Repository for Project Amenities."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, ProjectAmenity)

    async def get_project_amenities(self, project_id: str) -> List[ProjectAmenity]:
        """Get all amenities for a project."""
        stmt = (
            select(ProjectAmenity)
            .where(ProjectAmenity.project_id == project_id)
            .order_by(ProjectAmenity.created_at.asc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_type(self, project_id: str, amenity_type: str) -> Optional[ProjectAmenity]:
        """Get amenity by type."""
        stmt = select(ProjectAmenity).where(
            and_(
                ProjectAmenity.project_id == project_id,
                ProjectAmenity.amenity_type == amenity_type,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()
