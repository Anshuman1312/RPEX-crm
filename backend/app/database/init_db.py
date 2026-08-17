from __future__ import annotations

from loguru import logger
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.database.base import Base
from app.database.postgres import engine
import uuid
from app.models.user import Role, Department, Designation
import app.models  # noqa: F401  # register all models on Base metadata


async def _bootstrap_roles(conn) -> None:
    """Bootstrap core system roles."""
    core_roles = [
        {"name": "SUPER_ADMIN", "code": "SUPER_ADMIN", "description": "System super administrator", "is_system": True},
        {"name": "ADMIN", "code": "ADMIN", "description": "System administrator", "is_system": True},
        {"name": "SALES_MANAGER", "code": "SALES_MANAGER", "description": "Sales manager", "is_system": True},
        {"name": "SALES_EXECUTIVE", "code": "SALES_EXECUTIVE", "description": "Sales executive", "is_system": True},
        {"name": "TELECALLER", "code": "TELECALLER", "description": "Telecalling executive", "is_system": True},
        {"name": "CRM_EXECUTIVE", "code": "CRM_EXECUTIVE", "description": "CRM executive", "is_system": True},
        {"name": "SALES", "code": "SALES", "description": "Sales user", "is_system": True},
    ]
    stmt = pg_insert(Role).values(core_roles)
    stmt = stmt.on_conflict_do_nothing(index_elements=[Role.name])
    await conn.execute(stmt)
    logger.info(f"Bootstrapped {len(core_roles)} core system roles")


async def _bootstrap_departments_designations(conn) -> None:
    sales_dept_id = uuid.UUID("11111111-1111-1111-1111-111111111111")
    ops_dept_id = uuid.UUID("22222222-2222-2222-2222-222222222222")
    fin_dept_id = uuid.UUID("33333333-3333-3333-3333-333333333333")
    mktg_dept_id = uuid.UUID("44444444-4444-4444-4444-444444444444")
    hr_dept_id = uuid.UUID("55555555-5555-5555-5555-555555555555")

    core_departments = [
        {"id": sales_dept_id, "name": "Sales", "code": "SALES", "is_active": True},
        {"id": ops_dept_id, "name": "Operations", "code": "OPERATIONS", "is_active": True},
        {"id": fin_dept_id, "name": "Finance", "code": "FINANCE", "is_active": True},
        {"id": mktg_dept_id, "name": "Marketing", "code": "MARKETING", "is_active": True},
        {"id": hr_dept_id, "name": "HR", "code": "HR", "is_active": True},
    ]

    dept_stmt = pg_insert(Department).values(core_departments)
    dept_stmt = dept_stmt.on_conflict_do_nothing(index_elements=[Department.name])
    await conn.execute(dept_stmt)

    core_designations = [
        {"id": uuid.UUID("11111111-1111-1111-1111-222222222221"), "name": "Associate", "code": "ASSOCIATE", "department_id": sales_dept_id, "level": 1, "is_active": True},
        {"id": uuid.UUID("11111111-1111-1111-1111-222222222222"), "name": "Senior", "code": "SENIOR", "department_id": sales_dept_id, "level": 2, "is_active": True},
        {"id": uuid.UUID("11111111-1111-1111-1111-222222222223"), "name": "Lead", "code": "LEAD", "department_id": sales_dept_id, "level": 3, "is_active": True},
        {"id": uuid.UUID("11111111-1111-1111-1111-222222222224"), "name": "Manager", "code": "MANAGER", "department_id": sales_dept_id, "level": 4, "is_active": True},

        {"id": uuid.UUID("22222222-2222-2222-2222-222222222221"), "name": "Associate", "code": "ASSOCIATE", "department_id": ops_dept_id, "level": 1, "is_active": True},
        {"id": uuid.UUID("22222222-2222-2222-2222-222222222222"), "name": "Senior", "code": "SENIOR", "department_id": ops_dept_id, "level": 2, "is_active": True},
        {"id": uuid.UUID("22222222-2222-2222-2222-222222222223"), "name": "Lead", "code": "LEAD", "department_id": ops_dept_id, "level": 3, "is_active": True},
        {"id": uuid.UUID("22222222-2222-2222-2222-222222222224"), "name": "Manager", "code": "MANAGER", "department_id": ops_dept_id, "level": 4, "is_active": True},

        {"id": uuid.UUID("33333333-3333-3333-3333-222222222221"), "name": "Associate", "code": "ASSOCIATE", "department_id": fin_dept_id, "level": 1, "is_active": True},
        {"id": uuid.UUID("33333333-3333-3333-3333-222222222222"), "name": "Senior", "code": "SENIOR", "department_id": fin_dept_id, "level": 2, "is_active": True},
        {"id": uuid.UUID("33333333-3333-3333-3333-222222222223"), "name": "Lead", "code": "LEAD", "department_id": fin_dept_id, "level": 3, "is_active": True},
        {"id": uuid.UUID("33333333-3333-3333-3333-222222222224"), "name": "Manager", "code": "MANAGER", "department_id": fin_dept_id, "level": 4, "is_active": True},

        {"id": uuid.UUID("44444444-4444-4444-4444-222222222221"), "name": "Associate", "code": "ASSOCIATE", "department_id": mktg_dept_id, "level": 1, "is_active": True},
        {"id": uuid.UUID("44444444-4444-4444-4444-222222222222"), "name": "Senior", "code": "SENIOR", "department_id": mktg_dept_id, "level": 2, "is_active": True},
        {"id": uuid.UUID("44444444-4444-4444-4444-222222222223"), "name": "Lead", "code": "LEAD", "department_id": mktg_dept_id, "level": 3, "is_active": True},
        {"id": uuid.UUID("44444444-4444-4444-4444-222222222224"), "name": "Manager", "code": "MANAGER", "department_id": mktg_dept_id, "level": 4, "is_active": True},

        {"id": uuid.UUID("55555555-5555-5555-5555-222222222221"), "name": "Associate", "code": "ASSOCIATE", "department_id": hr_dept_id, "level": 1, "is_active": True},
        {"id": uuid.UUID("55555555-5555-5555-5555-222222222222"), "name": "Senior", "code": "SENIOR", "department_id": hr_dept_id, "level": 2, "is_active": True},
        {"id": uuid.UUID("55555555-5555-5555-5555-222222222223"), "name": "Lead", "code": "LEAD", "department_id": hr_dept_id, "level": 3, "is_active": True},
        {"id": uuid.UUID("55555555-5555-5555-5555-222222222224"), "name": "Manager", "code": "MANAGER", "department_id": hr_dept_id, "level": 4, "is_active": True},
    ]

    desig_stmt = pg_insert(Designation).values(core_designations)
    desig_stmt = desig_stmt.on_conflict_do_nothing(index_elements=["code", "department_id"])
    await conn.execute(desig_stmt)


async def init_db() -> None:
    """
    Create all tables defined in SQLAlchemy models.

    In production, Alembic migrations are the authoritative source of truth.
    This function is only used for tests and initial development setup.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await _bootstrap_roles(conn)
        await _bootstrap_departments_designations(conn)
    logger.info("Database tables initialised.")


async def init_roles_only() -> None:
    """
    Initialize or sync core system roles.

    This can be called independently to ensure roles exist,
    even if schema initialization is disabled.
    """
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT to_regclass('public.roles')"))
        if result.scalar() is None:
            logger.warning("Roles table not found — skipping role bootstrap (run migrations first).")
            return
        await _bootstrap_roles(conn)


async def drop_db() -> None:
    """Drop all tables. NEVER call in production."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    logger.warning("All database tables dropped.")
