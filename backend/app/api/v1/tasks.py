"""
FastAPI routes for task and activity management.

Endpoints:
- Task CRUD: POST/GET/PATCH/DELETE
- Status management: POST /status
- Assignment: POST /assign
- Progress tracking: POST /progress
- Checklist: POST/PATCH items
- Comments: POST/GET comments
- Statistics: GET /stats
- Activities: GET /activities
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db_session
from app.dependencies.auth import get_current_user, require_permission
from app.models.user import User
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
    TaskStatusUpdate,
    TaskProgressUpdate,
    TaskAssignRequest,
    TaskChecklistCreate,
    TaskChecklistResponse,
    TaskCommentCreate,
    TaskCommentResponse,
    TaskStatistics,
    UserTaskLoad,
    ActivityResponse,
)
from app.services.task_service import TaskService, ActivityService
from app.utils.pagination import PaginationParams, get_pagination_params
from app.utils.response import ok, created, PaginatedResponse
from loguru import logger

router = APIRouter()


# ── Task CRUD ─────────────────────────────────────────────────────────

@router.post("", status_code=status.HTTP_201_CREATED, response_model=dict)
async def create_task(
    request: TaskCreate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("tasks.create")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Create new task. Requires tasks.create permission."""
    service = TaskService(session)

    task = await service.create_task(
        title=request.title,
        description=request.description,
        task_type=request.task_type,
        category=request.category,
        priority=request.priority,
        assigned_to_user_id=request.assigned_to_user_id,
        created_by_user_id=current_user.id,
        due_date=request.due_date,
        start_date=request.start_date,
        estimated_hours=request.estimated_hours,
        lead_id=request.lead_id,
        customer_id=request.customer_id,
        project_id=request.project_id,
        booking_id=request.booking_id,
        tags=request.tags,
        is_urgent=request.is_urgent,
        is_recurring=request.is_recurring,
        checklists=[c.model_dump() for c in request.checklists] if request.checklists else None,
    )

    await session.commit()

    logger.info(f"Task created | number={task.task_number} | title={request.title}")

    return created(
        data=TaskResponse.model_validate(task).__dict__,
        message="Task created successfully.",
    )


@router.get("", status_code=status.HTTP_200_OK, response_model=PaginatedResponse)
async def list_tasks(
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("tasks.view")),
    pagination: PaginationParams = Depends(get_pagination_params),
    assigned_to_user_id: str = Query(None),
    statuses: str = Query(None, description="Comma-separated statuses"),
    priorities: str = Query(None, description="Comma-separated priorities"),
    categories: str = Query(None, description="Comma-separated categories"),
    lead_id: str = Query(None),
    customer_id: str = Query(None),
    project_id: str = Query(None),
    booking_id: str = Query(None),
    is_urgent: bool = Query(None),
    search: str = Query(None),
    sort_by: str = Query("due_date"),
    sort_direction: str = Query("asc"),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """List tasks with filtering and pagination."""
    service = TaskService(session)

    tasks, total = await service.list_tasks(
        assigned_to_user_id=assigned_to_user_id,
        statuses=statuses.split(",") if statuses else None,
        priorities=priorities.split(",") if priorities else None,
        categories=categories.split(",") if categories else None,
        lead_id=lead_id,
        customer_id=customer_id,
        project_id=project_id,
        booking_id=booking_id,
        is_urgent=is_urgent,
        search=search,
        skip=pagination.offset,
        limit=pagination.limit,
        sort_by=sort_by,
        sort_direction=sort_direction,
    )

    data = [TaskListResponse.model_validate(t).__dict__ for t in tasks]

    return PaginatedResponse.build(
        data=data,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    ).__dict__


@router.get("/{task_id}", status_code=status.HTTP_200_OK, response_model=dict)
async def get_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("tasks.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get task with all details."""
    service = TaskService(session)
    task = await service.get_task(task_id)

    return ok(data=TaskResponse.model_validate(task).__dict__)


@router.patch("/{task_id}", status_code=status.HTTP_200_OK, response_model=dict)
async def update_task(
    task_id: str,
    request: TaskUpdate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("tasks.edit")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Update task."""
    service = TaskService(session)

    task = await service.update_task(task_id, **request.model_dump(exclude_unset=True))

    await session.commit()

    logger.info(f"Task updated | id={task_id} | updated_by={current_user.id}")

    return ok(data=TaskResponse.model_validate(task).__dict__)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("tasks.delete")),
    session: AsyncSession = Depends(get_db_session),
) -> Response:
    """Soft delete task."""
    service = TaskService(session)
    await service.delete_task(task_id)

    await session.commit()

    logger.info(f"Task deleted | id={task_id} | deleted_by={current_user.id}")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ── Task Status ───────────────────────────────────────────────────────

@router.post("/{task_id}/status", status_code=status.HTTP_200_OK, response_model=dict)
async def update_task_status(
    task_id: str,
    request: TaskStatusUpdate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("tasks.edit")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Update task status."""
    service = TaskService(session)

    task = await service.transition_status(task_id, request.status, request.notes)

    await session.commit()

    logger.info(f"Task status updated | id={task_id} | status={request.status.value}")

    return ok(data=TaskResponse.model_validate(task).__dict__)


# ── Task Assignment ───────────────────────────────────────────────────

@router.post("/{task_id}/assign", status_code=status.HTTP_200_OK, response_model=dict)
async def assign_task(
    task_id: str,
    request: TaskAssignRequest,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("tasks.edit")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Assign task to user."""
    service = TaskService(session)

    task = await service.assign_task(task_id, request.assigned_to_user_id)

    await session.commit()

    logger.info(f"Task assigned | id={task_id} | user={request.assigned_to_user_id}")

    return ok(data=TaskResponse.model_validate(task).__dict__)


# ── Task Progress ─────────────────────────────────────────────────────

@router.post("/{task_id}/progress", status_code=status.HTTP_200_OK, response_model=dict)
async def update_progress(
    task_id: str,
    request: TaskProgressUpdate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("tasks.edit")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Update task progress."""
    service = TaskService(session)

    task = await service.update_progress(task_id, request.progress, request.actual_hours)

    await session.commit()

    logger.info(f"Task progress updated | id={task_id} | progress={request.progress}%")

    return ok(data=TaskResponse.model_validate(task).__dict__)


# ── Task Checklists ───────────────────────────────────────────────────

@router.post("/{task_id}/checklists", status_code=status.HTTP_201_CREATED, response_model=dict)
async def add_checklist_item(
    task_id: str,
    request: TaskChecklistCreate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("tasks.edit")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Add checklist item to task."""
    service = TaskService(session)

    item = await service.add_checklist_item(task_id, request.title, request.description)

    await session.commit()

    return created(
        data=TaskChecklistResponse.model_validate(item).__dict__,
        message="Checklist item added successfully.",
    )


@router.get("/{task_id}/checklists", status_code=status.HTTP_200_OK, response_model=dict)
async def get_checklists(
    task_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("tasks.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get checklists for task."""
    service = TaskService(session)
    checklist_repo = service.checklist_repo

    items = await checklist_repo.get_task_checklists(task_id)

    data = [TaskChecklistResponse.model_validate(i).__dict__ for i in items]

    return ok(data=data)


@router.patch("/{task_id}/checklists/{item_id}/complete", status_code=status.HTTP_200_OK, response_model=dict)
async def complete_checklist(
    task_id: str,
    item_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("tasks.edit")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Mark checklist item as complete."""
    service = TaskService(session)

    item = await service.complete_checklist_item(item_id, current_user.id)

    await session.commit()

    logger.info(f"Checklist item completed | id={item_id}")

    return ok(data=TaskChecklistResponse.model_validate(item).__dict__)


# ── Task Comments ─────────────────────────────────────────────────────

@router.post("/{task_id}/comments", status_code=status.HTTP_201_CREATED, response_model=dict)
async def add_comment(
    task_id: str,
    request: TaskCommentCreate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("tasks.edit")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Add comment to task."""
    service = TaskService(session)

    comment = await service.add_comment(
        task_id=task_id,
        content=request.content,
        commented_by_user_id=current_user.id,
        is_internal=request.is_internal,
        mentions=request.mentions,
    )

    await session.commit()

    return created(
        data=TaskCommentResponse.model_validate(comment).__dict__,
        message="Comment added successfully.",
    )


@router.get("/{task_id}/comments", status_code=status.HTTP_200_OK, response_model=dict)
async def get_comments(
    task_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("tasks.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get comments for task."""
    service = TaskService(session)
    comments = await service.get_task_comments(task_id)

    data = [TaskCommentResponse.model_validate(c).__dict__ for c in comments]

    return ok(data=data)


# ── Statistics ────────────────────────────────────────────────────────

@router.get("/stats/overview", status_code=status.HTTP_200_OK, response_model=dict)
async def get_task_statistics(
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("tasks.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get task statistics."""
    service = TaskService(session)
    stats = await service.get_task_statistics()

    return ok(data=stats)


@router.get("/user/{user_id}/workload", status_code=status.HTTP_200_OK, response_model=dict)
async def get_user_workload(
    user_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("tasks.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get task workload for user."""
    service = TaskService(session)
    workload = await service.get_user_workload(user_id)

    return ok(data=workload)


# ── Scheduled & Upcoming ──────────────────────────────────────────────

@router.get("/due/overdue", status_code=status.HTTP_200_OK, response_model=dict)
async def get_overdue_tasks(
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("tasks.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get overdue tasks."""
    service = TaskService(session)
    tasks = await service.get_overdue()

    data = [TaskListResponse.model_validate(t).__dict__ for t in tasks]

    return ok(data=data)


@router.get("/due/upcoming", status_code=status.HTTP_200_OK, response_model=dict)
async def get_upcoming_tasks(
    days: int = Query(7, ge=1, le=30),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("tasks.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get tasks due within N days."""
    service = TaskService(session)
    tasks = await service.get_due_soon(days)

    data = [TaskListResponse.model_validate(t).__dict__ for t in tasks]

    return ok(data=data)


# ── Activities ────────────────────────────────────────────────────────

@router.get("/activities/entity/{entity_type}/{entity_id}", status_code=status.HTTP_200_OK, response_model=PaginatedResponse)
async def get_entity_activities(
    entity_type: str,
    entity_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("activities.view")),
    pagination: PaginationParams = Depends(get_pagination_params),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get activities for an entity."""
    service = ActivityService(session)
    activities, total = await service.get_entity_activities(entity_type, entity_id, pagination.offset, pagination.limit)

    data = [ActivityResponse.model_validate(a).__dict__ for a in activities]

    return PaginatedResponse.build(
        data=data,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    ).__dict__


@router.get("/activities/user/{user_id}", status_code=status.HTTP_200_OK, response_model=PaginatedResponse)
async def get_user_activities(
    user_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("activities.view")),
    pagination: PaginationParams = Depends(get_pagination_params),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get activities performed by user."""
    service = ActivityService(session)
    activities, total = await service.get_user_activities(user_id, pagination.offset, pagination.limit)

    data = [ActivityResponse.model_validate(a).__dict__ for a in activities]

    return PaginatedResponse.build(
        data=data,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    ).__dict__


@router.get("/activities/recent", status_code=status.HTTP_200_OK, response_model=dict)
async def get_recent_activities(
    hours: int = Query(24, ge=1, le=720),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("activities.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get recent activities."""
    service = ActivityService(session)
    activities = await service.get_recent_activities(hours, limit)

    data = [ActivityResponse.model_validate(a).__dict__ for a in activities]

    return ok(data=data)
