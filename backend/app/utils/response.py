from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


# ── Pagination metadata ────────────────────────────────────────────────────────

class PaginationMeta(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool


# ── Standard response envelopes ────────────────────────────────────────────────

class APIResponse(BaseModel, Generic[T]):
    """Single-object success response."""

    success: bool = True
    message: str = "Success"
    data: T | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"arbitrary_types_allowed": True}


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated list response."""

    success: bool = True
    message: str = "Success"
    data: list[T]
    pagination: PaginationMeta
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"arbitrary_types_allowed": True}

    @classmethod
    def build(
        cls,
        data: list[T],
        total: int,
        page: int,
        page_size: int,
        message: str = "Success",
    ) -> "PaginatedResponse[T]":
        total_pages = math.ceil(total / page_size) if page_size > 0 else 0
        return cls(
            data=data,
            message=message,
            pagination=PaginationMeta(
                total=total,
                page=page,
                page_size=page_size,
                total_pages=total_pages,
                has_next=page < total_pages,
                has_previous=page > 1,
            ),
        )


# ── Convenience helpers (returns plain dict for JSONResponse) ──────────────────

def ok(data: Any = None, message: str = "Success") -> dict[str, Any]:
    return {
        "success": True,
        "message": message,
        "data": data,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def created(data: Any = None, message: str = "Created successfully.") -> dict[str, Any]:
    return ok(data=data, message=message)


def no_content(message: str = "Deleted successfully.") -> dict[str, Any]:
    return {"success": True, "message": message}


def error(message: str = "An error occurred.", data: Any = None) -> dict[str, Any]:
    return {
        "success": False,
        "message": message,
        "data": data,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
