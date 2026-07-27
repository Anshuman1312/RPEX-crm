from __future__ import annotations

from typing import AsyncGenerator

import redis.asyncio as aioredis
from redis.asyncio import Redis, ConnectionPool

from app.core.config import settings


class RedisManager:
    """
    Singleton-style manager for Redis connection pools.

    Separate databases are used to isolate concerns:
      DB 0 — default / general purpose
      DB 1 — cache
      DB 2 — sessions / refresh tokens
      DB 3 — Celery broker + result backend
      DB 4 — rate limiting
    """

    _default_pool: ConnectionPool | None = None
    _default_client: Redis | None = None

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    @classmethod
    async def init(cls) -> None:
        """Initialise the default connection pool. Call once on application startup."""
        cls._default_pool = aioredis.ConnectionPool.from_url(
            settings.REDIS_URL,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            decode_responses=True,
        )
        cls._default_client = aioredis.Redis(connection_pool=cls._default_pool)
        # Verify connectivity
        await cls._default_client.ping()

    @classmethod
    async def close(cls) -> None:
        """Close all connections. Call on application shutdown."""
        if cls._default_client:
            await cls._default_client.aclose()
        if cls._default_pool:
            await cls._default_pool.aclose()
        cls._default_client = None
        cls._default_pool = None

    # ── Client accessors ──────────────────────────────────────────────────────

    @classmethod
    def get_client(cls) -> Redis:
        """Return the default Redis client (DB 0)."""
        if cls._default_client is None:
            raise RuntimeError("Redis not initialised. Call RedisManager.init() on startup.")
        return cls._default_client

    @classmethod
    def get_cache_client(cls) -> Redis:
        """Return a Redis client bound to the cache DB."""
        return aioredis.Redis.from_url(settings.redis_cache_url, decode_responses=True)

    @classmethod
    def get_session_client(cls) -> Redis:
        """Return a Redis client bound to the session DB."""
        return aioredis.Redis.from_url(settings.redis_session_url, decode_responses=True)

    @classmethod
    def get_rate_limit_client(cls) -> Redis:
        """Return a Redis client bound to the rate-limit DB."""
        return aioredis.Redis.from_url(settings.redis_rate_limit_url, decode_responses=True)

    # ── High-level helpers ────────────────────────────────────────────────────

    @classmethod
    async def set_with_ttl(cls, key: str, value: str, ttl_seconds: int) -> None:
        await cls.get_client().setex(key, ttl_seconds, value)

    @classmethod
    async def get(cls, key: str) -> str | None:
        return await cls.get_client().get(key)

    @classmethod
    async def delete(cls, key: str) -> None:
        await cls.get_client().delete(key)

    @classmethod
    async def exists(cls, key: str) -> bool:
        return bool(await cls.get_client().exists(key))


# ── FastAPI dependency ─────────────────────────────────────────────────────────

async def get_redis() -> AsyncGenerator[Redis, None]:
    """FastAPI dependency that yields the default Redis client."""
    yield RedisManager.get_client()
