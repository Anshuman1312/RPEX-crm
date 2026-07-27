from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select, and_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.lead import Lead, LeadActivity, LeadAssignment
from app.repositories.base import BaseRepository
from app.utils.filters import LeadFilterParams


class LeadRepository(BaseRepository[Lead]):
    """Lead-specific repository with filtering and search."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Lead)

    async def get_by_lead_number(self, lead_number: str) -> Lead | None:
        """Fetch lead by lead number."""
        query = select(self.model).where(
            and_(
                self.model.lead_number == lead_number,
                self.model.is_deleted == False,
            )
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_with_activities(self, lead_id: str) -> Lead | None:
        """Fetch lead with all activities eagerly loaded."""
        query = (
            select(self.model)
            .where(
                and_(
                    self.model.id == lead_id,
                    self.model.is_deleted == False,
                )
            )
            .options(selectinload(self.model.activities))
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def list_with_filter(
        self,
        filters: LeadFilterParams,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Lead], int]:
        """
        List leads with comprehensive filtering.

        Returns: (leads, total_count)
        """
        query = select(self.model).where(self.model.is_deleted == False)

        # ── Search ───────────────────────────────────────────────────────────
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.where(
                (self.model.full_name.ilike(search_term))
                | (self.model.email.ilike(search_term))
                | (self.model.phone.ilike(search_term))
            )

        # ── Status filter ────────────────────────────────────────────────────
        if filters.statuses:
            query = query.where(self.model.status.in_(filters.statuses))

        # ── Source filter ────────────────────────────────────────────────────
        if filters.sources:
            query = query.where(self.model.source.in_(filters.sources))

        # ── Date range ───────────────────────────────────────────────────────
        if filters.created_after:
            query = query.where(self.model.created_at >= filters.created_after)

        if filters.created_before:
            query = query.where(self.model.created_at <= filters.created_before)

        # ── Assignment filter ────────────────────────────────────────────────
        if filters.assigned_to_user_id:
            query = query.where(self.model.assigned_to_user_id == filters.assigned_to_user_id)

        # ── Priority filter ──────────────────────────────────────────────────
        if filters.priorities:
            query = query.where(self.model.priority.in_(filters.priorities))

        # ── Project interest filter ──────────────────────────────────────────
        if filters.project_ids:
            query = query.where(self.model.interested_in_project.in_(filters.project_ids))

        # ── Count before pagination ──────────────────────────────────────────
        count_query = select(func.count()).select_from(self.model).where(
            and_(*[condition for condition in [self.model.is_deleted == False]])
        )
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0

        # ── Sorting ──────────────────────────────────────────────────────────
        if filters.sort_direction.value == "desc":
            query = query.order_by(desc(getattr(self.model, filters.sort_by)))
        else:
            query = query.order_by(getattr(self.model, filters.sort_by))

        # ── Pagination ───────────────────────────────────────────────────────
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        return result.scalars().all(), total

    async def get_overdue_followups(self, days: int = 1) -> list[Lead]:
        """Get leads with overdue followups."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        query = select(self.model).where(
            and_(
                self.model.is_deleted == False,
                self.model.next_followup_at <= cutoff,
            )
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_status(self, status: str, skip: int = 0, limit: int = 20) -> tuple[list[Lead], int]:
        """Get leads by status."""
        query = select(self.model).where(
            and_(
                self.model.is_deleted == False,
                self.model.status == status,
            )
        )
        count_query = select(func.count()).select_from(self.model).where(
            and_(
                self.model.is_deleted == False,
                self.model.status == status,
            )
        )
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0

        query = query.order_by(desc(self.model.created_at)).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all(), total

    async def count_by_status(self) -> dict[str, int]:
        """Count leads by status."""
        query = select(self.model.status, func.count()).where(
            self.model.is_deleted == False
        ).group_by(self.model.status)

        result = await self.session.execute(query)
        return {row[0]: row[1] for row in result.all()}

    async def count_by_source(self) -> dict[str, int]:
        """Count leads by source."""
        query = select(self.model.source, func.count()).where(
            self.model.is_deleted == False
        ).group_by(self.model.source)

        result = await self.session.execute(query)
        return {row[0]: row[1] for row in result.all()}

    async def get_unassigned(self, skip: int = 0, limit: int = 20) -> tuple[list[Lead], int]:
        """Get unassigned leads."""
        query = select(self.model).where(
            and_(
                self.model.is_deleted == False,
                self.model.assigned_to_user_id == None,
            )
        )
        count_query = select(func.count()).select_from(self.model).where(
            and_(
                self.model.is_deleted == False,
                self.model.assigned_to_user_id == None,
            )
        )
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0

        query = query.order_by(desc(self.model.created_at)).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all(), total


class LeadActivityRepository(BaseRepository[LeadActivity]):
    """Lead activity repository."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, LeadActivity)

    async def get_lead_activities(
        self, lead_id: str, skip: int = 0, limit: int = 20
    ) -> tuple[list[LeadActivity], int]:
        """Get activities for a lead."""
        query = select(self.model).where(self.model.lead_id == lead_id)

        count_query = select(func.count()).select_from(self.model).where(
            self.model.lead_id == lead_id
        )
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0

        query = query.order_by(desc(self.model.activity_date)).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all(), total

    async def get_latest_activity(self, lead_id: str) -> LeadActivity | None:
        """Get most recent activity for a lead."""
        query = (
            select(self.model)
            .where(self.model.lead_id == lead_id)
            .order_by(desc(self.model.activity_date))
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalars().first()


class LeadAssignmentRepository(BaseRepository[LeadAssignment]):
    """Lead assignment history repository."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, LeadAssignment)

    async def get_lead_assignments(self, lead_id: str) -> list[LeadAssignment]:
        """Get assignment history for a lead."""
        query = (
            select(self.model)
            .where(self.model.lead_id == lead_id)
            .order_by(desc(self.model.assigned_at))
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_active_assignment(self, lead_id: str) -> LeadAssignment | None:
        """Get current active assignment for a lead."""
        query = (
            select(self.model)
            .where(
                and_(
                    self.model.lead_id == lead_id,
                    self.model.unassigned_at == None,
                )
            )
            .order_by(desc(self.model.assigned_at))
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def count_user_leads(self, user_id: str) -> int:
        """Count active leads assigned to a user."""
        query = select(func.count()).select_from(self.model).where(
            and_(
                self.model.assigned_to_user_id == user_id,
                self.model.unassigned_at == None,
            )
        )
        result = await self.session.execute(query)
        return result.scalar() or 0
