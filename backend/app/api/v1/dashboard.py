"""
FastAPI routes for dashboard and system settings.

Dashboard:
- GET /dashboard — Full widget dashboard for current user

Settings:
- GET/POST /settings          — App settings
- GET/PATCH /settings/{key}   — Individual setting
- GET/POST /settings/user     — User preferences
"""

from __future__ import annotations

from typing import Optional, Any
from uuid import UUID

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db_session
from app.dependencies.auth import get_current_user, require_permission
from app.models.user import User
from app.schemas.dashboard import (
    DashboardResponse,
    AppSettingResponse, AppSettingCreate, AppSettingUpdate,
    UserSettingResponse, UserSettingUpdate, UserSettingsBulkUpdate,
)
from app.services.dashboard_service import DashboardService, SettingsService
from app.utils.response import ok, created
from loguru import logger

router = APIRouter()


# ── Dashboard ─────────────────────────────────────────────────────────

@router.get("/dashboard", status_code=status.HTTP_200_OK, response_model=dict)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get full dashboard for current user.
    
    Returns all widgets:
    - Lead pipeline summary
    - Revenue snapshot
    - Booking snapshot
    - My task summary
    - Team activity today
    - Inventory availability
    - Upcoming follow-ups & tasks
    - Recent leads & bookings
    """
    service = DashboardService(session)
    dashboard = await service.get_dashboard(
        user_id=current_user.id,
        user_name=getattr(current_user, "full_name", str(current_user.id)),
    )

    return ok(data=dashboard.model_dump())


# ── App Settings ──────────────────────────────────────────────────────

@router.get("/settings", status_code=status.HTTP_200_OK, response_model=dict)
async def list_settings(
    category: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("settings.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """List all application settings, optionally filtered by category."""
    service = SettingsService(session)
    settings = await service.list_app_settings(category=category)

    data = []
    for s in settings:
        # Resolve value from correct column
        value = _resolve_setting_value(s)
        data.append({
            "id": str(s.id),
            "key": s.key,
            "label": s.label,
            "category": s.category,
            "data_type": s.data_type,
            "value": "***" if s.is_sensitive else value,
            "description": s.description,
            "is_sensitive": s.is_sensitive,
            "is_readonly": s.is_readonly,
            "updated_at": s.updated_at,
        })

    return ok(data=data)


@router.post("/settings", status_code=status.HTTP_201_CREATED, response_model=dict)
async def create_setting(
    request: AppSettingCreate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("settings.manage")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Create a new application setting."""
    service = SettingsService(session)

    setting = await service.create_setting(
        key=request.key,
        label=request.label,
        category=request.category,
        data_type=request.data_type,
        value=request.value,
        description=request.description,
        is_sensitive=request.is_sensitive,
        is_readonly=request.is_readonly,
    )
    await session.commit()

    logger.info(f"Setting created | key={request.key} | by={current_user.id}")

    value = _resolve_setting_value(setting)
    return created(
        data={
            "id": str(setting.id),
            "key": setting.key,
            "label": setting.label,
            "category": setting.category,
            "data_type": setting.data_type,
            "value": "***" if setting.is_sensitive else value,
            "description": setting.description,
            "is_sensitive": setting.is_sensitive,
            "is_readonly": setting.is_readonly,
        },
        message="Setting created successfully.",
    )


@router.get("/settings/{key}", status_code=status.HTTP_200_OK, response_model=dict)
async def get_setting(
    key: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("settings.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get a specific setting by key."""
    service = SettingsService(session)
    setting = await service.get_setting(key)

    value = _resolve_setting_value(setting)
    return ok(data={
        "key": setting.key,
        "label": setting.label,
        "category": setting.category,
        "data_type": setting.data_type,
        "value": "***" if setting.is_sensitive else value,
        "description": setting.description,
        "is_readonly": setting.is_readonly,
        "updated_at": setting.updated_at,
    })


@router.patch("/settings/{key}", status_code=status.HTTP_200_OK, response_model=dict)
async def update_setting(
    key: str,
    request: AppSettingUpdate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("settings.manage")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Update a setting value."""
    service = SettingsService(session)
    setting = await service.update_setting(key, request.value, current_user.id)
    await session.commit()

    logger.info(f"Setting updated | key={key} | by={current_user.id}")

    value = _resolve_setting_value(setting)
    return ok(
        data={"key": setting.key, "value": "***" if setting.is_sensitive else value},
        message="Setting updated successfully.",
    )


# ── User Preferences ──────────────────────────────────────────────────

@router.get("/settings/user/preferences", status_code=status.HTTP_200_OK, response_model=dict)
async def get_user_preferences(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get current user's preference settings."""
    service = SettingsService(session)
    settings = await service.get_user_settings(current_user.id)

    data = [{"key": s.key, "value": s.value, "updated_at": s.updated_at} for s in settings]

    return ok(data=data)


@router.post("/settings/user/preferences", status_code=status.HTTP_200_OK, response_model=dict)
async def update_user_preferences(
    request: UserSettingsBulkUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Bulk update current user's preference settings."""
    service = SettingsService(session)

    updated = []
    for item in request.settings:
        setting = await service.upsert_user_setting(current_user.id, item.key, item.value)
        updated.append({"key": setting.key, "value": setting.value})

    await session.commit()

    return ok(data=updated, message=f"Updated {len(updated)} preferences.")


# ── Helpers ───────────────────────────────────────────────────────────

def _resolve_setting_value(setting) -> Any:
    """Resolve the stored value from the correct column."""
    if setting.data_type == "string":
        return setting.value_string
    elif setting.data_type == "int":
        return setting.value_int
    elif setting.data_type == "bool":
        return setting.value_bool
    elif setting.data_type == "json":
        return setting.value_json
    return None
