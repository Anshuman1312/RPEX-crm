from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db_session
from app.dependencies.auth import get_current_user, require_permission
from app.models.user import User
from app.schemas.lead import (
    LeadCreate,
    LeadUpdate,
    LeadResponse,
    LeadListResponse,
    LeadActivityCreate,
    LeadActivityResponse,
    LeadStatusUpdate,
    LeadAssignRequest,
)
from app.services.lead_service import LeadService
from app.utils.filters import LeadFilterParams, SortDirection
from app.utils.pagination import PaginationParams, get_pagination_params
from app.utils.response import ok, created, PaginatedResponse
from loguru import logger

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED, response_model=dict)
async def create_lead(
    request: LeadCreate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("leads.create")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Create new lead. Requires leads.create permission."""
    lead_service = LeadService(session)

    lead = await lead_service.create_lead(
        full_name=request.full_name,
        email=request.email,
        phone=request.phone,
        source=request.source,
        company_name=request.company_name,
        designation=request.designation,
        budget=request.budget,
        notes=request.notes,
        interested_in_project=request.interested_in_project,
        preferred_unit_type=request.preferred_unit_type,
        assigned_to_user_id=request.assigned_to_user_id,
        created_by=str(current_user.id),
    )

    await session.commit()

    logger.info(f"Lead created | lead_id={lead.id} | lead_number={lead.lead_number} | created_by={current_user.id}")

    return created(
        data=LeadResponse.model_validate(lead).__dict__,
        message="Lead created successfully.",
    )


@router.get("", status_code=status.HTTP_200_OK, response_model=PaginatedResponse)
async def list_leads(
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("leads.view")),
    pagination: PaginationParams = Depends(get_pagination_params),
    search: str = Query(None),
    statuses: str = Query(None, description="Comma-separated statuses"),
    sources: str = Query(None, description="Comma-separated sources"),
    sort_by: str = Query("created_at"),
    sort_direction: str = Query("desc"),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """List leads with filtering and pagination."""
    lead_service = LeadService(session)

    # Parse filter parameters
    filters = LeadFilterParams(
        search=search,
        statuses=statuses.split(",") if statuses else None,
        sources=sources.split(",") if sources else None,
        sort_by=sort_by,
        sort_direction=SortDirection(sort_direction),
    )

    leads, total = await lead_service.list_leads(filters, pagination.offset, pagination.limit)

    data = [LeadListResponse.model_validate(l).__dict__ for l in leads]

    return PaginatedResponse.build(
        data=data,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    ).__dict__


@router.get("/{lead_id}", status_code=status.HTTP_200_OK, response_model=dict)
async def get_lead(
    lead_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("leads.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get lead with all details."""
    lead_service = LeadService(session)
    lead = await lead_service.get_lead(lead_id)

    return ok(data=LeadResponse.model_validate(lead).__dict__)


@router.patch("/{lead_id}", status_code=status.HTTP_200_OK, response_model=dict)
async def update_lead(
    lead_id: str,
    request: LeadUpdate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("leads.edit")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Update lead details."""
    lead_service = LeadService(session)

    lead = await lead_service.update_lead(lead_id, **request.model_dump(exclude_unset=True))

    await session.commit()

    logger.info(f"Lead updated | lead_id={lead.id} | updated_by={current_user.id}")

    return ok(data=LeadResponse.model_validate(lead).__dict__)


@router.post("/{lead_id}/status", status_code=status.HTTP_200_OK, response_model=dict)
async def update_lead_status(
    lead_id: str,
    request: LeadStatusUpdate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("leads.edit")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Update lead status (transition through workflow)."""
    lead_service = LeadService(session)

    lead = await lead_service.transition_status(lead_id, request.status, request.notes)

    await session.commit()

    logger.info(f"Lead status changed | lead_id={lead.id} | status={request.status} | changed_by={current_user.id}")

    return ok(data=LeadResponse.model_validate(lead).__dict__)


@router.post("/{lead_id}/assign", status_code=status.HTTP_200_OK, response_model=dict)
async def assign_lead(
    lead_id: str,
    request: LeadAssignRequest,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("leads.assign")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Assign lead to a user."""
    lead_service = LeadService(session)

    lead = await lead_service.assign_lead(
        lead_id,
        request.assigned_to_user_id,
        assigned_by_user_id=str(current_user.id),
        notes=request.notes,
    )

    await session.commit()

    logger.info(
        f"Lead assigned | lead_id={lead.id} | assigned_to={request.assigned_to_user_id} | assigned_by={current_user.id}"
    )

    return ok(data=LeadResponse.model_validate(lead).__dict__)


@router.post("/{lead_id}/activities", status_code=status.HTTP_201_CREATED, response_model=dict)
async def add_lead_activity(
    lead_id: str,
    request: LeadActivityCreate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("leads.activity")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Add activity to lead."""
    lead_service = LeadService(session)

    activity = await lead_service.add_activity(
        lead_id,
        activity_type=request.activity_type,
        subject=request.subject,
        description=request.description,
        outcome=request.outcome,
        activity_date=request.activity_date,
        next_followup=request.next_followup,
        performed_by_user_id=str(current_user.id),
    )

    await session.commit()

    logger.info(f"Lead activity added | lead_id={lead_id} | activity_type={request.activity_type} | by={current_user.id}")

    return created(
        data=LeadActivityResponse.model_validate(activity).__dict__,
        message="Activity added successfully.",
    )


@router.get("/{lead_id}/activities", status_code=status.HTTP_200_OK, response_model=PaginatedResponse)
async def get_lead_activities(
    lead_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("leads.view")),
    pagination: PaginationParams = Depends(get_pagination_params),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get activities for a lead."""
    from app.repositories.lead_repository import LeadActivityRepository

    activity_repo = LeadActivityRepository(session)
    activities, total = await activity_repo.get_lead_activities(lead_id, pagination.offset, pagination.limit)

    data = [LeadActivityResponse.model_validate(a).__dict__ for a in activities]

    return PaginatedResponse.build(
        data=data,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    ).__dict__


@router.get("/stats/overview", status_code=status.HTTP_200_OK, response_model=dict)
async def get_lead_statistics(
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("leads.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get lead statistics (counts by status, source, etc.)."""
    lead_service = LeadService(session)
    stats = await lead_service.get_lead_statistics()

    return ok(data=stats)


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def delete_lead(
    lead_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("leads.delete")),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    """Soft delete a lead."""
    lead_service = LeadService(session)
    await lead_service.delete_lead(lead_id)

    await session.commit()

    logger.info(f"Lead deleted | lead_id={lead_id} | deleted_by={current_user.id}")
