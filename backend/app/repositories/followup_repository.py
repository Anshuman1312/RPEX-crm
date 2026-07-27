"""
Repository layer for follow-up data access and persistence.

Repositories:
- FollowUpRepository: Follow-up CRUD with filtering, status transitions
- FollowUpTaskRepository: Task management
- FollowUpOutcomeRepository: Outcome tracking
- FollowUpAttachmentRepository: Attachment management
"""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, or_, desc, asc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.repositories.base import BaseRepository
from app.models.followup import FollowUp, FollowUpTask, FollowUpOutcome, FollowUpAttachment
from app.utils.enums import FollowUpStatus, FollowUpType, FollowUpOutcomeType, FollowUpTaskStatus


class FollowUpRepository(BaseRepository[FollowUp]):
    """Repository for follow-up operations."""

    async def get_by_number(self, followup_number: str) -> Optional[FollowUp]:
        """Get follow-up by number."""
        query = select(FollowUp).where(
            and_(FollowUp.followup_number == followup_number, FollowUp.is_deleted == False)
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_with_details(self, followup_id: UUID) -> Optional[FollowUp]:
        """Get follow-up with tasks and outcomes."""
        query = (
            select(FollowUp)
            .where(and_(FollowUp.id == followup_id, FollowUp.is_deleted == False))
            .options(
                joinedload(FollowUp.tasks),
                joinedload(FollowUp.outcomes),
            )
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_lead_followups(
        self,
        lead_id: UUID,
        statuses: Optional[List[FollowUpStatus]] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[FollowUp], int]:
        """Get follow-ups for a lead with optional filtering."""
        filters = [FollowUp.lead_id == lead_id, FollowUp.is_deleted == False]
        if statuses:
            filters.append(FollowUp.status.in_(statuses))

        # Count query
        count_query = select(func.count(FollowUp.id)).where(and_(*filters))
        count_result = await self.session.execute(count_query)
        total = count_result.scalars().first() or 0

        # Data query
        query = (
            select(FollowUp)
            .where(and_(*filters))
            .order_by(desc(FollowUp.scheduled_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        followups = result.scalars().all()

        return followups, total

    async def get_customer_followups(
        self,
        customer_id: UUID,
        statuses: Optional[List[FollowUpStatus]] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[FollowUp], int]:
        """Get follow-ups for a customer."""
        filters = [FollowUp.customer_id == customer_id, FollowUp.is_deleted == False]
        if statuses:
            filters.append(FollowUp.status.in_(statuses))

        # Count query
        from sqlalchemy import func
        count_query = select(func.count(FollowUp.id)).where(and_(*filters))
        count_result = await self.session.execute(count_query)
        total = count_result.scalars().first() or 0

        # Data query
        query = (
            select(FollowUp)
            .where(and_(*filters))
            .order_by(desc(FollowUp.scheduled_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        followups = result.scalars().all()

        return followups, total

    async def get_assigned_to_user(
        self,
        user_id: UUID,
        statuses: Optional[List[FollowUpStatus]] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[FollowUp], int]:
        """Get follow-ups assigned to user."""
        filters = [FollowUp.assigned_to_user_id == user_id, FollowUp.is_deleted == False]
        if statuses:
            filters.append(FollowUp.status.in_(statuses))

        # Count query
        from sqlalchemy import func
        count_query = select(func.count(FollowUp.id)).where(and_(*filters))
        count_result = await self.session.execute(count_query)
        total = count_result.scalars().first() or 0

        # Data query
        query = (
            select(FollowUp)
            .where(and_(*filters))
            .order_by(asc(FollowUp.scheduled_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        followups = result.scalars().all()

        return followups, total

    async def get_scheduled_for_date(self, target_date: datetime) -> List[FollowUp]:
        """Get follow-ups scheduled for a specific date."""
        start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)

        query = select(FollowUp).where(
            and_(
                FollowUp.scheduled_at >= start,
                FollowUp.scheduled_at < end,
                FollowUp.status == FollowUpStatus.SCHEDULED,
                FollowUp.is_deleted == False,
            )
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_overdue(self) -> List[FollowUp]:
        """Get overdue follow-ups."""
        now = datetime.utcnow()
        query = select(FollowUp).where(
            and_(
                FollowUp.scheduled_at < now,
                FollowUp.status == FollowUpStatus.SCHEDULED,
                FollowUp.is_deleted == False,
            )
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_upcoming(self, days: int = 7) -> List[FollowUp]:
        """Get follow-ups scheduled in the next N days."""
        now = datetime.utcnow()
        future = now + timedelta(days=days)

        query = select(FollowUp).where(
            and_(
                FollowUp.scheduled_at >= now,
                FollowUp.scheduled_at <= future,
                FollowUp.status == FollowUpStatus.SCHEDULED,
                FollowUp.is_deleted == False,
            )
        ).order_by(asc(FollowUp.scheduled_at))
        result = await self.session.execute(query)
        return result.scalars().all()

    async def list_with_filter(
        self,
        lead_id: Optional[UUID] = None,
        customer_id: Optional[UUID] = None,
        assigned_to_user_id: Optional[UUID] = None,
        statuses: Optional[List[FollowUpStatus]] = None,
        types: Optional[List[FollowUpType]] = None,
        priority: Optional[int] = None,
        is_critical: Optional[bool] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
        sort_by: str = "scheduled_at",
        sort_direction: str = "asc",
    ) -> Tuple[List[FollowUp], int]:
        """List follow-ups with comprehensive filtering."""
        filters = [FollowUp.is_deleted == False]

        if lead_id:
            filters.append(FollowUp.lead_id == lead_id)
        if customer_id:
            filters.append(FollowUp.customer_id == customer_id)
        if assigned_to_user_id:
            filters.append(FollowUp.assigned_to_user_id == assigned_to_user_id)
        if statuses:
            filters.append(FollowUp.status.in_(statuses))
        if types:
            filters.append(FollowUp.type.in_(types))
        if priority is not None:
            filters.append(FollowUp.priority == priority)
        if is_critical is not None:
            filters.append(FollowUp.is_critical == is_critical)
        if search:
            search_term = f"%{search}%"
            filters.append(
                or_(
                    FollowUp.subject.ilike(search_term),
                    FollowUp.description.ilike(search_term),
                    FollowUp.followup_number.ilike(search_term),
                )
            )

        # Count query
        from sqlalchemy import func
        count_query = select(func.count(FollowUp.id)).where(and_(*filters))
        count_result = await self.session.execute(count_query)
        total = count_result.scalars().first() or 0

        # Sort
        order_by = getattr(FollowUp, sort_by, FollowUp.scheduled_at)
        if sort_direction == "desc":
            order_by = desc(order_by)
        else:
            order_by = asc(order_by)

        # Data query
        query = (
            select(FollowUp)
            .where(and_(*filters))
            .order_by(order_by)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        followups = result.scalars().all()

        return followups, total

    async def count_by_status(self) -> dict:
        """Count follow-ups by status."""
        from sqlalchemy import func
        query = (
            select(FollowUp.status, func.count(FollowUp.id))
            .where(FollowUp.is_deleted == False)
            .group_by(FollowUp.status)
        )
        result = await self.session.execute(query)
        return {status: count for status, count in result.all()}

    async def count_by_type(self) -> dict:
        """Count follow-ups by type."""
        from sqlalchemy import func
        query = (
            select(FollowUp.type, func.count(FollowUp.id))
            .where(FollowUp.is_deleted == False)
            .group_by(FollowUp.type)
        )
        result = await self.session.execute(query)
        return {type_: count for type_, count in result.all()}


class FollowUpTaskRepository(BaseRepository[FollowUpTask]):
    """Repository for follow-up task operations."""

    async def get_followup_tasks(self, followup_id: UUID) -> List[FollowUpTask]:
        """Get all tasks for a follow-up."""
        query = (
            select(FollowUpTask)
            .where(
                and_(
                    FollowUpTask.followup_id == followup_id,
                    FollowUpTask.is_deleted == False,
                )
            )
            .order_by(asc(FollowUpTask.task_number))
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_pending_tasks(self, followup_id: UUID) -> List[FollowUpTask]:
        """Get pending tasks for follow-up."""
        query = (
            select(FollowUpTask)
            .where(
                and_(
                    FollowUpTask.followup_id == followup_id,
                    FollowUpTask.status == FollowUpTaskStatus.PENDING,
                    FollowUpTask.is_deleted == False,
                )
            )
            .order_by(asc(FollowUpTask.task_number))
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def count_by_status(self, followup_id: UUID) -> dict:
        """Count tasks by status for a follow-up."""
        from sqlalchemy import func
        query = (
            select(FollowUpTask.status, func.count(FollowUpTask.id))
            .where(
                and_(
                    FollowUpTask.followup_id == followup_id,
                    FollowUpTask.is_deleted == False,
                )
            )
            .group_by(FollowUpTask.status)
        )
        result = await self.session.execute(query)
        return {status: count for status, count in result.all()}


class FollowUpOutcomeRepository(BaseRepository[FollowUpOutcome]):
    """Repository for follow-up outcome operations."""

    async def get_followup_outcomes(self, followup_id: UUID) -> List[FollowUpOutcome]:
        """Get all outcomes for a follow-up."""
        query = (
            select(FollowUpOutcome)
            .where(
                and_(
                    FollowUpOutcome.followup_id == followup_id,
                    FollowUpOutcome.is_deleted == False,
                )
            )
            .order_by(desc(FollowUpOutcome.recorded_at))
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_latest_outcome(self, followup_id: UUID) -> Optional[FollowUpOutcome]:
        """Get most recent outcome for follow-up."""
        query = (
            select(FollowUpOutcome)
            .where(
                and_(
                    FollowUpOutcome.followup_id == followup_id,
                    FollowUpOutcome.is_deleted == False,
                )
            )
            .order_by(desc(FollowUpOutcome.recorded_at))
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def count_by_type(self) -> dict:
        """Count outcomes by type."""
        from sqlalchemy import func
        query = (
            select(FollowUpOutcome.outcome_type, func.count(FollowUpOutcome.id))
            .where(FollowUpOutcome.is_deleted == False)
            .group_by(FollowUpOutcome.outcome_type)
        )
        result = await self.session.execute(query)
        return {type_: count for type_, count in result.all()}

    async def get_total_deal_value(self) -> Decimal:
        """Get total deal value from outcomes."""
        from sqlalchemy import func
        query = select(
            func.coalesce(func.sum(FollowUpOutcome.estimated_deal_value), Decimal("0"))
        ).where(
            and_(
                FollowUpOutcome.estimated_deal_value.isnot(None),
                FollowUpOutcome.is_deleted == False,
            )
        )
        result = await self.session.execute(query)
        return result.scalars().first() or Decimal("0")


class FollowUpAttachmentRepository(BaseRepository[FollowUpAttachment]):
    """Repository for follow-up attachment operations."""

    async def get_followup_attachments(self, followup_id: UUID) -> List[FollowUpAttachment]:
        """Get all attachments for a follow-up."""
        query = (
            select(FollowUpAttachment)
            .where(
                and_(
                    FollowUpAttachment.followup_id == followup_id,
                    FollowUpAttachment.is_deleted == False,
                )
            )
            .order_by(desc(FollowUpAttachment.created_at))
        )
        result = await self.session.execute(query)
        return result.scalars().all()
