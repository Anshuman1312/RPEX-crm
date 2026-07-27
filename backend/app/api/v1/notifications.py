"""
FastAPI routes for notification management.

Endpoints:
- User notifications: GET (list, unread count)
- Read management: POST /read, POST /read-all, POST /archive
- Delete: DELETE /{id}
- Preferences: GET/PATCH /preferences
- Templates (admin): CRUD
- Statistics: GET /stats
"""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db_session
from app.dependencies.auth import get_current_user, require_permission
from app.models.user import User
from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
    NotificationListResponse,
    NotificationMarkRead,
    NotificationMarkArchived,
    NotificationBulkSend,
    NotificationPreferenceUpdate,
    NotificationPreferenceResponse,
    NotificationTemplateCreate,
    NotificationTemplateUpdate,
    NotificationTemplateResponse,
    NotificationStatistics,
    UnreadCountResponse,
)
from app.services.notification_service import NotificationService
from app.utils.enums import NotificationType, NotificationChannel
from app.utils.pagination import PaginationParams, get_pagination_params
from app.utils.response import ok, created, PaginatedResponse
from loguru import logger

router = APIRouter()


# ── User Notifications ────────────────────────────────────────────────

@router.get("/me", status_code=status.HTTP_200_OK, response_model=PaginatedResponse)
async def list_my_notifications(
    current_user: User = Depends(get_current_user),
    pagination: PaginationParams = Depends(get_pagination_params),
    is_read: Optional[bool] = Query(None, description="Filter by read status"),
    is_archived: bool = Query(False),
    types: Optional[str] = Query(None, description="Comma-separated notification types"),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get notifications for current user."""
    service = NotificationService(session)

    notifications, total = await service.get_user_notifications(
        user_id=current_user.id,
        is_read=is_read,
        is_archived=is_archived,
        types=types.split(",") if types else None,
        skip=pagination.offset,
        limit=pagination.limit,
    )

    data = [NotificationListResponse.model_validate(n).__dict__ for n in notifications]

    return PaginatedResponse.build(
        data=data,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    ).__dict__


@router.get("/me/unread-count", status_code=status.HTTP_200_OK, response_model=dict)
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get unread notification count for current user."""
    service = NotificationService(session)
    counts = await service.get_unread_count(current_user.id)

    return ok(data={
        "user_id": str(current_user.id),
        **counts,
    })


# ── Read/Archive ──────────────────────────────────────────────────────

@router.post("/me/read", status_code=status.HTTP_200_OK, response_model=dict)
async def mark_read(
    request: NotificationMarkRead,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Mark specific notifications as read."""
    service = NotificationService(session)
    count = await service.mark_read(request.notification_ids, current_user.id)
    await session.commit()

    return ok(data={"updated_count": count}, message=f"Marked {count} notifications as read.")


@router.post("/me/read-all", status_code=status.HTTP_200_OK, response_model=dict)
async def mark_all_read(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Mark all notifications as read for current user."""
    service = NotificationService(session)
    count = await service.mark_all_read(current_user.id)
    await session.commit()

    return ok(data={"updated_count": count}, message=f"Marked {count} notifications as read.")


@router.post("/me/archive", status_code=status.HTTP_200_OK, response_model=dict)
async def archive_notifications(
    request: NotificationMarkArchived,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Archive specific notifications."""
    service = NotificationService(session)
    count = await service.mark_archived(request.notification_ids, current_user.id)
    await session.commit()

    return ok(data={"updated_count": count}, message=f"Archived {count} notifications.")


@router.delete("/me/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Response:
    """Delete a notification."""
    service = NotificationService(session)
    await service.delete_notification(notification_id, current_user.id)
    await session.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
# ── Preferences ───────────────────────────────────────────────────────

@router.get("/me/preferences", status_code=status.HTTP_200_OK, response_model=dict)
async def get_preferences(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get notification preferences for current user."""
    service = NotificationService(session)
    preferences = await service.get_user_preferences(current_user.id)

    data = [NotificationPreferenceResponse.model_validate(p).__dict__ for p in preferences]

    return ok(data=data)


@router.patch("/me/preferences/{notification_type}", status_code=status.HTTP_200_OK, response_model=dict)
async def update_preference(
    notification_type: str,
    request: NotificationPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Update notification preference for a type."""
    service = NotificationService(session)

    try:
        type_enum = NotificationType[notification_type.upper()]
    except KeyError:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=f"Invalid notification type: {notification_type}")

    pref = await service.update_preference(
        user_id=current_user.id,
        notification_type=type_enum,
        **request.model_dump(exclude_unset=True),
    )
    await session.commit()

    return ok(data=NotificationPreferenceResponse.model_validate(pref).__dict__)


# ── Admin: Send ───────────────────────────────────────────────────────

@router.post("/send", status_code=status.HTTP_201_CREATED, response_model=dict)
async def send_notification(
    request: NotificationCreate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("notifications.send")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Send a notification to a user (admin)."""
    service = NotificationService(session)

    notification = await service.send(
        user_id=request.user_id,
        type_=request.type,
        title=request.title,
        body=request.body,
        channel=request.channel,
        entity_type=request.entity_type,
        entity_id=request.entity_id,
        priority=request.priority,
        action_url=request.action_url,
        metadata=request.metadata,
    )
    await session.commit()

    logger.info(f"Notification sent | user={request.user_id} | by={current_user.id}")

    return created(
        data=NotificationResponse.model_validate(notification).__dict__,
        message="Notification sent successfully.",
    )


@router.post("/send-bulk", status_code=status.HTTP_201_CREATED, response_model=dict)
async def send_bulk_notification(
    request: NotificationBulkSend,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("notifications.send")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Send notification to multiple users (admin)."""
    service = NotificationService(session)

    notifications = await service.send_bulk(
        user_ids=request.user_ids,
        type_=request.type,
        title=request.title,
        body=request.body,
        channel=request.channel,
        entity_type=request.entity_type,
        entity_id=request.entity_id,
        priority=request.priority,
        action_url=request.action_url,
    )
    await session.commit()

    logger.info(f"Bulk notification sent | users={len(request.user_ids)} | by={current_user.id}")

    return created(
        data={"sent_count": len(notifications)},
        message=f"Notification sent to {len(notifications)} users.",
    )


# ── Templates ─────────────────────────────────────────────────────────

@router.post("/templates", status_code=status.HTTP_201_CREATED, response_model=dict)
async def create_template(
    request: NotificationTemplateCreate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("notifications.manage_templates")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Create a notification template."""
    service = NotificationService(session)

    template = await service.create_template(
        name=request.name,
        notification_type=request.notification_type,
        channel=request.channel,
        title_template=request.title_template,
        body_template=request.body_template,
        variables=request.variables,
    )
    await session.commit()

    return created(
        data=NotificationTemplateResponse.model_validate(template).__dict__,
        message="Template created successfully.",
    )


@router.get("/templates", status_code=status.HTTP_200_OK, response_model=dict)
async def list_templates(
    active_only: bool = Query(True),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("notifications.manage_templates")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """List notification templates."""
    service = NotificationService(session)
    templates = await service.get_templates(active_only)

    data = [NotificationTemplateResponse.model_validate(t).__dict__ for t in templates]

    return ok(data=data)


@router.patch("/templates/{template_id}", status_code=status.HTTP_200_OK, response_model=dict)
async def update_template(
    template_id: str,
    request: NotificationTemplateUpdate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("notifications.manage_templates")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Update a notification template."""
    service = NotificationService(session)

    template = await service.update_template(
        template_id,
        **request.model_dump(exclude_unset=True),
    )
    await session.commit()

    return ok(data=NotificationTemplateResponse.model_validate(template).__dict__)


# ── Statistics ────────────────────────────────────────────────────────

@router.get("/stats/overview", status_code=status.HTTP_200_OK, response_model=dict)
async def get_notification_statistics(
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("notifications.view_stats")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get notification statistics (admin)."""
    service = NotificationService(session)
    stats = await service.get_statistics()

    return ok(data=stats)
