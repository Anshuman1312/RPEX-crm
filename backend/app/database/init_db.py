from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import app.models  # noqa: F401
from app.core.config import get_settings
from app.database.postgres import Base, SessionLocal, engine
from app.models.lead_status import LeadStatus
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission

settings = get_settings()

DEFAULT_ROLES = {
    "ADMIN": "Full system access",
    "SEO_MANAGER": "SEO operations",
    "SALES": "Lead follow-up and closure",
    "ANALYST": "Reporting and analytics",
}

DEFAULT_PERMISSIONS = {
    "manage_users": "users",
    "manage_websites": "websites",
    "view_leads": "leads",
    "edit_leads": "leads",
    "manage_followups": "followups",
    "view_analytics": "analytics",
    "export_reports": "reports",
    "schedule_reports": "reports",
    "manage_campaigns": "campaigns",
    "manage_keywords": "keywords",
}

ROLE_PERMISSION_MAP = {
    "ADMIN": {
        "manage_users",
        "manage_websites",
        "view_leads",
        "edit_leads",
        "manage_followups",
        "view_analytics",
        "export_reports",
        "schedule_reports",
        "manage_campaigns",
        "manage_keywords",
    },
    "SEO_MANAGER": {"manage_websites", "view_leads", "view_analytics", "manage_campaigns", "manage_keywords"},
    "SALES": {"view_leads", "edit_leads", "manage_followups"},
    "ANALYST": {"view_leads", "view_analytics", "export_reports", "schedule_reports"},
}

DEFAULT_LEAD_STATUSES = ["NEW", "CONTACTED", "FOLLOW_UP", "DEMO", "CONVERTED", "LOST"]


async def initialize_sqlite_schema_if_needed() -> None:
    if not settings.database_url.startswith("sqlite"):
        return

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:
        await seed_default_data(session)


async def seed_default_data(session: AsyncSession) -> None:
    for role_name, description in DEFAULT_ROLES.items():
        role = (await session.execute(select(Role).where(Role.name == role_name))).scalar_one_or_none()
        if not role:
            session.add(Role(name=role_name, description=description))

    for permission_name, module in DEFAULT_PERMISSIONS.items():
        permission = (await session.execute(select(Permission).where(Permission.name == permission_name))).scalar_one_or_none()
        if not permission:
            session.add(Permission(name=permission_name, module=module))

    for status_name in DEFAULT_LEAD_STATUSES:
        status = (await session.execute(select(LeadStatus).where(LeadStatus.name == status_name))).scalar_one_or_none()
        if not status:
            session.add(LeadStatus(name=status_name))

    await session.commit()

    roles = {row.name: row for row in (await session.execute(select(Role))).scalars().all()}
    permissions = {row.name: row for row in (await session.execute(select(Permission))).scalars().all()}

    for role_name, permission_names in ROLE_PERMISSION_MAP.items():
        role = roles.get(role_name)
        if not role:
            continue
        for permission_name in permission_names:
            permission = permissions.get(permission_name)
            if not permission:
                continue
            existing = (
                await session.execute(
                    select(RolePermission).where(
                        RolePermission.role_id == role.id,
                        RolePermission.permission_id == permission.id,
                    )
                )
            ).scalar_one_or_none()
            if not existing:
                session.add(RolePermission(role_id=role.id, permission_id=permission.id))

    await session.commit()
