from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

# ── Engine ─────────────────────────────────────────────────────────────────────
# pool_pre_ping=True: discard stale connections before handing them out,
# preventing "server closed the connection unexpectedly" errors under load.

engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.is_development,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_timeout=settings.DATABASE_POOL_TIMEOUT,
    pool_recycle=settings.DATABASE_POOL_RECYCLE,
    pool_pre_ping=True,
)

# ── Session factory ────────────────────────────────────────────────────────────
# expire_on_commit=False: keep ORM objects usable after commit without
# triggering lazy-load round trips in an async context.

AsyncSessionFactory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)
SessionLocal = AsyncSessionFactory

# ── FastAPI dependency ─────────────────────────────────────────────────────────

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Yield a database session with automatic commit/rollback management.

    Commit is attempted on clean exit; any exception triggers a rollback.
    The session is always closed in the finally block.
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


get_db = get_db_session

