"""
Repository layer for booking data access.

Classes:
- BookingRepository: Booking CRUD + advanced filtering
- BookingPaymentPlanRepository: Payment plan management
- BookingApprovalRepository: Approval workflow tracking
- BookingCancellationRepository: Cancellation records
- PossessionRepository: Possession tracking
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, List, Tuple

from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.booking import (
    Booking,
    BookingPaymentPlan,
    BookingApproval,
    BookingCancellation,
    Possession,
)
from app.models.customer import Customer
from app.models.project import Unit
from app.repositories.base import BaseRepository
from app.utils.enums import BookingStatus, BookingApprovalStatus, PaymentStatus


class BookingRepository(BaseRepository[Booking]):
    """Booking data access."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Booking)

    async def get_by_booking_number(self, booking_number: str) -> Optional[Booking]:
        """Get booking by booking number."""
        stmt = select(self.model).where(
            and_(
                self.model.booking_number == booking_number,
                self.model.is_deleted == False,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_with_relations(self, booking_id: str) -> Optional[Booking]:
        """Get booking with all relations (payment plans, approvals, etc)."""
        stmt = (
            select(self.model)
            .options(
                selectinload(self.model.payment_plans),
                selectinload(self.model.approvals),
                selectinload(self.model.cancellation),
                selectinload(self.model.possession),
            )
            .where(
                and_(
                    self.model.id == booking_id,
                    self.model.is_deleted == False,
                )
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_unit_id(self, unit_id: str) -> Optional[Booking]:
        """Get active booking for a unit."""
        stmt = select(self.model).where(
            and_(
                self.model.unit_id == unit_id,
                self.model.status != BookingStatus.CANCELLED.value,
                self.model.is_deleted == False,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_customer_bookings(self, customer_id: str) -> List[Booking]:
        """Get all bookings for customer."""
        stmt = (
            select(self.model)
            .where(
                and_(
                    self.model.customer_id == customer_id,
                    self.model.is_deleted == False,
                )
            )
            .order_by(desc(self.model.created_at))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_with_filter(
        self,
        statuses: Optional[List[str]] = None,
        approval_statuses: Optional[List[str]] = None,
        customer_id: Optional[str] = None,
        assigned_to_user_id: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
        sort_by: str = "created_at",
        sort_direction: str = "desc",
    ) -> Tuple[List[Booking], int]:
        """Filter bookings with advanced options."""
        filters = [self.model.is_deleted == False]

        if statuses:
            filters.append(self.model.status.in_(statuses))
        if approval_statuses:
            filters.append(self.model.approval_status.in_(approval_statuses))
        if customer_id:
            filters.append(self.model.customer_id == customer_id)
        if assigned_to_user_id:
            filters.append(self.model.assignment_to_user_id == assigned_to_user_id)
        if search:
            filters.append(
                or_(
                    self.model.booking_number.ilike(f"%{search}%"),
                )
            )

        # Count query
        count_stmt = select(func.count()).select_from(self.model).where(and_(*filters))
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar() or 0

        # List query
        sort_column = getattr(self.model, sort_by, self.model.created_at)
        if sort_direction == "desc":
            sort_column = desc(sort_column)

        stmt = (
            select(self.model)
            .where(and_(*filters))
            .order_by(sort_column)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        bookings = result.scalars().all()

        return bookings, total

    async def get_pending_approvals(self, user_id: str) -> List[Booking]:
        """Get bookings awaiting approval by user."""
        stmt = (
            select(self.model)
            .join(BookingApproval)
            .where(
                and_(
                    BookingApproval.approver_user_id == user_id,
                    BookingApproval.status == BookingApprovalStatus.PENDING.value,
                    self.model.is_deleted == False,
                )
            )
            .order_by(desc(self.model.created_at))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_by_status(self) -> dict:
        """Get booking count by status."""
        stmt = (
            select(self.model.status, func.count(self.model.id))
            .where(self.model.is_deleted == False)
            .group_by(self.model.status)
        )
        result = await self.session.execute(stmt)
        rows = result.all()
        return {status: count for status, count in rows}

    async def get_expiring_bookings(self, days: int = 7) -> List[Booking]:
        """Get bookings expiring in next N days."""
        stmt = (
            select(self.model)
            .where(
                and_(
                    self.model.booking_expiry_date.isnot(None),
                    self.model.booking_expiry_date <= func.now() + func.make_interval(days=days),
                    self.model.status == BookingStatus.INITIATED.value,
                    self.model.is_deleted == False,
                )
            )
            .order_by(self.model.booking_expiry_date)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


class BookingPaymentPlanRepository(BaseRepository[BookingPaymentPlan]):
    """Booking payment plan data access."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, BookingPaymentPlan)

    async def get_booking_payment_plans(self, booking_id: str) -> List[BookingPaymentPlan]:
        """Get all payment plans for booking."""
        stmt = (
            select(self.model)
            .where(self.model.booking_id == booking_id)
            .order_by(self.model.due_date)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_pending_payments(self, booking_id: str) -> List[BookingPaymentPlan]:
        """Get pending/overdue payments for booking."""
        stmt = (
            select(self.model)
            .where(
                and_(
                    self.model.booking_id == booking_id,
                    self.model.payment_status.in_(
                        [PaymentStatus.PENDING.value, PaymentStatus.OVERDUE.value]
                    ),
                )
            )
            .order_by(self.model.due_date)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_total_paid_amount(self, booking_id: str) -> float:
        """Get total paid amount for booking."""
        stmt = select(func.sum(self.model.amount)).where(
            and_(
                self.model.booking_id == booking_id,
                self.model.payment_status == PaymentStatus.PAID.value,
            )
        )
        result = await self.session.execute(stmt)
        return float(result.scalar() or 0)

    async def get_total_pending_amount(self, booking_id: str) -> float:
        """Get total pending amount for booking."""
        stmt = select(func.sum(self.model.amount)).where(
            and_(
                self.model.booking_id == booking_id,
                self.model.payment_status.in_(
                    [PaymentStatus.PENDING.value, PaymentStatus.OVERDUE.value]
                ),
            )
        )
        result = await self.session.execute(stmt)
        return float(result.scalar() or 0)


class BookingApprovalRepository(BaseRepository[BookingApproval]):
    """Booking approval data access."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, BookingApproval)

    async def get_booking_approvals(self, booking_id: str) -> List[BookingApproval]:
        """Get all approvals for booking."""
        stmt = (
            select(self.model)
            .where(self.model.booking_id == booking_id)
            .order_by(self.model.approval_level)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_pending_approval_for_level(
        self, booking_id: str, approval_level: int
    ) -> Optional[BookingApproval]:
        """Get pending approval for specific level."""
        stmt = select(self.model).where(
            and_(
                self.model.booking_id == booking_id,
                self.model.approval_level == approval_level,
                self.model.status == BookingApprovalStatus.PENDING.value,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_pending_approvals(self, user_id: str) -> List[BookingApproval]:
        """Get all pending approvals for user."""
        stmt = (
            select(self.model)
            .where(
                and_(
                    self.model.approver_user_id == user_id,
                    self.model.status == BookingApprovalStatus.PENDING.value,
                )
            )
            .order_by(desc(self.model.created_at))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def are_all_approvals_complete(self, booking_id: str) -> bool:
        """Check if all approval levels completed."""
        stmt = (
            select(func.count())
            .select_from(self.model)
            .where(
                and_(
                    self.model.booking_id == booking_id,
                    self.model.status != BookingApprovalStatus.APPROVED.value,
                )
            )
        )
        result = await self.session.execute(stmt)
        count = result.scalar() or 0
        return count == 0


class BookingCancellationRepository(BaseRepository[BookingCancellation]):
    """Booking cancellation data access."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, BookingCancellation)

    async def get_by_booking_id(self, booking_id: str) -> Optional[BookingCancellation]:
        """Get cancellation record for booking."""
        stmt = select(self.model).where(self.model.booking_id == booking_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_pending_refunds(self) -> List[BookingCancellation]:
        """Get cancellations with pending refunds."""
        stmt = (
            select(self.model)
            .where(self.model.refund_status == PaymentStatus.PENDING.value)
            .order_by(self.model.cancellation_date)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


class PossessionRepository(BaseRepository[Possession]):
    """Possession data access."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Possession)

    async def get_by_booking_id(self, booking_id: str) -> Optional[Possession]:
        """Get possession record for booking."""
        stmt = select(self.model).where(self.model.booking_id == booking_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_pending_possessions(self) -> List[Possession]:
        """Get possessions scheduled but not handed over."""
        stmt = (
            select(self.model)
            .where(self.model.possession_status == "SCHEDULED")
            .order_by(self.model.possession_date)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_handed_over_possessions(self) -> List[Possession]:
        """Get handed over possessions."""
        stmt = (
            select(self.model)
            .where(self.model.possession_status == "HANDED_OVER")
            .order_by(desc(self.model.possession_handed_date))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
