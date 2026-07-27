"""
FastAPI routes for audit log viewing.

Endpoints:
- GET /audit                         — list logs (searchable, filterable)
- GET /audit/{log_id}                — single entry
- GET /audit/entity/{type}/{id}      — full entity history
- GET /audit/user/{user_id}          — user activity trail
- GET /audit/stats                   — aggregate statistics
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db_session
from app.dependencies.auth import get_current_user, require_permission
from app.models.user import User
from app.schemas.audit import AuditLogResponse, AuditLogListResponse, AuditLogStats
from app.services.audit_service import AuditService
from app.utils.pagination import PaginationParams, get_pagination_params
from app.utils.response import ok, PaginatedResponse

router = APIRouter()


@router.get("", status_code=status.HTTP_200_OK, response_model=PaginatedResponse)
async def list_audit_logs(
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("audit.view")),
    pagination: PaginationParams = Depends(get_pagination_params),
    user_id: Optional[str] = Query(None),
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    search: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """
    List audit logs with full filtering.

    Filterable by: user, entity_type, entity_id, action, status, date range, free text.
    """
    svc = AuditService(session)
    logs, total = await svc.list_logs(
        user_id=UUID(user_id) if user_id else None,
        entity_type=entity_type,
        entity_id=UUID(entity_id) if entity_id else None,
        action=action,
        status=status_filter,
        start_date=start_date,
        end_date=end_date,
        search=search,
        skip=pagination.offset,
        limit=pagination.limit,
    )

    data = [AuditLogListResponse.model_validate(l).__dict__ for l in logs]
    return PaginatedResponse.build(
        data=data,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    ).__dict__


@router.get("/stats", status_code=status.HTTP_200_OK, response_model=dict)
async def get_audit_stats(
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("audit.view")),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Aggregate audit statistics: totals by action, entity type, and top users."""
    svc = AuditService(session)
    stats = await svc.get_statistics(start_date, end_date)
    return ok(data=stats)


@router.get("/entity/{entity_type}/{entity_id}", status_code=status.HTTP_200_OK, response_model=dict)
async def get_entity_history(
    entity_type: str,
    entity_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("audit.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Full audit history for a specific entity (all changes, chronological)."""
    svc = AuditService(session)
    logs = await svc.get_entity_history(entity_type, UUID(entity_id))
    data = [AuditLogResponse.model_validate(l).__dict__ for l in logs]
    return ok(data=data)


@router.get("/user/{user_id}", status_code=status.HTTP_200_OK, response_model=PaginatedResponse)
async def get_user_activity(
    user_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("audit.view")),
    pagination: PaginationParams = Depends(get_pagination_params),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Audit trail for a specific user — all actions they performed."""
    svc = AuditService(session)
    logs, total = await svc.get_user_activity(
        UUID(user_id), pagination.offset, pagination.limit
    )
    data = [AuditLogListResponse.model_validate(l).__dict__ for l in logs]
    return PaginatedResponse.build(
        data=data,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    ).__dict__


@router.get("/{log_id}", status_code=status.HTTP_200_OK, response_model=dict)
async def get_audit_log(
    log_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("audit.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get a single audit log entry with full details including before/after values."""
    svc = AuditService(session)
    log = await svc.get_log(UUID(log_id))
    return ok(data=AuditLogResponse.model_validate(log).__dict__)
