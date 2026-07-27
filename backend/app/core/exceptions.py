from __future__ import annotations

from typing import Any

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


# ── Base Exception ─────────────────────────────────────────────────────────────

class CRMException(Exception):
    """Root exception for all CRM-specific errors."""

    def __init__(
        self,
        message: str,
        code: str = "CRM_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Any = None,
    ) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details
        super().__init__(message)


# ── Domain Exceptions ──────────────────────────────────────────────────────────

class NotFoundException(CRMException):
    def __init__(self, resource: str, identifier: Any = None) -> None:
        msg = (
            f"{resource} not found"
            if identifier is None
            else f"{resource} '{identifier}' not found"
        )
        super().__init__(message=msg, code="NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)


class ConflictException(CRMException):
    def __init__(self, message: str) -> None:
        super().__init__(message=message, code="CONFLICT", status_code=status.HTTP_409_CONFLICT)


class ValidationException(CRMException):
    def __init__(self, message: str, field: str | None = None) -> None:
        self.field = field
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class AuthenticationException(CRMException):
    def __init__(self, message: str = "Authentication failed.") -> None:
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class AuthorizationException(CRMException):
    def __init__(self, message: str = "You do not have permission to perform this action.") -> None:
        super().__init__(
            message=message,
            code="AUTHORIZATION_ERROR",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class BusinessRuleException(CRMException):
    def __init__(self, message: str, rule: str | None = None) -> None:
        self.rule = rule
        super().__init__(
            message=message,
            code="BUSINESS_RULE_VIOLATION",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class OptimisticLockException(CRMException):
    def __init__(self, resource: str) -> None:
        super().__init__(
            message=f"{resource} was modified by another request. Please reload and retry.",
            code="OPTIMISTIC_LOCK_CONFLICT",
            status_code=status.HTTP_409_CONFLICT,
        )


class RateLimitException(CRMException):
    def __init__(self) -> None:
        super().__init__(
            message="Too many requests. Please slow down.",
            code="RATE_LIMIT_EXCEEDED",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )


class ExternalServiceException(CRMException):
    def __init__(self, service: str, message: str) -> None:
        super().__init__(
            message=f"External service error ({service}): {message}",
            code="EXTERNAL_SERVICE_ERROR",
            status_code=status.HTTP_502_BAD_GATEWAY,
        )


class TokenExpiredException(CRMException):
    def __init__(self) -> None:
        super().__init__(
            message="Token has expired. Please log in again.",
            code="TOKEN_EXPIRED",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class InvalidTokenException(CRMException):
    def __init__(self) -> None:
        super().__init__(
            message="Invalid or malformed token.",
            code="INVALID_TOKEN",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class AccountDisabledException(CRMException):
    def __init__(self) -> None:
        super().__init__(
            message="Your account has been disabled. Please contact an administrator.",
            code="ACCOUNT_DISABLED",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class InvalidStateTransitionException(CRMException):
    def __init__(self, resource: str, from_state: str, to_state: str) -> None:
        super().__init__(
            message=f"Cannot transition {resource} from '{from_state}' to '{to_state}'.",
            code="INVALID_STATE_TRANSITION",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class DuplicateEntryException(CRMException):
    def __init__(self, resource: str, field: str) -> None:
        super().__init__(
            message=f"{resource} with this {field} already exists.",
            code="DUPLICATE_ENTRY",
            status_code=status.HTTP_409_CONFLICT,
        )


# ── HTTP Exception Handlers ────────────────────────────────────────────────────

def _build_error_body(
    code: str,
    message: str,
    details: Any = None,
    request_id: str | None = None,
) -> dict[str, Any]:
    body: dict[str, Any] = {"success": False, "code": code, "message": message}
    if details is not None:
        body["details"] = details
    if request_id:
        body["request_id"] = request_id
    return body


async def crm_exception_handler(request: Request, exc: CRMException) -> JSONResponse:
    request_id: str | None = getattr(request.state, "correlation_id", None)
    return JSONResponse(
        status_code=exc.status_code,
        content=_build_error_body(exc.code, exc.message, exc.details, request_id),
    )


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    request_id: str | None = getattr(request.state, "correlation_id", None)
    return JSONResponse(
        status_code=exc.status_code,
        content=_build_error_body("HTTP_ERROR", str(exc.detail), request_id=request_id),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    request_id: str | None = getattr(request.state, "correlation_id", None)
    errors = [
        {
            "field": " → ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        }
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=_build_error_body(
            "VALIDATION_ERROR",
            "Request validation failed.",
            details=errors,
            request_id=request_id,
        ),
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    from loguru import logger

    request_id: str = getattr(request.state, "correlation_id", "N/A")
    logger.exception(f"Unhandled exception | request_id={request_id} | path={request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=_build_error_body(
            "INTERNAL_SERVER_ERROR",
            "An unexpected error occurred. Please try again later.",
            request_id=request_id,
        ),
    )
