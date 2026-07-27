from __future__ import annotations

from fastapi import Query
from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    """
    Standard pagination + sorting parameters.

    Used as a FastAPI dependency via `get_pagination_params`.
    """

    page: int = Field(default=1, ge=1, description="Page number (1-based)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page (max 100)")
    sort_by: str | None = Field(default=None, description="Column name to sort by")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$", description="asc or desc")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size

    @property
    def is_ascending(self) -> bool:
        return self.sort_order == "asc"


# ── FastAPI dependency ─────────────────────────────────────────────────────────

def get_pagination_params(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    sort_by: str | None = Query(default=None, description="Sort column"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$", description="Sort direction"),
) -> PaginationParams:
    return PaginationParams(
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
