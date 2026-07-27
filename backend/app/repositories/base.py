from __future__ import annotations

from typing import Generic, TypeVar, Any

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InspectionAttr

from app.database.base import Base
from app.core.exceptions import NotFoundException, OptimisticLockException

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """
    Generic repository for CRUD operations on any SQLAlchemy model.

    Handles soft deletes automatically by filtering is_deleted=false.
    """

    def __init__(self, session: AsyncSession, model: type[T]):
        self.session = session
        self.model = model

    async def create(self, **kwargs: Any) -> T:
        """Create and flush a new instance."""
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def get_by_id(self, id: Any, include_deleted: bool = False) -> T | None:
        """Fetch by primary key (respects soft delete by default)."""
        query = select(self.model).where(self.model.id == id)
        if not include_deleted and hasattr(self.model, "is_deleted"):
            query = query.where(self.model.is_deleted == False)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_or_404(self, id: Any, resource_name: str = "Resource") -> T:
        """Fetch by ID or raise NotFoundException."""
        instance = await self.get_by_id(id)
        if not instance:
            raise NotFoundException(resource_name, id)
        return instance

    async def list(
        self,
        skip: int = 0,
        limit: int = 20,
        include_deleted: bool = False,
    ) -> list[T]:
        """List instances with pagination (soft-delete aware)."""
        query = select(self.model).offset(skip).limit(limit)
        if not include_deleted and hasattr(self.model, "is_deleted"):
            query = query.where(self.model.is_deleted == False)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def count(self, include_deleted: bool = False) -> int:
        """Count all instances (soft-delete aware)."""
        query = select(func.count()).select_from(self.model)
        if not include_deleted and hasattr(self.model, "is_deleted"):
            query = query.where(self.model.is_deleted == False)
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def update(self, id: Any, **kwargs: Any) -> T:
        """Update an instance by ID."""
        instance = await self.get_or_404(id)
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        await self.session.flush()
        return instance

    async def update_with_version(self, id: Any, current_version: int, **kwargs: Any) -> T:
        """
        Optimistic lock update: only succeeds if version matches.

        Raises OptimisticLockException if version mismatch.
        """
        instance = await self.get_or_404(id)

        if not hasattr(instance, "version"):
            raise AttributeError(f"{self.model.__name__} does not support versioning")

        if instance.version != current_version:
            raise OptimisticLockException(self.model.__name__)

        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        instance.version += 1
        await self.session.flush()
        return instance

    async def soft_delete(self, id: Any) -> T:
        """Soft delete an instance (mark is_deleted=true)."""
        from datetime import datetime, timezone

        if not hasattr(self.model, "is_deleted"):
            raise AttributeError(f"{self.model.__name__} does not support soft delete")

        instance = await self.get_or_404(id)
        instance.is_deleted = True
        instance.deleted_at = datetime.now(timezone.utc)
        await self.session.flush()
        return instance

    async def delete(self, id: Any) -> None:
        """Hard delete an instance (use carefully!)."""
        instance = await self.get_or_404(id, include_deleted=True)
        await self.session.delete(instance)
        await self.session.flush()

    async def exists(self, id: Any, include_deleted: bool = False) -> bool:
        """Check if an instance exists."""
        query = select(func.count()).select_from(self.model).where(self.model.id == id)
        if not include_deleted and hasattr(self.model, "is_deleted"):
            query = query.where(self.model.is_deleted == False)
        result = await self.session.execute(query)
        return (result.scalar() or 0) > 0

    async def refresh(self, instance: T) -> T:
        """Refresh an instance from the database."""
        await self.session.refresh(instance)
        return instance
