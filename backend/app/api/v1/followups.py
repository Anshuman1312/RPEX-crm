"""
FastAPI routes for follow-up management.

Endpoints:
- Follow-up CRUD: POST/GET/PATCH/DELETE
- Status management: POST /status
- Task management: POST/GET tasks
- Outcome tracking: POST/GET outcomes
- Assignment: POST /assign
- Statistics: GET /stats
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db_session
from app.dependencies.auth import get_current_user, require_permission
from app.models.followup import FollowUp
from app.models.lead import Lead
from app.models.user import User
from app.schemas.followup import (
    FollowUpCreate,
    FollowUpUpdate,
    FollowUpResponse,
    FollowUpListResponse,
    FollowUpStatusUpdate,
    FollowUpAssignRequest,
    FollowUpTaskCreate,
    FollowUpTaskUpdate,
    FollowUpTaskStatusUpdate,
    FollowUpTaskResponse,
    FollowUpOutcomeCreate,
    FollowUpOutcomeResponse,
    FollowUpStatistics,
    LeadFollowUpSummary,
    UserFollowUpLoad,
)
from app.services.followup_service import FollowUpService
from app.utils.pagination import PaginationParams, get_pagination_params
from app.utils.response import ok, created, PaginatedResponse
from loguru import logger

router = APIRouter()


@router.get("/stats/kpis", status_code=status.HTTP_200_OK, response_model=dict)
async def get_followup_kpis(
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("followups.view")),
    statuses: str = Query(None, description="Comma-separated follow-up statuses"),
    priorities: str = Query(None, description="Comma-separated lead priorities"),
    sources: str = Query(None, description="Comma-separated lead sources"),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get follow-up KPIs with optional status/priority/source filters."""
    status_values = [s.strip().lower() for s in statuses.split(",") if s.strip()] if statuses else None
    priority_values = [p.strip().lower() for p in priorities.split(",") if p.strip()] if priorities else None
    source_values = [s.strip().lower() for s in sources.split(",") if s.strip()] if sources else None

    base_query = select(
        func.count(FollowUp.id).label("total_followups"),
        func.count(FollowUp.id).filter(FollowUp.status == "scheduled").label("scheduled_followups"),
        func.count(FollowUp.id).filter(FollowUp.status == "completed").label("completed_followups"),
        func.count(FollowUp.id).filter(FollowUp.status == "overdue").label("overdue_followups"),
    ).select_from(FollowUp)

    filters = [FollowUp.is_deleted == False]

    if status_values:
        filters.append(func.lower(FollowUp.status).in_(status_values))

    if source_values or priority_values:
        base_query = base_query.join(Lead, FollowUp.lead_id == Lead.id)
        if source_values:
            filters.append(func.lower(Lead.source).in_(source_values))
        if priority_values:
            filters.append(func.lower(Lead.priority).in_(priority_values))

    query = base_query.where(and_(*filters))
    row = (await session.execute(query)).one()

    return ok(
        data={
            "total_followups": row.total_followups or 0,
            "scheduled_followups": row.scheduled_followups or 0,
            "completed_followups": row.completed_followups or 0,
            "overdue_followups": row.overdue_followups or 0,
            "filters_applied": {
                "statuses": status_values,
                "priorities": priority_values,
                "sources": source_values,
            },
        }
    )


# ── Follow-Up CRUD ────────────────────────────────────────────────────

@router.post("", status_code=status.HTTP_201_CREATED, response_model=dict)
async def create_followup(
    request: FollowUpCreate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("followups.create")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Create new follow-up. Requires followups.create permission."""
    service = FollowUpService(session)

    followup = await service.create_followup(
        type_=request.type,
        subject=request.subject,
        description=request.description,
        scheduled_at=request.scheduled_at,
        created_by_user_id=current_user.id,
        assigned_to_user_id=request.assigned_to_user_id,
        lead_id=request.lead_id,
        customer_id=request.customer_id,
        priority=request.priority,
        is_critical=request.is_critical,
        notes=request.notes,
        tasks=[t.model_dump() for t in request.tasks] if request.tasks else None,
    )

    await session.commit()

    logger.info(
        f"Follow-up created | number={followup.followup_number} | lead={request.lead_id} | customer={request.customer_id}"
    )

    return created(
        data=FollowUpResponse.model_validate(followup).__dict__,
        message="Follow-up created successfully.",
    )


@router.get("", status_code=status.HTTP_200_OK, response_model=PaginatedResponse)
async def list_followups(
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("followups.view")),
    pagination: PaginationParams = Depends(get_pagination_params),
    lead_id: str = Query(None),
    customer_id: str = Query(None),
    assigned_to_user_id: str = Query(None),
    statuses: str = Query(None, description="Comma-separated statuses"),
    types: str = Query(None, description="Comma-separated types"),
    priority: int = Query(None),
    is_critical: bool = Query(None),
    search: str = Query(None),
    sort_by: str = Query("scheduled_at"),
    sort_direction: str = Query("asc"),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """List follow-ups with filtering and pagination."""
    service = FollowUpService(session)

    followups, total = await service.list_followups(
        lead_id=lead_id,
        customer_id=customer_id,
        assigned_to_user_id=assigned_to_user_id,
        statuses=statuses.split(",") if statuses else None,
        types=types.split(",") if types else None,
        priority=priority,
        is_critical=is_critical,
        search=search,
        skip=pagination.offset,
        limit=pagination.limit,
        sort_by=sort_by,
        sort_direction=sort_direction,
    )

    data = [FollowUpListResponse.model_validate(f).__dict__ for f in followups]

    return PaginatedResponse.build(
        data=data,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    ).__dict__


@router.get("/{followup_id}", status_code=status.HTTP_200_OK, response_model=dict)
async def get_followup(
    followup_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("followups.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get follow-up with all details."""
    service = FollowUpService(session)
    followup = await service.get_followup(followup_id)

    return ok(data=FollowUpResponse.model_validate(followup).__dict__)


@router.patch("/{followup_id}", status_code=status.HTTP_200_OK, response_model=dict)
async def update_followup(
    followup_id: str,
    request: FollowUpUpdate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("followups.edit")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Update follow-up (SCHEDULED only)."""
    service = FollowUpService(session)

    followup = await service.update_followup(followup_id, **request.model_dump(exclude_unset=True))

    await session.commit()

    logger.info(f"Follow-up updated | id={followup_id} | updated_by={current_user.id}")

    return ok(data=FollowUpResponse.model_validate(followup).__dict__)

@router.delete("/{followup_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_followup(
    followup_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("followups.delete")),
    session: AsyncSession = Depends(get_db_session),
):
    """Soft delete follow-up."""
    service = FollowUpService(session)
    await service.delete_followup(followup_id)

    await session.commit()

    logger.info(f"Follow-up deleted | id={followup_id} | deleted_by={current_user.id}")

    # FIX: Return the Response object to ensure there is no body
    return Response(status_code=status.HTTP_204_NO_CONTENT)
# ── Follow-Up Status ─────────────────────────────────────────────────

@router.post("/{followup_id}/status", status_code=status.HTTP_200_OK, response_model=dict)
async def update_followup_status(
    followup_id: str,
    request: FollowUpStatusUpdate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("followups.edit")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Update follow-up status."""
    service = FollowUpService(session)

    followup = await service.transition_status(followup_id, request.status, request.notes)

    await session.commit()

    logger.info(f"Follow-up status updated | id={followup_id} | status={request.status.value}")

    return ok(data=FollowUpResponse.model_validate(followup).__dict__)


# ── Follow-Up Assignment ──────────────────────────────────────────────

@router.post("/{followup_id}/assign", status_code=status.HTTP_200_OK, response_model=dict)
async def assign_followup(
    followup_id: str,
    request: FollowUpAssignRequest,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("followups.edit")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Assign follow-up to user."""
    service = FollowUpService(session)

    followup = await service.assign_followup(followup_id, request.assigned_to_user_id)

    await session.commit()

    logger.info(f"Follow-up assigned | id={followup_id} | user={request.assigned_to_user_id}")

    return ok(data=FollowUpResponse.model_validate(followup).__dict__)


# ── Follow-Up Tasks ──────────────────────────────────────────────────

@router.post("/{followup_id}/tasks", status_code=status.HTTP_201_CREATED, response_model=dict)
async def add_task(
    followup_id: str,
    request: FollowUpTaskCreate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("followups.edit")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Add task to follow-up."""
    service = FollowUpService(session)

    task = await service.add_task(
        followup_id=followup_id,
        task_type=request.task_type,
        title=request.title,
        description=request.description,
        scheduled_at=request.scheduled_at,
        is_required=request.is_required,
    )

    await session.commit()

    return created(
        data=FollowUpTaskResponse.model_validate(task).__dict__,
        message="Task added successfully.",
    )


@router.get("/{followup_id}/tasks", status_code=status.HTTP_200_OK, response_model=dict)
async def get_tasks(
    followup_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("followups.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get tasks for follow-up."""
    service = FollowUpService(session)
    task_repo = service.task_repo

    tasks = await task_repo.get_followup_tasks(followup_id)

    data = [FollowUpTaskResponse.model_validate(t).__dict__ for t in tasks]

    return ok(data=data)


@router.patch("/{followup_id}/tasks/{task_id}/status", status_code=status.HTTP_200_OK, response_model=dict)
async def update_task_status(
    followup_id: str,
    task_id: str,
    request: FollowUpTaskStatusUpdate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("followups.edit")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Update task status."""
    service = FollowUpService(session)

    task = await service.update_task_status(task_id, request.status, request.result_notes)

    await session.commit()

    logger.info(f"Task status updated | id={task_id} | status={request.status.value}")

    return ok(data=FollowUpTaskResponse.model_validate(task).__dict__)


# ── Follow-Up Outcomes ────────────────────────────────────────────────

@router.post("/{followup_id}/outcomes", status_code=status.HTTP_201_CREATED, response_model=dict)
async def record_outcome(
    followup_id: str,
    request: FollowUpOutcomeCreate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("followups.edit")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Record outcome for follow-up."""
    service = FollowUpService(session)

    outcome = await service.record_outcome(
        followup_id=followup_id,
        outcome_type=request.outcome_type,
        summary=request.summary,
        recorded_by_user_id=current_user.id,
        next_step=request.next_step,
        next_followup_date=request.next_followup_date,
        estimated_deal_value=request.estimated_deal_value,
        conversion_probability=request.conversion_probability,
        lost_reason=request.lost_reason,
        discussed_projects=request.discussed_projects,
        discussed_units=request.discussed_units,
    )

    await session.commit()

    return created(
        data=FollowUpOutcomeResponse.model_validate(outcome).__dict__,
        message="Outcome recorded successfully.",
    )


@router.get("/{followup_id}/outcomes", status_code=status.HTTP_200_OK, response_model=dict)
async def get_outcomes(
    followup_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("followups.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get outcomes for follow-up."""
    service = FollowUpService(session)
    outcome_repo = service.outcome_repo

    outcomes = await outcome_repo.get_followup_outcomes(followup_id)

    data = [FollowUpOutcomeResponse.model_validate(o).__dict__ for o in outcomes]

    return ok(data=data)


# ── Statistics ─────────────────────────────────────────────────────

@router.get("/stats/overview", status_code=status.HTTP_200_OK, response_model=dict)
async def get_followup_statistics(
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("followups.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get follow-up statistics."""
    service = FollowUpService(session)
    stats = await service.get_followup_statistics()

    return ok(data=stats)


@router.get("/lead/{lead_id}/summary", status_code=status.HTTP_200_OK, response_model=dict)
async def get_lead_followup_summary(
    lead_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("followups.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get follow-up summary for lead."""
    service = FollowUpService(session)
    summary = await service.get_lead_summary(lead_id)

    return ok(data=summary)


@router.get("/user/{user_id}/workload", status_code=status.HTTP_200_OK, response_model=dict)
async def get_user_workload(
    user_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("followups.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get follow-up workload for user."""
    service = FollowUpService(session)
    workload = await service.get_user_workload(user_id)

    return ok(data=workload)


# ── Scheduled & Upcoming ──────────────────────────────────────────────

@router.get("/due/overdue", status_code=status.HTTP_200_OK, response_model=dict)
async def get_overdue_followups(
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("followups.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get overdue follow-ups."""
    service = FollowUpService(session)
    followups = await service.get_overdue()

    data = [FollowUpListResponse.model_validate(f).__dict__ for f in followups]

    return ok(data=data)


@router.get("/due/upcoming", status_code=status.HTTP_200_OK, response_model=dict)
async def get_upcoming_followups(
    days: int = Query(7, ge=1, le=30),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("followups.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get upcoming follow-ups within N days."""
    service = FollowUpService(session)
    followups = await service.get_upcoming(days)

    data = [FollowUpListResponse.model_validate(f).__dict__ for f in followups]

    return ok(data=data)
