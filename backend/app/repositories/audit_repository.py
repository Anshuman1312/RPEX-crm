"""
Repository for audit log queries — read-only analytics on immutable records.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, desc, select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


class AuditLogRepository:
    """Read-heavy repository for audit log queries."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, **kwargs) -> AuditLog:
        """Insert an immutable audit log entry."""
        entry = AuditLog(**kwargs)
        self.session.add(entry)
        await self.session.flush()
        return entry

    async def get(self, log_id: UUID) -> Optional[AuditLog]:
        """Get a single audit log entry."""
        result = await self.session.execute(
            select(AuditLog).where(AuditLog.id == log_id)
        )
        return result.scalars().first()

    async def list_with_filter(
        self,
        user_id: Optional[UUID] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[UUID] = None,
        action: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[AuditLog], int]:
        """List audit logs with comprehensive filtering."""
        filters = []

        if user_id:
            filters.append(AuditLog.user_id == user_id)
        if entity_type:
            filters.append(AuditLog.entity_type == entity_type)
        if entity_id:
            filters.append(AuditLog.entity_id == entity_id)
        if action:
            filters.append(AuditLog.action.ilike(f"%{action}%"))
        if status:
            filters.append(AuditLog.status == status)
        if start_date:
            filters.append(AuditLog.created_at >= start_date)
        if end_date:
            filters.append(AuditLog.created_at <= end_date)
        if search:
            term = f"%{search}%"
            filters.append(or_(
                AuditLog.description.ilike(term),
                AuditLog.entity_display.ilike(term),
                AuditLog.user_email.ilike(term),
                AuditLog.action.ilike(term),
            ))

        where = and_(*filters) if filters else True

        count_q = select(func.count(AuditLog.id)).where(where)
        total = (await self.session.execute(count_q)).scalar() or 0

        q = (
            select(AuditLog)
            .where(where)
            .order_by(desc(AuditLog.created_at))
            .offset(skip)
            .limit(limit)
        )
        rows = (await self.session.execute(q)).scalars().all()
        return rows, total

    async def get_entity_history(
        self, entity_type: str, entity_id: UUID
    ) -> List[AuditLog]:
        """Full history for a specific entity."""
        q = (
            select(AuditLog)
            .where(
                and_(
                    AuditLog.entity_type == entity_type,
                    AuditLog.entity_id == entity_id,
                )
            )
            .order_by(desc(AuditLog.created_at))
        )
        return (await self.session.execute(q)).scalars().all()

    async def get_user_activity(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[AuditLog], int]:
        """Audit trail for a specific user."""
        filters = AuditLog.user_id == user_id

        total = (await self.session.execute(
            select(func.count(AuditLog.id)).where(filters)
        )).scalar() or 0

        rows = (await self.session.execute(
            select(AuditLog)
            .where(filters)
            .order_by(desc(AuditLog.created_at))
            .offset(skip)
            .limit(limit)
        )).scalars().all()

        return rows, total

    async def get_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> dict:
        """Aggregate statistics over a date range."""
        filters = []
        if start_date:
            filters.append(AuditLog.created_at >= start_date)
        if end_date:
            filters.append(AuditLog.created_at <= end_date)
        where = and_(*filters) if filters else True

        total = (await self.session.execute(
            select(func.count(AuditLog.id)).where(where)
        )).scalar() or 0

        success = (await self.session.execute(
            select(func.count(AuditLog.id)).where(
                and_(where, AuditLog.status == "success")
            )
        )).scalar() or 0

        failure = (await self.session.execute(
            select(func.count(AuditLog.id)).where(
                and_(where, AuditLog.status == "failure")
            )
        )).scalar() or 0

        # By action
        by_action_q = (
            select(AuditLog.action, func.count(AuditLog.id))
            .where(where)
            .group_by(AuditLog.action)
            .order_by(desc(func.count(AuditLog.id)))
            .limit(20)
        )
        by_action = dict((await self.session.execute(by_action_q)).all())

        # By entity type
        by_entity_q = (
            select(AuditLog.entity_type, func.count(AuditLog.id))
            .where(where)
            .group_by(AuditLog.entity_type)
        )
        by_entity = dict((await self.session.execute(by_entity_q)).all())

        # Top users
        by_user_q = (
            select(
                AuditLog.user_email,
                func.count(AuditLog.id).label("count")
            )
            .where(and_(where, AuditLog.user_email.isnot(None)))
            .group_by(AuditLog.user_email)
            .order_by(desc(func.count(AuditLog.id)))
            .limit(10)
        )
        by_user_rows = (await self.session.execute(by_user_q)).all()
        by_user = [{"email": row[0], "count": row[1]} for row in by_user_rows]

        return {
            "total_entries": total,
            "success_count": success,
            "failure_count": failure,
            "by_action": by_action,
            "by_entity_type": by_entity,
            "by_user": by_user,
        }


class AuditRepository(AuditLogRepository):
    """Backward-compatible alias for older imports."""

