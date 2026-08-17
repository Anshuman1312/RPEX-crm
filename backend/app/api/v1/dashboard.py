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

from datetime import date
from typing import Optional, Any
from uuid import UUID

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db_session
from app.dependencies.auth import get_current_user, require_permission
from app.models.campaign import Campaign
from app.models.customer import Customer
from app.models.followup import FollowUp
from app.models.lead import Lead
from app.models.project import Project
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


@router.get("/kpis/leads", status_code=status.HTTP_200_OK, response_model=dict)
async def get_lead_pipeline_kpis(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get lead pipeline KPIs broken down by status for the dashboard KPI cards."""
    _ = current_user

    row = (
        await session.execute(
            select(
                func.count(Lead.id).label("total_leads"),
                # Open = anything not lost/inactive/converted
                func.count(Lead.id).filter(
                    func.lower(Lead.status).notin_(["lost", "inactive", "converted"])
                ).label("open_leads"),
                # Follow-up leads = those with a scheduled next followup
                func.count(Lead.id).filter(
                    Lead.next_followup_at.isnot(None),
                    func.lower(Lead.status).notin_(["lost", "inactive", "converted"]),
                ).label("follow_leads"),
                # Contacted (visit scheduled proxy) = contacted + proposal_sent
                func.count(Lead.id).filter(
                    func.lower(Lead.status).in_(["contacted", "proposal_sent"])
                ).label("visit_scheduled"),
                # Negotiation = visited / qualified
                func.count(Lead.id).filter(
                    func.lower(Lead.status).in_(["negotiation", "qualified"])
                ).label("visited_leads"),
                # Converted = booking leads
                func.count(Lead.id).filter(
                    func.lower(Lead.status) == "converted"
                ).label("booking_leads"),
                # Lost = future perspective / lost but trackable
                func.count(Lead.id).filter(
                    func.lower(Lead.status) == "lost"
                ).label("lost_leads"),
                # Inactive = duplicate/cold
                func.count(Lead.id).filter(
                    func.lower(Lead.status) == "inactive"
                ).label("inactive_leads"),
            ).where(Lead.is_deleted == False)
        )
    ).one()

    return ok(
        data={
            "total_leads": row.total_leads or 0,
            "open_leads": row.open_leads or 0,
            "follow_leads": row.follow_leads or 0,
            "visit_scheduled": row.visit_scheduled or 0,
            "visited_leads": row.visited_leads or 0,
            "booking_leads": row.booking_leads or 0,
            "lost_leads": row.lost_leads or 0,
            "inactive_leads": row.inactive_leads or 0,
        }
    )


@router.get("/kpis/overview", status_code=status.HTTP_200_OK, response_model=dict)
async def get_kpis_overview(
    statuses: str = Query(None, description="Comma-separated statuses"),
    priorities: str = Query(None, description="Comma-separated priorities"),
    sources: str = Query(None, description="Comma-separated sources"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get combined KPIs for leads, campaigns, customers, followups, and projects."""
    _ = current_user

    status_values = [s.strip().lower() for s in statuses.split(",") if s.strip()] if statuses else None
    priority_values = [p.strip().lower() for p in priorities.split(",") if p.strip()] if priorities else None
    source_values = [s.strip().lower() for s in sources.split(",") if s.strip()] if sources else None

    # Leads KPIs
    lead_filters = [Lead.is_deleted == False]
    if status_values:
        lead_filters.append(func.lower(Lead.status).in_(status_values))
    if priority_values:
        lead_filters.append(func.lower(Lead.priority).in_(priority_values))
    if source_values:
        lead_filters.append(func.lower(Lead.source).in_(source_values))

    lead_row = (
        await session.execute(
            select(
                func.count(Lead.id).label("total_leads"),
                func.count(Lead.id).filter(func.lower(Lead.status) == "new").label("new_leads"),
                func.count(Lead.id).filter(func.lower(Lead.status) == "qualified").label("qualified_leads"),
                func.count(Lead.id).filter(func.lower(Lead.priority) == "warm").label("warm_leads"),
            ).where(and_(*lead_filters))
        )
    ).one()

    # Campaign KPIs
    today = date.today()
    active_condition = and_(
        Campaign.start_date.is_not(None),
        Campaign.start_date <= today,
        or_(Campaign.end_date.is_(None), Campaign.end_date >= today),
    )
    upcoming_condition = and_(Campaign.start_date.is_not(None), Campaign.start_date > today)
    ended_condition = and_(Campaign.end_date.is_not(None), Campaign.end_date < today)

    campaign_filters = [Campaign.is_deleted == False]
    campaign_ignored_filters = []

    if source_values:
        campaign_filters.append(func.lower(Campaign.platform).in_(source_values))
    if priority_values:
        campaign_ignored_filters.append("priorities")
    if status_values:
        status_conditions = []
        if "active" in status_values:
            status_conditions.append(active_condition)
        if "upcoming" in status_values:
            status_conditions.append(upcoming_condition)
        if "ended" in status_values:
            status_conditions.append(ended_condition)
        if status_conditions:
            campaign_filters.append(or_(*status_conditions))

    campaign_row = (
        await session.execute(
            select(
                func.count(Campaign.id).label("total_campaigns"),
                func.count(Campaign.id).filter(active_condition).label("active_campaigns"),
                func.count(Campaign.id).filter(upcoming_condition).label("upcoming_campaigns"),
                func.count(Campaign.id).filter(ended_condition).label("ended_campaigns"),
            ).where(and_(*campaign_filters))
        )
    ).one()

    # Customers KPIs
    customer_base_query = select(
        func.count(Customer.id).label("total_customers"),
        func.count(Customer.id).filter(func.lower(Customer.status) == "active").label("active_customers"),
        func.count(Customer.id).filter(func.lower(Customer.status) == "inactive").label("inactive_customers"),
        func.count(Customer.id).filter(func.lower(Customer.status) == "blacklisted").label("blacklisted_customers"),
    ).select_from(Customer)

    customer_filters = [Customer.is_deleted == False]
    if status_values:
        customer_filters.append(func.lower(Customer.status).in_(status_values))
    if source_values or priority_values:
        customer_base_query = customer_base_query.join(Lead, Customer.lead_converted_from_id == Lead.id)
        if source_values:
            customer_filters.append(func.lower(Lead.source).in_(source_values))
        if priority_values:
            customer_filters.append(func.lower(Lead.priority).in_(priority_values))

    customer_row = (await session.execute(customer_base_query.where(and_(*customer_filters)))).one()

    # Follow-up KPIs
    followup_base_query = select(
        func.count(FollowUp.id).label("total_followups"),
        func.count(FollowUp.id).filter(func.lower(FollowUp.status) == "scheduled").label("scheduled_followups"),
        func.count(FollowUp.id).filter(func.lower(FollowUp.status) == "completed").label("completed_followups"),
        func.count(FollowUp.id).filter(func.lower(FollowUp.status) == "overdue").label("overdue_followups"),
    ).select_from(FollowUp)

    followup_filters = [FollowUp.is_deleted == False]
    if status_values:
        followup_filters.append(func.lower(FollowUp.status).in_(status_values))
    if source_values or priority_values:
        followup_base_query = followup_base_query.join(Lead, FollowUp.lead_id == Lead.id)
        if source_values:
            followup_filters.append(func.lower(Lead.source).in_(source_values))
        if priority_values:
            followup_filters.append(func.lower(Lead.priority).in_(priority_values))

    followup_row = (await session.execute(followup_base_query.where(and_(*followup_filters)))).one()

    # Project KPIs
    project_filters = [Project.is_deleted == False]
    project_ignored_filters = []
    if status_values:
        project_filters.append(func.lower(Project.status).in_(status_values))
    if priority_values:
        project_ignored_filters.append("priorities")
    if source_values:
        project_ignored_filters.append("sources")

    project_row = (
        await session.execute(
            select(
                func.count(Project.id).label("total_projects"),
                func.count(Project.id).filter(func.lower(Project.status) == "planning").label("planning_projects"),
                func.count(Project.id).filter(func.lower(Project.status) == "ongoing").label("ongoing_projects"),
                func.count(Project.id).filter(func.lower(Project.status) == "completed").label("completed_projects"),
            ).where(and_(*project_filters))
        )
    ).one()

    return ok(
        data={
            "leads": {
                "total_leads": lead_row.total_leads or 0,
                "new_leads": lead_row.new_leads or 0,
                "qualified_leads": lead_row.qualified_leads or 0,
                "warm_leads": lead_row.warm_leads or 0,
            },
            "campaigns": {
                "total_campaigns": campaign_row.total_campaigns or 0,
                "active_campaigns": campaign_row.active_campaigns or 0,
                "upcoming_campaigns": campaign_row.upcoming_campaigns or 0,
                "ended_campaigns": campaign_row.ended_campaigns or 0,
            },
            "customers": {
                "total_customers": customer_row.total_customers or 0,
                "active_customers": customer_row.active_customers or 0,
                "inactive_customers": customer_row.inactive_customers or 0,
                "blacklisted_customers": customer_row.blacklisted_customers or 0,
            },
            "followups": {
                "total_followups": followup_row.total_followups or 0,
                "scheduled_followups": followup_row.scheduled_followups or 0,
                "completed_followups": followup_row.completed_followups or 0,
                "overdue_followups": followup_row.overdue_followups or 0,
            },
            "projects": {
                "total_projects": project_row.total_projects or 0,
                "planning_projects": project_row.planning_projects or 0,
                "ongoing_projects": project_row.ongoing_projects or 0,
                "completed_projects": project_row.completed_projects or 0,
            },
            "filters_applied": {
                "statuses": status_values,
                "priorities": priority_values,
                "sources": source_values,
                "ignored_filters": {
                    "campaigns": campaign_ignored_filters,
                    "projects": project_ignored_filters,
                },
            },
        }
    )


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
