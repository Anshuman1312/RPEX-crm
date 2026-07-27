from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TimestampMixin:
    """Adds created_at / updated_at with automatic server-side defaults."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utcnow,
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utcnow,
        server_default=func.now(),
        onupdate=_utcnow,
        nullable=False,
    )


class AuditUserMixin:
    """Tracks which user created / last updated the row."""

    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )


class SoftDeleteMixin:
    """Soft-delete support — rows are never physically removed."""

    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class VersionMixin:
    """
    Optimistic locking via a monotonically incrementing version counter.

    The service layer must pass the client-supplied version when updating;
    the repository checks `WHERE id = :id AND version = :version` before
    issuing the UPDATE and increments the counter on success.
    """

    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)


class PrimaryKeyMixin:
    """UUID primary key — generated at the application layer."""

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )


class BaseModelMixin(PrimaryKeyMixin, TimestampMixin, AuditUserMixin, SoftDeleteMixin):
    """
    Full base mixin applied to every business entity table.

    Provides: id, created_at, updated_at, created_by, updated_by,
              is_deleted, deleted_at.
    """


class VersionedModelMixin(BaseModelMixin, VersionMixin):
    """
    Base mixin for entities that require optimistic locking.

    Applied to: Unit, Booking, Payment.
    """
