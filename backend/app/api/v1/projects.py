from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db_session
from app.dependencies.auth import get_current_user, require_permission
from app.models.project import Project
from app.models.user import User
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
    ProjectStatusUpdate,
    BlockCreate,
    BlockResponse,
    UnitCreate,
    UnitUpdate,
    UnitResponse,
    UnitListResponse,
    UnitStatusUpdate,
    ProjectAmenityCreate,
    ProjectAmenityResponse,
)
from app.services.project_service import ProjectService
from app.utils.filters import SortDirection
from app.utils.pagination import PaginationParams, get_pagination_params
from app.utils.response import ok, created, PaginatedResponse
from loguru import logger

router = APIRouter()


@router.get("/stats/kpis", status_code=status.HTTP_200_OK, response_model=dict)
async def get_project_kpis(
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("projects.view")),
    statuses: str = Query(None, description="Comma-separated project statuses"),
    priorities: str = Query(None, description="Comma-separated priorities (not applicable for projects)"),
    sources: str = Query(None, description="Comma-separated sources (not applicable for projects)"),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get project KPIs with optional status filter."""
    status_values = [s.strip().lower() for s in statuses.split(",") if s.strip()] if statuses else None
    priority_values = [p.strip().lower() for p in priorities.split(",") if p.strip()] if priorities else None
    source_values = [s.strip().lower() for s in sources.split(",") if s.strip()] if sources else None

    filters = [Project.is_deleted == False]

    if status_values:
        filters.append(func.lower(Project.status).in_(status_values))

    query = select(
        func.count(Project.id).label("total_projects"),
        func.count(Project.id).filter(Project.status == "planning").label("planning_projects"),
        func.count(Project.id).filter(Project.status == "ongoing").label("ongoing_projects"),
        func.count(Project.id).filter(Project.status == "completed").label("completed_projects"),
    ).where(and_(*filters))

    row = (await session.execute(query)).one()

    ignored_filters = []
    if priority_values:
        ignored_filters.append("priorities")
    if source_values:
        ignored_filters.append("sources")

    return ok(
        data={
            "total_projects": row.total_projects or 0,
            "planning_projects": row.planning_projects or 0,
            "ongoing_projects": row.ongoing_projects or 0,
            "completed_projects": row.completed_projects or 0,
            "filters_applied": {
                "statuses": status_values,
                "priorities": priority_values,
                "sources": source_values,
                "ignored_filters": ignored_filters,
            },
        }
    )


# ── Project CRUD ──────────────────────────────────────────────────────

@router.post("", status_code=status.HTTP_201_CREATED, response_model=dict)
async def create_project(
    request: ProjectCreate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("projects.create")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Create new project. Requires projects.create permission."""
    service = ProjectService(session)

    project = await service.create_project(
        name=request.name,
        location=request.location,
        city=request.city,
        state=request.state,
        description=request.description,
        postal_code=request.postal_code,
        latitude=request.latitude,
        longitude=request.longitude,
        developer_id=request.developer_id,
        launch_date=request.launch_date,
        completion_date=request.completion_date,
        status=request.status,
        construction_status=request.construction_status,
        total_units=request.total_units,
        total_area_sqft=request.total_area_sqft,
        total_land_area_sqft=request.total_land_area_sqft,
        amenities=request.amenities,
        unit_types=request.unit_types,
        avg_price_per_sqft=request.avg_price_per_sqft,
        brochure_url=request.brochure_url,
        created_by=str(current_user.id),
    )

    await session.commit()

    logger.info(f"Project created | id={project.id} | number={project.project_number} | city={request.city}")

    return created(
        data=ProjectResponse.model_validate(project).__dict__,
        message="Project created successfully.",
    )


@router.get("", status_code=status.HTTP_200_OK, response_model=PaginatedResponse)
async def list_projects(
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("projects.view")),
    pagination: PaginationParams = Depends(get_pagination_params),
    search: str = Query(None),
    statuses: str = Query(None, description="Comma-separated statuses"),
    cities: str = Query(None, description="Comma-separated cities"),
    sort_by: str = Query("created_at"),
    sort_direction: str = Query("desc"),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """List projects with filtering and pagination."""
    service = ProjectService(session)

    projects, total = await service.list_projects(
        search=search,
        statuses=statuses.split(",") if statuses else None,
        cities=cities.split(",") if cities else None,
        skip=pagination.offset,
        limit=pagination.limit,
        sort_by=sort_by,
        sort_direction=SortDirection(sort_direction),
    )

    data = [ProjectListResponse.model_validate(p).__dict__ for p in projects]

    return PaginatedResponse.build(
        data=data,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    ).__dict__


@router.get("/{project_id}", status_code=status.HTTP_200_OK, response_model=dict)
async def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("projects.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get project with all details."""
    service = ProjectService(session)
    project = await service.get_project(project_id)

    return ok(data=ProjectResponse.model_validate(project).__dict__)


@router.patch("/{project_id}", status_code=status.HTTP_200_OK, response_model=dict)
async def update_project(
    project_id: str,
    request: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("projects.edit")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Update project details."""
    service = ProjectService(session)

    project = await service.update_project(project_id, **request.model_dump(exclude_unset=True))

    await session.commit()

    logger.info(f"Project updated | id={project_id} | updated_by={current_user.id}")

    return ok(data=ProjectResponse.model_validate(project).__dict__)


@router.post("/{project_id}/status", status_code=status.HTTP_200_OK, response_model=dict)
async def change_project_status(
    project_id: str,
    request: ProjectStatusUpdate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("projects.edit")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Change project status."""
    service = ProjectService(session)

    project = await service.change_status(project_id, request.status)

    await session.commit()

    logger.info(f"Project status changed | id={project_id} | status={request.status}")

    return ok(data=ProjectResponse.model_validate(project).__dict__)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("projects.delete")),
    session: AsyncSession = Depends(get_db_session),
):
    """Soft delete a project."""
    service = ProjectService(session)
    await service.delete_project(project_id)

    await session.commit()

    logger.info(f"Project deleted | id={project_id} | deleted_by={current_user.id}")

    # FIX: Explicitly return an empty Response
    return Response(status_code=status.HTTP_204_NO_CONTENT)
# ── Block Management ──────────────────────────────────────────────────

@router.post("/{project_id}/blocks", status_code=status.HTTP_201_CREATED, response_model=dict)
async def add_project_block(
    project_id: str,
    request: BlockCreate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("projects.edit")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Add block to project."""
    service = ProjectService(session)

    block = await service.add_block(
        project_id=project_id,
        block_name=request.block_name,
        description=request.description,
        total_units=request.total_units,
        total_floors=request.total_floors,
        created_by=str(current_user.id),
    )

    await session.commit()

    return created(
        data=BlockResponse.model_validate(block).__dict__,
        message="Block added successfully.",
    )


@router.get("/{project_id}/blocks", status_code=status.HTTP_200_OK, response_model=dict)
async def get_project_blocks(
    project_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("projects.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get all blocks in project."""
    service = ProjectService(session)
    blocks = await service.get_blocks(project_id)

    data = [BlockResponse.model_validate(b).__dict__ for b in blocks]

    return ok(data=data)


# ── Unit Management ──────────────────────────────────────────────────

@router.post("/{project_id}/units", status_code=status.HTTP_201_CREATED, response_model=dict)
async def add_unit(
    project_id: str,
    request: UnitCreate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("projects.edit")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Add unit to project."""
    service = ProjectService(session)

    unit = await service.add_unit(
        project_id=project_id,
        floor_id=request.floor_id,
        unit_number=request.unit_number,
        unit_type=request.unit_type,
        carpet_area_sqft=request.carpet_area_sqft,
        built_up_area_sqft=request.built_up_area_sqft,
        price=request.price,
        bedroom_count=request.bedroom_count,
        bathroom_count=request.bathroom_count,
        balcony_count=request.balcony_count,
        furnishing_type=request.furnishing_type,
        facing=request.facing,
        description=request.description,
        amenities=request.amenities,
        images_urls=request.images_urls,
        created_by=str(current_user.id),
    )

    await session.commit()

    return created(
        data=UnitResponse.model_validate(unit).__dict__,
        message="Unit added successfully.",
    )


@router.get("/units", status_code=status.HTTP_200_OK, response_model=PaginatedResponse)
async def list_units(
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("projects.view")),
    pagination: PaginationParams = Depends(get_pagination_params),
    project_id: str = Query(None),
    search: str = Query(None),
    unit_types: str = Query(None, description="Comma-separated unit types"),
    statuses: str = Query(None, description="Comma-separated statuses"),
    min_price: float = Query(None),
    max_price: float = Query(None),
    min_area: float = Query(None),
    max_area: float = Query(None),
    bedrooms: str = Query(None, description="Comma-separated bedroom counts"),
    sort_by: str = Query("created_at"),
    sort_direction: str = Query("desc"),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """List units with advanced filtering."""
    service = ProjectService(session)

    units, total = await service.list_units(
        project_id=project_id,
        search=search,
        unit_types=unit_types.split(",") if unit_types else None,
        statuses=statuses.split(",") if statuses else None,
        min_price=min_price,
        max_price=max_price,
        min_area=min_area,
        max_area=max_area,
        bedrooms=[int(b) for b in bedrooms.split(",")] if bedrooms else None,
        skip=pagination.offset,
        limit=pagination.limit,
        sort_by=sort_by,
        sort_direction=SortDirection(sort_direction),
    )

    data = [UnitListResponse.model_validate(u).__dict__ for u in units]

    return PaginatedResponse.build(
        data=data,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    ).__dict__


@router.get("/{project_id}/units/{unit_id}", status_code=status.HTTP_200_OK, response_model=dict)
async def get_unit(
    project_id: str,
    unit_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("projects.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get unit with all details."""
    service = ProjectService(session)
    unit = await service.get_unit(unit_id)

    return ok(data=UnitResponse.model_validate(unit).__dict__)


@router.patch("/{project_id}/units/{unit_id}", status_code=status.HTTP_200_OK, response_model=dict)
async def update_unit(
    project_id: str,
    unit_id: str,
    request: UnitUpdate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("projects.edit")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Update unit details."""
    service = ProjectService(session)

    unit = await service.update_unit(unit_id, **request.model_dump(exclude_unset=True))

    await session.commit()

    logger.info(f"Unit updated | id={unit_id} | updated_by={current_user.id}")

    return ok(data=UnitResponse.model_validate(unit).__dict__)


@router.post("/{project_id}/units/{unit_id}/status", status_code=status.HTTP_200_OK, response_model=dict)
async def change_unit_status(
    project_id: str,
    unit_id: str,
    request: UnitStatusUpdate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("projects.edit")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Change unit status."""
    service = ProjectService(session)

    unit = await service.change_unit_status(
        unit_id=unit_id,
        new_status=request.status,
        reason=request.reason,
        booking_id=request.booking_id,
        changed_by_user_id=str(current_user.id),
    )

    await session.commit()

    logger.info(f"Unit status changed | id={unit_id} | status={request.status}")

    return ok(data=UnitResponse.model_validate(unit).__dict__)


# ── Statistics ────────────────────────────────────────────────────────

@router.get("/{project_id}/stats", status_code=status.HTTP_200_OK, response_model=dict)
async def get_project_statistics(
    project_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("projects.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get project statistics."""
    service = ProjectService(session)
    stats = await service.get_project_statistics(project_id)

    return ok(data=stats)


@router.get("/stats/overview", status_code=status.HTTP_200_OK, response_model=dict)
async def get_global_statistics(
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("projects.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get global project statistics."""
    service = ProjectService(session)
    stats = await service.get_global_statistics()

    return ok(data=stats)
