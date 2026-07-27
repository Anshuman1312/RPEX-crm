from __future__ import annotations

import time

from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

# Endpoints excluded from verbose request/response logging
_SILENT_PATHS = {"/health", "/metrics", "/favicon.ico"}


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Structured request/response logging middleware.

    Logs:
      - Method, path, client IP on every incoming request
      - Status code and wall-clock duration on response
      - Correlation ID bound into every log entry for the request lifetime
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in _SILENT_PATHS:
            return await call_next(request)

        correlation_id: str = getattr(request.state, "correlation_id", "N/A")
        client_ip = request.client.host if request.client else "unknown"
        start = time.perf_counter()

        with logger.contextualize(correlation_id=correlation_id):
            logger.info(
                f"→ {request.method} {request.url.path}"
                f" | IP: {client_ip}"
                f" | UA: {request.headers.get('user-agent', '')[:80]}"
            )

            response = await call_next(request)

            duration_ms = (time.perf_counter() - start) * 1000
            level = "warning" if response.status_code >= 400 else "info"
            logger.log(
                level.upper(),
                f"← {request.method} {request.url.path}"
                f" | {response.status_code}"
                f" | {duration_ms:.2f}ms",
            )

            response.headers["X-Process-Time"] = f"{duration_ms:.2f}ms"

        return response
