from __future__ import annotations

import logging
import sys

from loguru import logger

from app.core.config import settings


class _InterceptHandler(logging.Handler):
    """Route all standard library logging records through Loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back  # type: ignore[assignment]
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


_CONSOLE_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<magenta>{extra[correlation_id]}</magenta> | "
    "{message}"
)

_FILE_FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
    "{name}:{function}:{line} | {extra[correlation_id]} | {message}"
)

_INTERCEPTED_LOGGERS = [
    "uvicorn",
    "uvicorn.error",
    "uvicorn.access",
    "sqlalchemy.engine",
    "alembic",
    "celery",
]


def setup_logging() -> None:
    """Configure Loguru as the sole logging backend for the entire application."""
    logger.remove()

    # Bind a default correlation_id so the format never fails
    logger.configure(extra={"correlation_id": "N/A"})

    # ── Console handler ───────────────────────────────────────────────────────
    logger.add(
        sys.stdout,
        format=_CONSOLE_FORMAT,
        level=settings.LOG_LEVEL,
        colorize=True,
        backtrace=True,
        diagnose=not settings.is_production,
    )

    # ── Rotating file handler ─────────────────────────────────────────────────
    logger.add(
        settings.LOG_FILE_PATH,
        format=_FILE_FORMAT,
        level=settings.LOG_LEVEL,
        rotation="500 MB",
        retention="30 days",
        compression="gz",
        serialize=settings.is_production,   # JSON in production
        backtrace=True,
        enqueue=True,                        # Non-blocking, thread-safe writes
    )

    # ── Intercept stdlib logging ──────────────────────────────────────────────
    logging.basicConfig(handlers=[_InterceptHandler()], level=0, force=True)
    for name in _INTERCEPTED_LOGGERS:
        _logger = logging.getLogger(name)
        _logger.handlers = [_InterceptHandler()]
        _logger.propagate = False
