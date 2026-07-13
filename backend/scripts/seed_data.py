import asyncio

from sqlalchemy import select

from app.core.security import hash_password
from app.database.postgres import SessionLocal
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.user import User

DEFAULT_ROLES = [
    ("ADMIN", "Full system access"),
    ("SEO_MANAGER", "SEO operations"),
    ("SALES", "Lead lifecycle updates"),
    ("ANALYST", "Analytics and report exports"),
]

DEFAULT_PERMISSIONS = [
    ("manage_users", "users"),
    ("manage_websites", "websites"),
    ("view_leads", "leads"),
    ("edit_leads", "leads"),
    ("manage_followups", "followups"),
    ("view_analytics", "analytics"),
    ("export_reports", "reports"),
    ("schedule_reports", "reports"),
    ("manage_campaigns", "campaigns"),
    ("manage_keywords", "keywords"),
]

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


async def seed() -> None:
    async with SessionLocal() as session:
        for name, description in DEFAULT_ROLES:
            existing = (await session.execute(select(Role).where(Role.name == name))).scalar_one_or_none()
            if not existing:
                session.add(Role(name=name, description=description))
        await session.commit()

        for name, module in DEFAULT_PERMISSIONS:
            existing = (await session.execute(select(Permission).where(Permission.name == name))).scalar_one_or_none()
            if not existing:
                session.add(Permission(name=name, module=module))
        await session.commit()

        roles = {r.name: r for r in (await session.execute(select(Role))).scalars().all()}
        permissions = {p.name: p for p in (await session.execute(select(Permission))).scalars().all()}
        for role_name, permission_names in ROLE_PERMISSION_MAP.items():
            role = roles.get(role_name)
            if not role:
                continue
            for permission_name in permission_names:
                permission = permissions.get(permission_name)
                if not permission:
                    continue
                exists = (
                    await session.execute(
                        select(RolePermission).where(
                            RolePermission.role_id == role.id,
                            RolePermission.permission_id == permission.id,
                        )
                    )
                ).scalar_one_or_none()
                if not exists:
                    session.add(RolePermission(role_id=role.id, permission_id=permission.id))
        await session.commit()

        admin_role = (await session.execute(select(Role).where(Role.name == "ADMIN"))).scalar_one()
        admin = (await session.execute(select(User).where(User.email == "admin@rpex.local"))).scalar_one_or_none()
        if not admin:
            session.add(
                User(
                    name="Platform Admin",
                    email="admin@rpex.local",
                    password_hash=hash_password("admin12345"),
                    role_id=admin_role.id,
                    is_active=True,
                )
            )
            await session.commit()


if __name__ == "__main__":
    asyncio.run(seed())
