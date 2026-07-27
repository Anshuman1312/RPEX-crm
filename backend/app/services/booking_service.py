"""
Booking service layer with business logic.

Key features:
- Booking state machine (PENDING → BLOCKED → CONFIRMED → POSSESSION_INITIATED → COMPLETED)
- Multi-level approval workflow (Sales Manager → Finance Manager → CEO)
- Payment plan management with milestone tracking
- Booking cancellation with refund tracking
- Possession handover workflow
"""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    NotFoundException,
    ValidationException,
    ConflictException,
    InvalidStateTransitionException,
)
from app.models.booking import (
    Booking,
    BookingPaymentPlan,
    BookingApproval,
    BookingCancellation,
    Possession,
)
from app.models.project import Unit, UnitAvailabilityLog
from app.models.customer import Customer
from app.models.user import User
from app.repositories.booking_repository import (
    BookingRepository,
    BookingPaymentPlanRepository,
    BookingApprovalRepository,
    BookingCancellationRepository,
    PossessionRepository,
)
from app.repositories.project_repository import UnitRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.user_repository import UserRepository
from app.utils.enums import BookingStatus, BookingApprovalStatus, PaymentStatus, UnitStatus
from app.utils.numbering import NumberingService


class BookingService:
    """Booking management service."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.booking_repo = BookingRepository(session)
        self.payment_plan_repo = BookingPaymentPlanRepository(session)
        self.approval_repo = BookingApprovalRepository(session)
        self.cancellation_repo = BookingCancellationRepository(session)
        self.possession_repo = PossessionRepository(session)
        self.unit_repo = UnitRepository(session)
        self.customer_repo = CustomerRepository(session)
        self.user_repo = UserRepository(session)
        self.numbering_service = NumberingService(session)

    # ── Booking CRUD ──────────────────────────────────────────────────

    async def create_booking(
        self,
        unit_id: str,
        customer_id: str,
        booking_amount: Decimal,
        booking_expiry_date: Optional[datetime] = None,
        booking_notes: Optional[str] = None,
        assignment_to_user_id: Optional[str] = None,
        related_lead_id: Optional[str] = None,
        created_by: str = "system",
    ) -> Booking:
        """Create new booking."""
        # Validate unit exists and available
        unit = await self.unit_repo.get_by_id(unit_id)
        if not unit:
            raise NotFoundException(f"Unit {unit_id} not found")
        if unit.status != UnitStatus.AVAILABLE.value:
            raise ValidationException(f"Unit {unit_id} is not available for booking")

        # Check no active booking for unit
        existing_booking = await self.booking_repo.get_by_unit_id(unit_id)
        if existing_booking:
            raise ConflictException(f"Unit {unit_id} already has active booking")

        # Validate customer exists
        customer = await self.customer_repo.get_by_id(customer_id)
        if not customer:
            raise NotFoundException(f"Customer {customer_id} not found")

        # Generate booking number
        booking_number = await self.numbering_service.get_next_number("BOOK")

        # Create booking
        booking = Booking(
            booking_number=booking_number,
            unit_id=unit_id,
            customer_id=customer_id,
            booking_amount=booking_amount,
            total_unit_price=unit.price,
            status=BookingStatus.INITIATED.value,
            booking_expiry_date=booking_expiry_date or (datetime.utcnow() + timedelta(days=7)),
            booking_notes=booking_notes,
            assignment_to_user_id=assignment_to_user_id,
            approval_status=BookingApprovalStatus.PENDING.value,
            related_lead_id=related_lead_id,
            created_by=created_by,
        )
        self.session.add(booking)
        await self.session.flush()

        # Update unit status to BLOCKED
        unit.status = UnitStatus.BLOCKED.value
        unit.updated_at = datetime.utcnow()

        # Create approval workflow (3 levels)
        approval_levels = [
            (1, "Sales Manager"),
            (2, "Finance Manager"),
            (3, "CEO"),
        ]
        for level, role_name in approval_levels:
            approval = BookingApproval(
                booking_id=booking.id,
                approval_level=level,
                approver_user_id="",  # Will be assigned
                status=BookingApprovalStatus.PENDING.value,
                approval_order=level,
                created_by=created_by,
            )
            self.session.add(approval)

        await self.session.flush()
        return booking

    async def get_booking(self, booking_id: str) -> Booking:
        """Get booking with relations."""
        booking = await self.booking_repo.get_with_relations(booking_id)
        if not booking:
            raise NotFoundException(f"Booking {booking_id} not found")
        return booking

    async def list_bookings(
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
    ) -> tuple[List[Booking], int]:
        """List bookings with filtering."""
        return await self.booking_repo.list_with_filter(
            statuses=statuses,
            approval_statuses=approval_statuses,
            customer_id=customer_id,
            assigned_to_user_id=assigned_to_user_id,
            search=search,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_direction=sort_direction,
        )

    async def update_booking(self, booking_id: str, **kwargs) -> Booking:
        """Update booking details."""
        booking = await self.get_booking(booking_id)

        allowed_fields = ["booking_expiry_date", "booking_notes", "assignment_to_user_id"]
        for field in allowed_fields:
            if field in kwargs and kwargs[field] is not None:
                setattr(booking, field, kwargs[field])

        booking.updated_at = datetime.utcnow()
        return booking

    async def delete_booking(self, booking_id: str) -> None:
        """Soft delete booking."""
        booking = await self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise NotFoundException(f"Booking {booking_id} not found")
        await self.booking_repo.soft_delete(booking_id)

    # ── Booking Status ────────────────────────────────────────────────

    async def change_booking_status(
        self,
        booking_id: str,
        new_status: str,
        notes: Optional[str] = None,
    ) -> Booking:
        """Change booking status with validation."""
        booking = await self.get_booking(booking_id)

        # Valid state transitions
        valid_transitions = {
            BookingStatus.INITIATED.value: [BookingStatus.CONFIRMED.value],
            BookingStatus.CONFIRMED.value: [BookingStatus.APPROVED.value],
            BookingStatus.APPROVED.value: [BookingStatus.AGREEMENT_SIGNED.value],
            BookingStatus.AGREEMENT_SIGNED.value: [BookingStatus.POSSESSION.value],
            BookingStatus.POSSESSION.value: [],
            BookingStatus.CANCELLED.value: [],
            BookingStatus.DEFAULTED.value: [],
        }

        if new_status not in valid_transitions.get(booking.status, []):
            raise InvalidStateTransitionException(
                f"Cannot transition from {booking.status} to {new_status}"
            )

        booking.status = new_status
        booking.updated_at = datetime.utcnow()

        if new_status == BookingStatus.CONFIRMED.value:
            booking.confirmed_at = datetime.utcnow()
            # Update unit status to SOLD
            unit = await self.unit_repo.get_by_id(booking.unit_id)
            if unit:
                unit.status = UnitStatus.SOLD.value
                unit.updated_at = datetime.utcnow()

        return booking

    # ── Approval Workflow ─────────────────────────────────────────────

    async def approve_booking(
        self,
        booking_id: str,
        approver_user_id: str,
        approval_level: int,
        notes: Optional[str] = None,
    ) -> BookingApproval:
        """Approve booking at level."""
        booking = await self.get_booking(booking_id)

        approval = await self.approval_repo.get_pending_approval_for_level(booking_id, approval_level)
        if not approval:
            raise NotFoundException(
                f"No pending approval at level {approval_level} for booking {booking_id}"
            )

        approval.approver_user_id = approver_user_id
        approval.status = BookingApprovalStatus.APPROVED.value
        approval.notes = notes
        approval.approval_date = datetime.utcnow()
        approval.updated_at = datetime.utcnow()

        # Check if all approvals complete
        all_approved = await self.approval_repo.are_all_approvals_complete(booking_id)
        if all_approved:
            booking.approval_status = BookingApprovalStatus.APPROVED.value
            booking.approval_completed_at = datetime.utcnow()
            booking.updated_at = datetime.utcnow()

        return approval

    async def reject_booking(
        self,
        booking_id: str,
        approver_user_id: str,
        approval_level: int,
        notes: str,
    ) -> BookingApproval:
        """Reject booking at level."""
        booking = await self.get_booking(booking_id)

        approval = await self.approval_repo.get_pending_approval_for_level(booking_id, approval_level)
        if not approval:
            raise NotFoundException(
                f"No pending approval at level {approval_level} for booking {booking_id}"
            )

        approval.approver_user_id = approver_user_id
        approval.status = BookingApprovalStatus.REJECTED.value
        approval.notes = notes
        approval.approval_date = datetime.utcnow()
        approval.updated_at = datetime.utcnow()

        booking.approval_status = BookingApprovalStatus.REJECTED.value
        booking.status = BookingStatus.INITIATED.value

        return approval

    async def get_pending_approvals(self, user_id: str) -> List[Booking]:
        """Get bookings awaiting approval by user."""
        return await self.booking_repo.get_pending_approvals(user_id)

    # ── Payment Plans ─────────────────────────────────────────────────

    async def add_payment_plan(
        self,
        booking_id: str,
        milestone_name: str,
        percentage: int,
        due_date: datetime,
        amount: Decimal,
        payment_method: Optional[str] = None,
        grace_period_days: int = 0,
        notes: Optional[str] = None,
        created_by: str = "system",
    ) -> BookingPaymentPlan:
        """Add payment plan milestone."""
        booking = await self.get_booking(booking_id)

        # Validate percentage
        if not (0 <= percentage <= 100):
            raise ValidationException("Percentage must be between 0 and 100")

        plan = BookingPaymentPlan(
            booking_id=booking_id,
            milestone_name=milestone_name,
            percentage=percentage,
            due_date=due_date,
            amount=amount,
            payment_status=PaymentStatus.PENDING.value,
            payment_method=payment_method,
            grace_period_days=grace_period_days,
            notes=notes,
            created_by=created_by,
        )
        self.session.add(plan)
        await self.session.flush()
        return plan

    async def get_payment_plans(self, booking_id: str) -> List[BookingPaymentPlan]:
        """Get payment plans for booking."""
        return await self.payment_plan_repo.get_booking_payment_plans(booking_id)

    async def mark_payment_received(
        self,
        payment_plan_id: str,
        transaction_ref: str,
        payment_method: str,
        notes: Optional[str] = None,
    ) -> BookingPaymentPlan:
        """Mark payment as received."""
        plan = await self.payment_plan_repo.get_by_id(payment_plan_id)
        if not plan:
            raise NotFoundException(f"Payment plan {payment_plan_id} not found")

        plan.payment_status = PaymentStatus.PAID.value
        plan.payment_date = datetime.utcnow()
        plan.transaction_ref = transaction_ref
        plan.payment_method = payment_method
        plan.notes = notes
        plan.updated_at = datetime.utcnow()

        return plan

    async def get_booking_payment_summary(self, booking_id: str) -> Dict[str, Any]:
        """Get payment summary for booking."""
        booking = await self.get_booking(booking_id)
        total_paid = await self.payment_plan_repo.get_total_paid_amount(booking_id)
        total_pending = await self.payment_plan_repo.get_total_pending_amount(booking_id)

        return {
            "booking_id": booking_id,
            "total_unit_price": float(booking.total_unit_price),
            "booking_amount": float(booking.booking_amount),
            "total_paid": total_paid,
            "total_pending": total_pending,
            "percentage_paid": (total_paid / float(booking.total_unit_price) * 100) if booking.total_unit_price else 0,
        }

    # ── Booking Cancellation ──────────────────────────────────────────

    async def cancel_booking(
        self,
        booking_id: str,
        reason: str,
        cancelled_by_user_id: str,
        notes: Optional[str] = None,
    ) -> BookingCancellation:
        """Cancel booking."""
        booking = await self.get_booking(booking_id)

        if booking.status in [BookingStatus.POSSESSION.value]:
            raise ValidationException(f"Cannot cancel booking in {booking.status} status")

        # Create cancellation record
        cancellation = BookingCancellation(
            booking_id=booking_id,
            reason=reason,
            cancelled_by_user_id=cancelled_by_user_id,
            refund_amount=booking.booking_amount,
            refund_status=PaymentStatus.PENDING.value,
            notes=notes,
            created_by=cancelled_by_user_id,
        )
        self.session.add(cancellation)

        # Update booking
        booking.status = BookingStatus.CANCELLED.value
        booking.cancellation_initiated_at = datetime.utcnow()
        booking.cancellation_reason = reason
        booking.updated_at = datetime.utcnow()

        # Release unit back to available
        unit = await self.unit_repo.get_by_id(booking.unit_id)
        if unit:
            unit.status = UnitStatus.AVAILABLE.value
            unit.updated_at = datetime.utcnow()

        await self.session.flush()
        return cancellation

    async def process_refund(
        self,
        cancellation_id: str,
        transaction_ref: str,
    ) -> BookingCancellation:
        """Process refund for cancellation."""
        cancellation = await self.cancellation_repo.get_by_id(cancellation_id)
        if not cancellation:
            raise NotFoundException(f"Cancellation {cancellation_id} not found")

        cancellation.refund_status = PaymentStatus.PAID.value
        cancellation.refund_date = datetime.utcnow()
        cancellation.refund_transaction_ref = transaction_ref
        cancellation.updated_at = datetime.utcnow()

        return cancellation

    # ── Possession ────────────────────────────────────────────────────

    async def create_possession(
        self,
        booking_id: str,
        possession_date: datetime,
        possession_notes: Optional[str] = None,
        created_by: str = "system",
    ) -> Possession:
        """Create possession record."""
        booking = await self.get_booking(booking_id)

        if booking.status != BookingStatus.AGREEMENT_SIGNED.value:
            raise ValidationException("Can only create possession for bookings with signed agreements")

        possession = Possession(
            booking_id=booking_id,
            possession_date=possession_date,
            possession_notes=possession_notes,
            possession_status="SCHEDULED",
            created_by=created_by,
        )
        self.session.add(possession)
        await self.session.flush()
        return possession

    async def handover_possession(
        self,
        possession_id: str,
        keys_handed_by_user_id: str,
        keys_handed_to_customer: bool = True,
        documents_handed: bool = True,
        final_inspection_done: bool = False,
        inspection_notes: Optional[str] = None,
    ) -> Possession:
        """Handover possession to customer."""
        possession = await self.possession_repo.get_by_id(possession_id)
        if not possession:
            raise NotFoundException(f"Possession {possession_id} not found")

        possession.possession_handed_date = datetime.utcnow()
        possession.keys_handed_by_user_id = keys_handed_by_user_id
        possession.keys_handed_to_customer = keys_handed_to_customer
        possession.documents_handed = documents_handed
        possession.final_inspection_done = final_inspection_done
        possession.inspection_notes = inspection_notes
        possession.possession_status = "HANDED_OVER"
        possession.updated_at = datetime.utcnow()

        # Update booking status
        booking = await self.get_booking(possession.booking_id)
        await self.change_booking_status(booking.id, BookingStatus.POSSESSION.value)

        return possession

    # ── Statistics ────────────────────────────────────────────────────

    async def get_booking_statistics(self) -> Dict[str, Any]:
        """Get booking statistics."""
        status_counts = await self.booking_repo.count_by_status()
        total_bookings = sum(status_counts.values())

        return {
            "total_bookings": total_bookings,
            "by_status": status_counts,
            "pending_approvals_count": len(await self.approval_repo.get_user_pending_approvals("all")),
        }
