"""
Service layer for dashboard aggregation and system settings management.

DashboardService: Aggregates data from all modules for the main dashboard.
SettingsService: Manages app-level and user-level configuration.
"""

from __future__ import annotations

from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Any, List, Optional
from uuid import UUID

from sqlalchemy import select, func, and_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.core.exceptions import NotFoundException, ValidationException
from app.models.setting import AppSetting, UserSetting
from app.models.lead import Lead
from app.models.booking import Booking
from app.models.invoice import Invoice
from app.models.task import Task, Activity
from app.models.followup import FollowUp
from app.models.project import Unit
from app.utils.enums import (
    LeadStatus, BookingStatus, PaymentStatus,
    TaskStatus, FollowUpStatus
)
from app.schemas.dashboard import (
    DashboardResponse, LeadPipelineWidget, RevenueSnapshotWidget,
    BookingSnapshotWidget, TaskSummaryWidget, TeamActivityWidget,
    InventorySnapshotWidget, UpcomingItem, RecentLead, RecentBooking,
    AppSettingResponse, UserSettingResponse
)


class DashboardService:
    """Service for assembling dashboard data widgets."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_dashboard(self, user_id: UUID, user_name: str) -> DashboardResponse:
        """Assemble full dashboard for a user."""
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Gather all widgets concurrently via sequential awaits
        lead_pipeline = await self._lead_pipeline(today_start, month_start)
        revenue_snapshot = await self._revenue_snapshot(month_start)
        booking_snapshot = await self._booking_snapshot(month_start)
        task_summary = await self._task_summary(user_id, now)
        team_activity = await self._team_activity(today_start)
        inventory_snapshot = await self._inventory_snapshot()
        upcoming_items = await self._upcoming_items(user_id, now)
        recent_leads = await self._recent_leads()
        recent_bookings = await self._recent_bookings()

        return DashboardResponse(
            user_id=user_id,
            user_name=user_name,
            generated_at=now,
            period_label="This Month",
            lead_pipeline=lead_pipeline,
            revenue_snapshot=revenue_snapshot,
            booking_snapshot=booking_snapshot,
            task_summary=task_summary,
            team_activity=team_activity,
            inventory_snapshot=inventory_snapshot,
            upcoming_items=upcoming_items,
            recent_leads=recent_leads,
            recent_bookings=recent_bookings,
        )

    # ── Widget builders ───────────────────────────────────────────────

    async def _lead_pipeline(
        self, today_start: datetime, month_start: datetime
    ) -> LeadPipelineWidget:
        total = (await self.session.execute(
            select(func.count(Lead.id)).where(Lead.is_deleted == False)
        )).scalar() or 0

        new_today = (await self.session.execute(
            select(func.count(Lead.id)).where(
                and_(Lead.created_at >= today_start, Lead.is_deleted == False)
            )
        )).scalar() or 0

        async def count_status(status: str) -> int:
            return (await self.session.execute(
                select(func.count(Lead.id)).where(
                    and_(Lead.status == status, Lead.is_deleted == False)
                )
            )).scalar() or 0

        contacted = await count_status(LeadStatus.CONTACTED.value)
        qualified = await count_status(LeadStatus.QUALIFIED.value)
        converted = (await self.session.execute(
            select(func.count(Lead.id)).where(
                and_(
                    Lead.status == LeadStatus.CONVERTED.value,
                    Lead.updated_at >= month_start,
                    Lead.is_deleted == False,
                )
            )
        )).scalar() or 0
        lost = (await self.session.execute(
            select(func.count(Lead.id)).where(
                and_(
                    Lead.status == LeadStatus.LOST.value,
                    Lead.updated_at >= month_start,
                    Lead.is_deleted == False,
                )
            )
        )).scalar() or 0
        overdue_followups = (await self.session.execute(
            select(func.count(FollowUp.id)).where(
                and_(
                    FollowUp.scheduled_at < datetime.utcnow(),
                    FollowUp.status == FollowUpStatus.SCHEDULED.value,
                    FollowUp.is_deleted == False,
                )
            )
        )).scalar() or 0

        conversion_rate = (converted / total * 100) if total > 0 else 0

        return LeadPipelineWidget(
            total_leads=total,
            new_today=new_today,
            contacted=contacted,
            qualified=qualified,
            converted_this_month=converted,
            lost_this_month=lost,
            conversion_rate=round(conversion_rate, 2),
            overdue_followups=overdue_followups,
        )

    async def _revenue_snapshot(self, month_start: datetime) -> RevenueSnapshotWidget:
        invoiced = (await self.session.execute(
            select(func.coalesce(func.sum(Invoice.total_amount), 0)).where(
                and_(Invoice.created_at >= month_start, Invoice.is_deleted == False)
            )
        )).scalar() or Decimal(0)

        collected = (await self.session.execute(
            select(func.coalesce(func.sum(Invoice.paid_amount), 0)).where(
                Invoice.is_deleted == False
            )
        )).scalar() or Decimal(0)

        pending = (await self.session.execute(
            select(func.coalesce(func.sum(Invoice.total_amount - Invoice.paid_amount), 0)).where(
                and_(
                    Invoice.payment_status.in_([
                        PaymentStatus.PENDING.value, PaymentStatus.PARTIAL.value
                    ]),
                    Invoice.is_deleted == False,
                )
            )
        )).scalar() or Decimal(0)

        overdue = (await self.session.execute(
            select(func.coalesce(func.sum(Invoice.total_amount - Invoice.paid_amount), 0)).where(
                and_(
                    Invoice.due_date < datetime.utcnow(),
                    Invoice.payment_status != PaymentStatus.PAID.value,
                    Invoice.is_deleted == False,
                )
            )
        )).scalar() or Decimal(0)

        total_receivable = (await self.session.execute(
            select(func.coalesce(func.sum(Invoice.total_amount - Invoice.paid_amount), 0)).where(
                Invoice.is_deleted == False
            )
        )).scalar() or Decimal(0)

        collection_rate = (float(collected) / float(invoiced) * 100) if invoiced else 0

        return RevenueSnapshotWidget(
            invoiced_this_month=invoiced,
            collected_this_month=collected,
            pending_amount=pending,
            overdue_amount=overdue,
            collection_rate=round(collection_rate, 2),
            total_receivable=total_receivable,
        )

    async def _booking_snapshot(self, month_start: datetime) -> BookingSnapshotWidget:
        total = (await self.session.execute(
            select(func.count(Booking.id)).where(Booking.is_deleted == False)
        )).scalar() or 0

        async def count_status(status: str) -> int:
            return (await self.session.execute(
                select(func.count(Booking.id)).where(
                    and_(Booking.status == status, Booking.is_deleted == False)
                )
            )).scalar() or 0

        initiated = await count_status(BookingStatus.INITIATED.value)
        confirmed = await count_status(BookingStatus.CONFIRMED.value)
        approved = await count_status(BookingStatus.APPROVED.value)
        cancelled = (await self.session.execute(
            select(func.count(Booking.id)).where(
                and_(
                    Booking.status == BookingStatus.CANCELLED.value,
                    Booking.updated_at >= month_start,
                    Booking.is_deleted == False,
                )
            )
        )).scalar() or 0

        total_value = (await self.session.execute(
            select(func.coalesce(func.sum(Booking.booking_amount), 0)).where(
                Booking.is_deleted == False
            )
        )).scalar() or Decimal(0)

        return BookingSnapshotWidget(
            total_bookings=total,
            initiated_count=initiated,
            confirmed_count=confirmed,
            approved_count=approved,
            cancelled_this_month=cancelled,
            total_booking_value=total_value,
        )

    async def _task_summary(self, user_id: UUID, now: datetime) -> TaskSummaryWidget:
        today_end = now.replace(hour=23, minute=59, second=59)
        week_end = now + timedelta(days=7)

        pending = (await self.session.execute(
            select(func.count(Task.id)).where(
                and_(
                    Task.assigned_to_user_id == user_id,
                    Task.status == TaskStatus.PENDING.value,
                    Task.is_deleted == False,
                )
            )
        )).scalar() or 0

        in_progress = (await self.session.execute(
            select(func.count(Task.id)).where(
                and_(
                    Task.assigned_to_user_id == user_id,
                    Task.status == TaskStatus.IN_PROGRESS.value,
                    Task.is_deleted == False,
                )
            )
        )).scalar() or 0

        overdue = (await self.session.execute(
            select(func.count(Task.id)).where(
                and_(
                    Task.assigned_to_user_id == user_id,
                    Task.due_date < now,
                    Task.status.in_([TaskStatus.PENDING.value, TaskStatus.IN_PROGRESS.value]),
                    Task.is_deleted == False,
                )
            )
        )).scalar() or 0

        due_today = (await self.session.execute(
            select(func.count(Task.id)).where(
                and_(
                    Task.due_date <= today_end,
                    Task.due_date >= now,
                    Task.status.in_([TaskStatus.PENDING.value, TaskStatus.IN_PROGRESS.value]),
                    Task.is_deleted == False,
                )
            )
        )).scalar() or 0

        due_week = (await self.session.execute(
            select(func.count(Task.id)).where(
                and_(
                    Task.due_date <= week_end,
                    Task.due_date >= now,
                    Task.status.in_([TaskStatus.PENDING.value, TaskStatus.IN_PROGRESS.value]),
                    Task.is_deleted == False,
                )
            )
        )).scalar() or 0

        completed_today = (await self.session.execute(
            select(func.count(Task.id)).where(
                and_(
                    Task.assigned_to_user_id == user_id,
                    Task.completed_at >= now.replace(hour=0, minute=0),
                    Task.status == TaskStatus.COMPLETED.value,
                    Task.is_deleted == False,
                )
            )
        )).scalar() or 0

        return TaskSummaryWidget(
            my_pending=pending,
            my_in_progress=in_progress,
            my_overdue=overdue,
            due_today=due_today,
            due_this_week=due_week,
            completed_today=completed_today,
        )

    async def _team_activity(self, today_start: datetime) -> TeamActivityWidget:
        activities_today = (await self.session.execute(
            select(func.count(Activity.id)).where(Activity.created_at >= today_start)
        )).scalar() or 0

        followups_today = (await self.session.execute(
            select(func.count(FollowUp.id)).where(
                and_(
                    FollowUp.scheduled_at >= today_start,
                    FollowUp.is_deleted == False,
                )
            )
        )).scalar() or 0

        tasks_completed_today = (await self.session.execute(
            select(func.count(Task.id)).where(
                and_(
                    Task.completed_at >= today_start,
                    Task.status == TaskStatus.COMPLETED.value,
                    Task.is_deleted == False,
                )
            )
        )).scalar() or 0

        new_leads_today = (await self.session.execute(
            select(func.count(Lead.id)).where(
                and_(Lead.created_at >= today_start, Lead.is_deleted == False)
            )
        )).scalar() or 0

        bookings_today = (await self.session.execute(
            select(func.count(Booking.id)).where(
                and_(Booking.created_at >= today_start, Booking.is_deleted == False)
            )
        )).scalar() or 0

        return TeamActivityWidget(
            activities_today=activities_today,
            followups_today=followups_today,
            tasks_completed_today=tasks_completed_today,
            new_leads_today=new_leads_today,
            bookings_today=bookings_today,
        )

    async def _inventory_snapshot(self) -> InventorySnapshotWidget:
        from app.utils.enums import UnitStatus
        total = (await self.session.execute(
            select(func.count(Unit.id)).where(Unit.is_deleted == False)
        )).scalar() or 0

        async def count_unit_status(status: str) -> int:
            return (await self.session.execute(
                select(func.count(Unit.id)).where(
                    and_(Unit.status == status, Unit.is_deleted == False)
                )
            )).scalar() or 0

        available = await count_unit_status(UnitStatus.AVAILABLE.value)
        booked = await count_unit_status(UnitStatus.BOOKED.value)
        sold = await count_unit_status(UnitStatus.SOLD.value)
        availability_rate = (available / total * 100) if total > 0 else 0

        return InventorySnapshotWidget(
            total_units=total,
            available_units=available,
            booked_units=booked,
            sold_units=sold,
            availability_rate=round(availability_rate, 2),
        )

    async def _upcoming_items(
        self, user_id: UUID, now: datetime, limit: int = 10
    ) -> List[UpcomingItem]:
        horizon = now + timedelta(days=7)
        items: List[UpcomingItem] = []

        # Upcoming followups assigned to user
        followup_q = (
            select(FollowUp)
            .where(
                and_(
                    FollowUp.assigned_to_user_id == user_id,
                    FollowUp.scheduled_at <= horizon,
                    FollowUp.status == FollowUpStatus.SCHEDULED.value,
                    FollowUp.is_deleted == False,
                )
            )
            .order_by(asc(FollowUp.scheduled_at))
            .limit(limit)
        )
        followups = (await self.session.execute(followup_q)).scalars().all()
        for f in followups:
            items.append(UpcomingItem(
                id=f.id,
                type="followup",
                title=f.subject,
                entity_type="lead" if f.lead_id else "customer",
                entity_name=None,
                scheduled_at=f.scheduled_at,
                due_date=None,
                priority=f.priority,
                is_overdue=f.scheduled_at < now,
            ))

        # Upcoming tasks assigned to user
        task_q = (
            select(Task)
            .where(
                and_(
                    Task.assigned_to_user_id == user_id,
                    Task.due_date <= horizon,
                    Task.status.in_([TaskStatus.PENDING.value, TaskStatus.IN_PROGRESS.value]),
                    Task.is_deleted == False,
                )
            )
            .order_by(asc(Task.due_date))
            .limit(limit)
        )
        tasks = (await self.session.execute(task_q)).scalars().all()
        for t in tasks:
            items.append(UpcomingItem(
                id=t.id,
                type="task",
                title=t.title,
                entity_type=t.task_type,
                entity_name=None,
                scheduled_at=None,
                due_date=t.due_date,
                priority={"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}.get(t.priority.value, 0),
                is_overdue=bool(t.due_date and t.due_date < now),
            ))

        # Sort combined list by soonest date
        items.sort(key=lambda x: (x.scheduled_at or x.due_date or datetime.max))
        return items[:limit]

    async def _recent_leads(self, limit: int = 5) -> List[RecentLead]:
        q = (
            select(Lead)
            .where(Lead.is_deleted == False)
            .order_by(desc(Lead.created_at))
            .limit(limit)
        )
        leads = (await self.session.execute(q)).scalars().all()
        return [
            RecentLead(
                id=l.id,
                lead_number=l.lead_number,
                full_name=l.full_name,
                status=l.status,
                source=l.source,
                created_at=l.created_at,
                assigned_to_name=None,
            )
            for l in leads
        ]

    async def _recent_bookings(self, limit: int = 5) -> List[RecentBooking]:
        q = (
            select(Booking)
            .where(Booking.is_deleted == False)
            .order_by(desc(Booking.created_at))
            .limit(limit)
        )
        bookings = (await self.session.execute(q)).scalars().all()
        return [
            RecentBooking(
                id=b.id,
                booking_number=b.booking_number,
                customer_name="",  # Would need join to customer
                project_name="",   # Would need join to project
                booking_amount=b.booking_amount or Decimal(0),
                status=b.status,
                created_at=b.created_at,
            )
            for b in bookings
        ]


class SettingsService:
    """Service for managing application and user settings."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ── App Settings ──────────────────────────────────────────────────

    async def list_app_settings(
        self, category: Optional[str] = None, include_sensitive: bool = False
    ) -> List[AppSetting]:
        """List all app settings."""
        filters = []
        if category:
            filters.append(AppSetting.category == category)

        q = select(AppSetting)
        if filters:
            q = q.where(and_(*filters))
        q = q.order_by(asc(AppSetting.category), asc(AppSetting.key))

        result = await self.session.execute(q)
        settings = result.scalars().all()
        if not include_sensitive:
            for s in settings:
                if s.is_sensitive:
                    s.value_string = "***"
        return settings

    async def get_setting(self, key: str) -> AppSetting:
        """Get a setting by key."""
        result = await self.session.execute(
            select(AppSetting).where(AppSetting.key == key)
        )
        setting = result.scalars().first()
        if not setting:
            raise NotFoundException(f"Setting '{key}' not found")
        return setting

    async def update_setting(
        self, key: str, value: Any, updated_by: UUID
    ) -> AppSetting:
        """Update a setting value."""
        setting = await self.get_setting(key)

        if setting.is_readonly:
            raise ValidationException(f"Setting '{key}' is read-only")

        # Store in the correct column based on data_type
        if setting.data_type == "string":
            setting.value_string = str(value)
        elif setting.data_type == "int":
            setting.value_int = int(value)
        elif setting.data_type == "bool":
            setting.value_bool = bool(value)
        elif setting.data_type == "json":
            setting.value_json = value

        setting.updated_by_user_id = updated_by
        logger.info(f"App setting updated | key={key} | by={updated_by}")
        return setting

    async def create_setting(
        self,
        key: str,
        label: str,
        category: str,
        data_type: str,
        value: Any,
        description: Optional[str],
        is_sensitive: bool,
        is_readonly: bool,
    ) -> AppSetting:
        """Create a new app setting."""
        existing = await self.session.execute(
            select(AppSetting).where(AppSetting.key == key)
        )
        if existing.scalars().first():
            raise ValidationException(f"Setting '{key}' already exists")

        setting = AppSetting(
            key=key,
            label=label,
            category=category,
            data_type=data_type,
            description=description,
            is_sensitive=is_sensitive,
            is_readonly=is_readonly,
        )
        # Set value
        if data_type == "string":
            setting.value_string = str(value) if value is not None else None
        elif data_type == "int":
            setting.value_int = int(value) if value is not None else None
        elif data_type == "bool":
            setting.value_bool = bool(value) if value is not None else None
        elif data_type == "json":
            setting.value_json = value

        self.session.add(setting)
        await self.session.flush()
        return setting

    # ── User Settings ─────────────────────────────────────────────────

    async def get_user_settings(self, user_id: UUID) -> List[UserSetting]:
        """Get all settings for a user."""
        result = await self.session.execute(
            select(UserSetting).where(UserSetting.user_id == user_id).order_by(asc(UserSetting.key))
        )
        return result.scalars().all()

    async def upsert_user_setting(self, user_id: UUID, key: str, value: Any) -> UserSetting:
        """Create or update a user setting."""
        result = await self.session.execute(
            select(UserSetting).where(
                and_(UserSetting.user_id == user_id, UserSetting.key == key)
            )
        )
        setting = result.scalars().first()
        if setting:
            setting.value = value
        else:
            setting = UserSetting(user_id=user_id, key=key, value=value)
            self.session.add(setting)
            await self.session.flush()
        return setting


def and_(*clauses):
    from sqlalchemy import and_ as _and_
    return _and_(*clauses)
