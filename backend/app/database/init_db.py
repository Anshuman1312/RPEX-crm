from __future__ import annotations

from loguru import logger

from app.database.base import Base
from app.database.postgres import engine


async def init_db() -> None:
    """
    Create all tables defined in SQLAlchemy models.

    In production, Alembic migrations are the authoritative source of truth.
    This function is only used for tests and initial development setup.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialised.")


async def drop_db() -> None:
    """Drop all tables. NEVER call in production."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    logger.warning("All database tables dropped.")
