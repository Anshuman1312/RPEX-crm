import asyncio
from sqlalchemy import select

from app.core.security import hash_password
from app.database.postgres import Base, SessionLocal, engine
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.user import User

# 1. DEFINE ALL ROLES
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
    ("manage_documents", "documents"),
]

# 2. DEFINE ALL PERMISSIONS (Including new Plotting Project modules)
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
    ("manage_finance", "finance"),
    ("manage_hr", "hr"),
    ("manage_legal", "legal"),
    ("manage_partners", "partners"),
    ("view_customer_portal", "portal"),
    # New Plotting Project Permissions
    ("view_inventory", "inventory"),
    ("manage_inventory", "inventory"),
    ("view_customers", "customers"),
    ("manage_customers", "customers"),
    ("manage_bookings", "sales"),
    ("view_sales", "sales"),
    ("manage_site_visits", "site_visits"),
    ("manage_vendors", "vendors"),
    ("view_telecalling", "telecalling"),
    ("manage_tasks", "tasks"),
]

# 3. DEFINE ROLE-SPECIFIC MAPPINGS (Admins are handled dynamically below)
ROLE_PERMISSION_MAP = {
    "DIRECTOR": {"view_leads", "view_analytics", "export_reports", "schedule_reports", "manage_finance", "view_sales", "view_inventory"},
    "PROJECT_HEAD": {"view_leads", "edit_leads", "manage_followups", "view_analytics", "manage_campaigns", "manage_inventory", "view_sales"},
    "MARKETING_MANAGER": {"manage_websites", "view_analytics", "manage_campaigns", "manage_keywords"},
    "SALES_MANAGER": {"view_leads", "edit_leads", "manage_followups", "view_analytics", "manage_bookings", "view_sales", "manage_site_visits"},
    "SALES_EXECUTIVE": {"view_leads", "edit_leads", "manage_followups", "manage_site_visits", "view_inventory"},
    "TELECALLER": {"view_leads", "manage_followups", "view_telecalling", "manage_site_visits"},
    "CRM_EXECUTIVE": {"view_leads", "edit_leads", "manage_followups", "manage_customers", "view_inventory"},
    "FINANCE": {"view_analytics", "export_reports", "manage_finance"},
    "LEGAL": {"view_leads", "manage_legal", "view_customers"},
    "HR": {"manage_hr", "manage_users", "manage_tasks"},
    "CHANNEL_PARTNER": {"view_leads", "manage_partners"},
    "ANALYST": {"view_leads", "view_analytics", "export_reports"},
}

async def seed() -> None:
    async with engine.begin() as conn:
        # Note: Be careful with create_all if tables already exist
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:
        print("Starting Seeding Process...")

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
        
        all_permission_names = set(permissions.keys())

        for role_name, role_obj in roles.items():
            # RULE: SUPER_ADMIN and ADMIN get EVERY permission automatically
            if role_name in ["SUPER_ADMIN", "ADMIN"]:
                target_permissions = all_permission_names
            else:
                target_permissions = ROLE_PERMISSION_MAP.get(role_name, set())

            for p_name in target_permissions:
                permission = permissions.get(p_name)
                if not permission:
                    continue
                
                # Check if link already exists
                exists = (await session.execute(
                        select(RolePermission).where(
                            RolePermission.role_id == role_obj.id,
                            RolePermission.permission_id == permission.id,
                        )
                )).scalar_one_or_none()
                
                if not exists:
                    session.add(RolePermission(role_id=role_obj.id, permission_id=permission.id))
        
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
            print(f"Seeding completed. New Admin created: {admin_email}")
        else:
            print(f"Seeding completed. Admin {admin_email} already exists.")

if __name__ == "__main__":
    asyncio.run(seed())