from __future__ import annotations

from loguru import logger
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.database.base import Base
from app.database.postgres import engine
from app.models.user import Role
import app.models  # noqa: F401  # register all models on Base metadata


async def _bootstrap_roles(conn) -> None:
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


async def init_db() -> None:
    """
    Create all tables defined in SQLAlchemy models.

    In production, Alembic migrations are the authoritative source of truth.
    This function is only used for tests and initial development setup.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await _bootstrap_roles(conn)
    logger.info("Database tables initialised.")


async def drop_db() -> None:
    """Drop all tables. NEVER call in production."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    logger.warning("All database tables dropped.")
