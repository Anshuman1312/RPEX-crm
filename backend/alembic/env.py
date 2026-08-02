"""
Alembic environment configuration.
Supports async SQLAlchemy engine with PostgreSQL for migrations.
"""
import os
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from alembic import context

# Import all models so Alembic can detect them
from app.database.base import Base  # noqa: F401
import app.models  # noqa: F401 - registers all models

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode using asyncpg."""
    from app.core.config import settings
    import asyncio
    import time
    
    async def async_run():
        from sqlalchemy.ext.asyncio import create_async_engine
        
        max_retries = 5
        for attempt in range(max_retries):
            try:
                engine = create_async_engine(
                    settings.DATABASE_URL,
                    poolclass=pool.NullPool,
                )
                async with engine.connect() as connection:
                    await connection.run_sync(do_run_migrations)
                await engine.dispose()
                return
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"Attempt {attempt + 1}: Connection failed - {e}")
                    print(f"Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    raise
    
    asyncio.run(async_run())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
