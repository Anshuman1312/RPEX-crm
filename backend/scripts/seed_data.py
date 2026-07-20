import asyncio

# pyrefly: ignore [missing-import]
from sqlalchemy import select

from app.core.security import hash_password
from app.database.postgres import Base, SessionLocal, engine
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.user import User

DEFAULT_ROLES = [
    ("SUPER_ADMIN", "Highest level system access"),
    ("DIRECTOR", "Strategic oversight and full reporting access"),
    ("PROJECT_HEAD", "Management of specific projects and teams"),
    ("MARKETING_MANAGER", "Marketing campaign and strategy management"),
    ("SALES_MANAGER", "Sales team management and lead oversight"),
    ("SALES_EXECUTIVE", "Direct sales operations and lead handling"),
    ("TELECALLER", "Inbound and outbound calling operations"),
    ("CRM_EXECUTIVE", "Customer relationship management and data entry"),
    ("FINANCE", "Financial records and billing access"),
    ("LEGAL", "Legal documentation and compliance"),
    ("HR", "Human resources and employee management"),
    ("RECEPTIONIST", "Front desk and initial lead entry"),
    ("CHANNEL_PARTNER", "External partner access for lead submission"),
    ("DEVELOPER", "Technical system configuration"),
    ("CUSTOMER_PORTAL", "Restricted access for end customers"),
    ("ADMIN", "System administration"),
    ("SEO_MANAGER", "SEO operations and website management"),
    ("SALES", "General sales operations"),
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
    # New permissions for the new roles
    ("manage_finance", "finance"),
    ("manage_hr", "hr"),
    ("manage_legal", "legal"),
    ("manage_partners", "partners"),
    ("view_customer_portal", "portal"),
]

# Mapping permissions to roles
ROLE_PERMISSION_MAP = {
    "SUPER_ADMIN": {p[0] for p in DEFAULT_PERMISSIONS},  # Gets everything
    "ADMIN": {p[0] for p in DEFAULT_PERMISSIONS},
    "DIRECTOR": {"view_leads", "view_analytics", "export_reports", "schedule_reports", "manage_finance"},
    "PROJECT_HEAD": {"view_leads", "edit_leads", "manage_followups", "view_analytics", "manage_campaigns"},
    "MARKETING_MANAGER": {"manage_websites", "view_analytics", "manage_campaigns", "manage_keywords"},
    "SEO_MANAGER": {"manage_websites", "view_leads", "view_analytics", "manage_campaigns", "manage_keywords"},
    "SALES_MANAGER": {"view_leads", "edit_leads", "manage_followups", "view_analytics", "export_reports"},
    "SALES_EXECUTIVE": {"view_leads", "edit_leads", "manage_followups"},
    "SALES": {"view_leads", "edit_leads", "manage_followups"},
    "TELECALLER": {"view_leads", "manage_followups"},
    "CRM_EXECUTIVE": {"view_leads", "edit_leads", "manage_followups"},
    "FINANCE": {"view_analytics", "export_reports", "manage_finance"},
    "LEGAL": {"view_leads", "manage_legal"},
    "HR": {"manage_hr", "manage_users"},
    "RECEPTIONIST": {"view_leads", "manage_followups"},
    "CHANNEL_PARTNER": {"view_leads", "manage_partners"},
    "DEVELOPER": {"manage_websites", "manage_keywords", "view_analytics"},
    "CUSTOMER_PORTAL": {"view_customer_portal"},
    "ANALYST": {"view_leads", "view_analytics", "export_reports", "schedule_reports"},
}


async def seed() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:
        # 1. Seed Roles
        for name, description in DEFAULT_ROLES:
            existing = (await session.execute(select(Role).where(Role.name == name))).scalar_one_or_none()
            if not existing:
                session.add(Role(name=name, description=description))
        await session.commit()

        # 2. Seed Permissions
        for name, module in DEFAULT_PERMISSIONS:
            existing = (await session.execute(select(Permission).where(Permission.name == name))).scalar_one_or_none()
            if not existing:
                session.add(Permission(name=name, module=module))
        await session.commit()

        # 3. Map Roles to Permissions
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
                
                # Check if link already exists
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

        # 4. Create Initial Super Admin User
        super_admin_role = (await session.execute(select(Role).where(Role.name == "SUPER_ADMIN"))).scalar_one()
        admin_email = "admin@rpex.local"
        admin = (await session.execute(select(User).where(User.email == admin_email))).scalar_one_or_none()
        
        if not admin:
            session.add(
                User(
                    name="Platform Admin",
                    email=admin_email,
                    password_hash=hash_password("admin12345"),
                    role_id=super_admin_role.id,
                    is_active=True,
                )
            )
            await session.commit()
            print(f"Seeding completed. Admin created with role: {super_admin_role.name}")
        else:
            print("Seeding completed. Admin already exists.")


if __name__ == "__main__":
    asyncio.run(seed())