"""
FastAPI routes for booking management.

Endpoints:
- Booking CRUD: POST/GET/PATCH/DELETE
- Status management: POST /status
- Approval workflow: GET /approvals, POST /approvals/{id}/approve|reject
- Payment plans: POST/GET payment-plans, POST /payment-plans/{id}/mark-paid
- Cancellation: POST /cancel, PATCH /cancellations/{id}/refund
- Possession: POST/GET /possession, POST /possession/handover
- Statistics: GET /stats/overview
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db_session
from app.dependencies.auth import get_current_user, require_permission
from app.models.user import User
from app.schemas.booking import (
    BookingCreate,
    BookingUpdate,
    BookingResponse,
    BookingListResponse,
    BookingStatusUpdate,
    BookingConfirmRequest,
    BookingCancellationRequest,
    BookingPaymentPlanCreate,
    BookingPaymentPlanResponse,
    PaymentMarkAsPaidRequest,
    BookingApprovalResponse,
    BookingApprovalActionRequest,
    PossessionCreate,
    PossessionResponse,
    PossessionHandoverRequest,
    BookingCancellationResponse,
)
from app.services.booking_service import BookingService
from app.utils.pagination import PaginationParams, get_pagination_params
from app.utils.response import ok, created, PaginatedResponse
from loguru import logger

router = APIRouter()


# ── Booking CRUD ──────────────────────────────────────────────────────

@router.post("", status_code=status.HTTP_201_CREATED, response_model=dict)
async def create_booking(
    request: BookingCreate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("bookings.create")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Create new booking. Requires bookings.create permission."""
    service = BookingService(session)

    booking = await service.create_booking(
        unit_id=request.unit_id,
        customer_id=request.customer_id,
        booking_amount=request.booking_amount,
        booking_expiry_date=request.booking_expiry_date,
        booking_notes=request.booking_notes,
        assignment_to_user_id=request.assignment_to_user_id,
        related_lead_id=request.related_lead_id,
        created_by=str(current_user.id),
    )

    await session.commit()

    logger.info(f"Booking created | id={booking.id} | number={booking.booking_number} | unit={request.unit_id}")

    return created(
        data=BookingResponse.model_validate(booking).__dict__,
        message="Booking created successfully.",
    )


@router.get("", status_code=status.HTTP_200_OK, response_model=PaginatedResponse)
async def list_bookings(
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("bookings.view")),
    pagination: PaginationParams = Depends(get_pagination_params),
    statuses: str = Query(None, description="Comma-separated statuses"),
    approval_statuses: str = Query(None, description="Comma-separated approval statuses"),
    customer_id: str = Query(None),
    assigned_to_user_id: str = Query(None),
    search: str = Query(None),
    sort_by: str = Query("created_at"),
    sort_direction: str = Query("desc"),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """List bookings with filtering and pagination."""
    service = BookingService(session)

    bookings, total = await service.list_bookings(
        statuses=statuses.split(",") if statuses else None,
        approval_statuses=approval_statuses.split(",") if approval_statuses else None,
        customer_id=customer_id,
        assigned_to_user_id=assigned_to_user_id,
        search=search,
        skip=pagination.offset,
        limit=pagination.limit,
        sort_by=sort_by,
        sort_direction=sort_direction,
    )

    data = [BookingListResponse.model_validate(b).__dict__ for b in bookings]

    return PaginatedResponse.build(
        data=data,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    ).__dict__


@router.get("/{booking_id}", status_code=status.HTTP_200_OK, response_model=dict)
async def get_booking(
    booking_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("bookings.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get booking with all details."""
    service = BookingService(session)
    booking = await service.get_booking(booking_id)

    return ok(data=BookingResponse.model_validate(booking).__dict__)


@router.patch("/{booking_id}", status_code=status.HTTP_200_OK, response_model=dict)
async def update_booking(
    booking_id: str,
    request: BookingUpdate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("bookings.edit")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Update booking details."""
    service = BookingService(session)

    booking = await service.update_booking(booking_id, **request.model_dump(exclude_unset=True))

    await session.commit()

    logger.info(f"Booking updated | id={booking_id} | updated_by={current_user.id}")

    return ok(data=BookingResponse.model_validate(booking).__dict__)


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_booking(
    booking_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("bookings.delete")),
    session: AsyncSession = Depends(get_db_session),
): # Removed "-> None"
    """Soft delete a booking."""
    service = BookingService(session)
    await service.delete_booking(booking_id)

    await session.commit()

    logger.info(f"Booking deleted | id={booking_id} | deleted_by={current_user.id}")
    
    # ADD THIS LINE:
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ── Booking Status ────────────────────────────────────────────────────

@router.post("/{booking_id}/status", status_code=status.HTTP_200_OK, response_model=dict)
async def change_booking_status(
    booking_id: str,
    request: BookingStatusUpdate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("bookings.edit")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Change booking status."""
    service = BookingService(session)

    booking = await service.change_booking_status(booking_id, request.status, request.notes)

    await session.commit()

    logger.info(f"Booking status changed | id={booking_id} | status={request.status}")

    return ok(data=BookingResponse.model_validate(booking).__dict__)


# ── Approval Workflow ─────────────────────────────────────────────────

@router.get("/{booking_id}/approvals", status_code=status.HTTP_200_OK, response_model=dict)
async def get_booking_approvals(
    booking_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("bookings.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get approval workflow for booking."""
    service = BookingService(session)
    booking = await service.get_booking(booking_id)

    data = [BookingApprovalResponse.model_validate(a).__dict__ for a in booking.approvals]

    return ok(data=data)


@router.get("/approvals/pending", status_code=status.HTTP_200_OK, response_model=dict)
async def get_my_pending_approvals(
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("bookings.approve")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get my pending approvals."""
    service = BookingService(session)
    bookings = await service.get_pending_approvals(str(current_user.id))

    data = [BookingListResponse.model_validate(b).__dict__ for b in bookings]

    return ok(data=data)


@router.post("/{booking_id}/approvals/{approval_level}/approve", status_code=status.HTTP_200_OK, response_model=dict)
async def approve_booking(
    booking_id: str,
    approval_level: int,
    request: BookingApprovalActionRequest,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("bookings.approve")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Approve booking at level."""
    service = BookingService(session)

    approval = await service.approve_booking(
        booking_id=booking_id,
        approver_user_id=str(current_user.id),
        approval_level=approval_level,
        notes=request.notes,
    )

    await session.commit()

    logger.info(f"Booking approved | id={booking_id} | level={approval_level} | by={current_user.id}")

    return ok(
        data=BookingApprovalResponse.model_validate(approval).__dict__,
        message="Booking approved successfully.",
    )


@router.post("/{booking_id}/approvals/{approval_level}/reject", status_code=status.HTTP_200_OK, response_model=dict)
async def reject_booking(
    booking_id: str,
    approval_level: int,
    request: BookingApprovalActionRequest,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("bookings.approve")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Reject booking at level."""
    service = BookingService(session)

    approval = await service.reject_booking(
        booking_id=booking_id,
        approver_user_id=str(current_user.id),
        approval_level=approval_level,
        notes=request.notes or "No reason provided",
    )

    await session.commit()

    logger.info(f"Booking rejected | id={booking_id} | level={approval_level} | by={current_user.id}")

    return ok(
        data=BookingApprovalResponse.model_validate(approval).__dict__,
        message="Booking rejected successfully.",
    )


# ── Payment Plans ─────────────────────────────────────────────────────

@router.post("/{booking_id}/payment-plans", status_code=status.HTTP_201_CREATED, response_model=dict)
async def add_payment_plan(
    booking_id: str,
    request: BookingPaymentPlanCreate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("bookings.edit")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Add payment plan milestone."""
    service = BookingService(session)

    plan = await service.add_payment_plan(
        booking_id=booking_id,
        milestone_name=request.milestone_name,
        percentage=request.percentage,
        due_date=request.due_date,
        amount=request.amount,
        payment_method=request.payment_method,
        grace_period_days=request.grace_period_days,
        notes=request.notes,
        created_by=str(current_user.id),
    )

    await session.commit()

    return created(
        data=BookingPaymentPlanResponse.model_validate(plan).__dict__,
        message="Payment plan added successfully.",
    )


@router.get("/{booking_id}/payment-plans", status_code=status.HTTP_200_OK, response_model=dict)
async def get_payment_plans(
    booking_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("bookings.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get payment plans for booking."""
    service = BookingService(session)
    plans = await service.get_payment_plans(booking_id)

    data = [BookingPaymentPlanResponse.model_validate(p).__dict__ for p in plans]

    return ok(data=data)


@router.post("/{booking_id}/payment-plans/{plan_id}/mark-paid", status_code=status.HTTP_200_OK, response_model=dict)
async def mark_payment_received(
    booking_id: str,
    plan_id: str,
    request: PaymentMarkAsPaidRequest,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("bookings.edit")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Mark payment as received."""
    service = BookingService(session)

    plan = await service.mark_payment_received(
        payment_plan_id=plan_id,
        transaction_ref=request.transaction_ref,
        payment_method=request.payment_method,
        notes=request.notes,
    )

    await session.commit()

    logger.info(f"Payment marked paid | plan={plan_id} | by={current_user.id}")

    return ok(
        data=BookingPaymentPlanResponse.model_validate(plan).__dict__,
        message="Payment marked as received.",
    )


@router.get("/{booking_id}/payment-summary", status_code=status.HTTP_200_OK, response_model=dict)
async def get_payment_summary(
    booking_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("bookings.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get payment summary for booking."""
    service = BookingService(session)
    summary = await service.get_booking_payment_summary(booking_id)

    return ok(data=summary)


# ── Booking Cancellation ──────────────────────────────────────────────

@router.post("/{booking_id}/cancel", status_code=status.HTTP_200_OK, response_model=dict)
async def cancel_booking(
    booking_id: str,
    request: BookingCancellationRequest,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("bookings.cancel")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Cancel booking."""
    service = BookingService(session)

    cancellation = await service.cancel_booking(
        booking_id=booking_id,
        reason=request.reason,
        cancelled_by_user_id=str(current_user.id),
        notes=request.notes,
    )

    await session.commit()

    logger.info(f"Booking cancelled | id={booking_id} | by={current_user.id}")

    return ok(
        data=BookingCancellationResponse.model_validate(cancellation).__dict__,
        message="Booking cancelled successfully.",
    )


@router.post("/{booking_id}/cancellations/{cancellation_id}/refund", status_code=status.HTTP_200_OK, response_model=dict)
async def process_refund(
    booking_id: str,
    cancellation_id: str,
    transaction_ref: str = Query(...),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("bookings.cancel")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Process refund for cancellation."""
    service = BookingService(session)

    cancellation = await service.process_refund(
        cancellation_id=cancellation_id,
        transaction_ref=transaction_ref,
    )

    await session.commit()

    logger.info(f"Refund processed | cancellation={cancellation_id} | by={current_user.id}")

    return ok(
        data=BookingCancellationResponse.model_validate(cancellation).__dict__,
        message="Refund processed successfully.",
    )


# ── Possession ────────────────────────────────────────────────────────

@router.post("/{booking_id}/possession", status_code=status.HTTP_201_CREATED, response_model=dict)
async def create_possession(
    booking_id: str,
    request: PossessionCreate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("bookings.edit")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Create possession record."""
    service = BookingService(session)

    possession = await service.create_possession(
        booking_id=booking_id,
        possession_date=request.possession_date,
        possession_notes=request.possession_notes,
        created_by=str(current_user.id),
    )

    await session.commit()

    return created(
        data=PossessionResponse.model_validate(possession).__dict__,
        message="Possession created successfully.",
    )


@router.get("/{booking_id}/possession", status_code=status.HTTP_200_OK, response_model=dict)
async def get_possession(
    booking_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("bookings.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get possession record."""
    service = BookingService(session)
    booking = await service.get_booking(booking_id)

    if not booking.possession:
        return ok(data=None, message="No possession record found")

    return ok(data=PossessionResponse.model_validate(booking.possession).__dict__)


@router.post("/{booking_id}/possession/handover", status_code=status.HTTP_200_OK, response_model=dict)
async def handover_possession(
    booking_id: str,
    request: PossessionHandoverRequest,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("bookings.edit")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Handover possession to customer."""
    service = BookingService(session)
    booking = await service.get_booking(booking_id)

    if not booking.possession:
        return ok(data=None, message="No possession record found for booking")

    possession = await service.handover_possession(
        possession_id=booking.possession.id,
        keys_handed_by_user_id=str(current_user.id),
        keys_handed_to_customer=request.keys_handed_to_customer,
        documents_handed=request.documents_handed,
        final_inspection_done=request.final_inspection_done,
        inspection_notes=request.inspection_notes,
    )

    await session.commit()

    logger.info(f"Possession handed over | booking={booking_id} | by={current_user.id}")

    return ok(
        data=PossessionResponse.model_validate(possession).__dict__,
        message="Possession handed over successfully.",
    )


# ── Statistics ────────────────────────────────────────────────────────

@router.get("/stats/overview", status_code=status.HTTP_200_OK, response_model=dict)
async def get_booking_statistics(
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("bookings.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get booking statistics."""
    service = BookingService(session)
    stats = await service.get_booking_statistics()

    return ok(data=stats)
