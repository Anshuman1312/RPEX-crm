from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import (
    CRMException,
    crm_exception_handler,
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.core.logging import setup_logging
from app.core.redis import RedisManager
from app.database.postgres import engine
from app.middleware.correlation_middleware import CorrelationIDMiddleware
from app.middleware.logging_middleware import RequestLoggingMiddleware
from app.middleware.security import setup_security


# ── Lifespan ───────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # ── Startup ───────────────────────────────────────────────────────────────
    setup_logging()
    await RedisManager.init()

    from loguru import logger
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} starting [{settings.APP_ENV}]")

    yield

    # ── Shutdown ──────────────────────────────────────────────────────────────
    from loguru import logger
    logger.info("Shutting down — closing connections.")
    await RedisManager.close()
    await engine.dispose()


# ── App factory ────────────────────────────────────────────────────────────────

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "Enterprise Real Estate CRM API — "
            "manages leads, customers, projects, inventory, bookings and payments."
        ),
        # Disable interactive docs in production
        docs_url="/api/docs" if not settings.is_production else None,
        redoc_url="/api/redoc" if not settings.is_production else None,
        openapi_url="/api/openapi.json" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # ── Middleware (outermost → innermost) ────────────────────────────────────
    # CORS must be outermost so preflight requests are handled before auth.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Correlation-ID", "X-Process-Time"],
    )
    # Logging runs after correlation so the ID is available in log records.
    app.add_middleware(RequestLoggingMiddleware)
    # Correlation must be innermost so it runs first on the way in.
    app.add_middleware(CorrelationIDMiddleware)

    # ── Security hardening ────────────────────────────────────────────────────
    setup_security(app)

    # ── Exception handlers ────────────────────────────────────────────────────
    app.add_exception_handler(CRMException, crm_exception_handler)          # type: ignore[arg-type]
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unhandled_exception_handler)

    # ── Prometheus metrics ────────────────────────────────────────────────────
    from prometheus_fastapi_instrumentator import Instrumentator

    Instrumentator(
        should_group_status_codes=True,
        should_ignore_untemplated=True,
        excluded_handlers=["/health", "/metrics"],
    ).instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)

    # ── API routes ────────────────────────────────────────────────────────────
    app.include_router(api_router, prefix="/api/v1")

    # ── Built-in endpoints ────────────────────────────────────────────────────
    @app.get("/health", tags=["Health"], include_in_schema=False)
    async def health_check() -> dict:
        redis_ok = False
        try:
            redis_ok = await RedisManager.get_client().ping()
        except Exception:
            pass
        return {
            "status": "healthy",
            "version": settings.APP_VERSION,
            "environment": settings.APP_ENV,
            "services": {"redis": "ok" if redis_ok else "unavailable"},
        }

    return app


app: FastAPI = create_app()
