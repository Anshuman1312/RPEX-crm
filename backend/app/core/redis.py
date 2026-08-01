from __future__ import annotations

import asyncio
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
    _initialization_failed: bool = False
    _retry_count: int = 0
    _max_retries: int = 3

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    @classmethod
    async def init(cls, retries: int = 3) -> None:
        """
        Initialise the default connection pool with retry logic.
        
        If initialization fails, app continues with degraded mode (no caching).
        """
        cls._max_retries = retries
        
        for attempt in range(retries):
            try:
                cls._default_pool = aioredis.ConnectionPool.from_url(
                    settings.REDIS_URL,
                    max_connections=settings.REDIS_MAX_CONNECTIONS,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_keepalive=True,
                )
                cls._default_client = aioredis.Redis(connection_pool=cls._default_pool)
                
                # Verify connectivity
                await asyncio.wait_for(cls._default_client.ping(), timeout=5.0)
                cls._initialization_failed = False
                
                from loguru import logger
                logger.info(f"Redis initialized successfully on attempt {attempt + 1}")
                return
                
            except asyncio.TimeoutError as exc:
                from loguru import logger
                logger.warning(f"Redis connection timeout (attempt {attempt + 1}/{retries}): {exc}")
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    
            except Exception as exc:
                from loguru import logger
                logger.warning(f"Redis initialization failed (attempt {attempt + 1}/{retries}): {exc}")
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)
        
        # All retries exhausted
        from loguru import logger
        logger.error(f"Redis initialization failed after {retries} attempts. Running in degraded mode.")
        cls._initialization_failed = True
        cls._default_client = None
        cls._default_pool = None

    @classmethod
    async def close(cls) -> None:
        """Close all connections. Call on application shutdown."""
        if cls._default_client:
            try:
                await cls._default_client.aclose()
            except Exception as exc:
                from loguru import logger
                logger.warning(f"Error closing Redis client: {exc}")
        if cls._default_pool:
            try:
                await cls._default_pool.aclose()
            except Exception as exc:
                from loguru import logger
                logger.warning(f"Error closing Redis pool: {exc}")
        cls._default_client = None
        cls._default_pool = None

    # ── Client accessors ──────────────────────────────────────────────────────

    @classmethod
    def get_client(cls) -> Redis:
        """Return the default Redis client (DB 0)."""
        if cls._default_client is None:
            if cls._initialization_failed:
                raise RuntimeError(
                    "Redis is unavailable. Application is running in degraded mode. "
                    "Session persistence, caching, and token revocation will not work."
                )
            raise RuntimeError("Redis not initialised. Call RedisManager.init() on startup.")
        return cls._default_client

    @classmethod
    def is_available(cls) -> bool:
        """Check if Redis is available."""
        return cls._default_client is not None and not cls._initialization_failed

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
        """Set a key with TTL, silently failing if Redis is unavailable."""
        if not cls.is_available():
            from loguru import logger
            logger.debug(f"Redis unavailable: skipping set_with_ttl for key={key}")
            return
        try:
            await cls.get_client().setex(key, ttl_seconds, value)
        except Exception as exc:
            from loguru import logger
            logger.warning(f"Failed to set Redis key {key}: {exc}")

    @classmethod
    async def get(cls, key: str) -> str | None:
        """Get a key, returning None if Redis is unavailable."""
        if not cls.is_available():
            return None
        try:
            return await cls.get_client().get(key)
        except Exception as exc:
            from loguru import logger
            logger.warning(f"Failed to get Redis key {key}: {exc}")
            return None

    @classmethod
    async def delete(cls, key: str) -> None:
        """Delete a key, silently failing if Redis is unavailable."""
        if not cls.is_available():
            return
        try:
            await cls.get_client().delete(key)
        except Exception as exc:
            from loguru import logger
            logger.warning(f"Failed to delete Redis key {key}: {exc}")

    @classmethod
    async def exists(cls, key: str) -> bool:
        """Check if a key exists, returning False if Redis is unavailable."""
        if not cls.is_available():
            return False
        try:
            return bool(await cls.get_client().exists(key))
        except Exception as exc:
            from loguru import logger
            logger.warning(f"Failed to check Redis key existence {key}: {exc}")
            return False


# ── FastAPI dependency ─────────────────────────────────────────────────────────

async def get_redis() -> AsyncGenerator[Redis, None]:
    """FastAPI dependency that yields the default Redis client."""
    yield RedisManager.get_client()


# ── Module-level redis_client alias ───────────────────────────────────────────
# Provides a `redis_client` name that delegates all attribute access to
# RedisManager.get_client() at call time, so imports like:
#   from app.core.redis import redis_client
# work correctly after RedisManager.init() is called on startup.

class _RedisClientProxy:
    """Lazy proxy — forwards every attribute access to the live RedisManager client."""

    def __getattr__(self, name: str):
        return getattr(RedisManager.get_client(), name)


redis_client = _RedisClientProxy()
