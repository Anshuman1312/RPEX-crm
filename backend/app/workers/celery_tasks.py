import asyncio
from datetime import date, timedelta

from sqlalchemy import func, select

from app.database.postgres import SessionLocal
from app.models.approval_request import ApprovalRequest
from app.models.audit_log import AuditLog
from app.models.booking import Booking
from app.models.customer_payment import CustomerPayment
from app.models.invoice import Invoice
from app.workers.celery_app import celery


@celery.task(name="app.workers.celery_tasks.generate_daily_lead_report")
def generate_daily_lead_report() -> str:
    return "Daily lead report generated"


@celery.task(name="app.workers.celery_tasks.generate_weekly_lead_report")
def generate_weekly_lead_report() -> str:
    return "Weekly lead report generated"


@celery.task(name="app.workers.celery_tasks.send_payment_reminders")
def send_payment_reminders() -> str:
    async def _run() -> str:
        today = date.today()
        async with SessionLocal() as session:
            overdue_rows = (
                await session.execute(
                    select(Invoice)
                    .where(Invoice.due_date.is_not(None))
                    .where(Invoice.due_date < today)
                    .where(Invoice.status.in_(["ISSUED", "PARTIAL", "OVERDUE"]))
                )
            ).scalars().all()

            for invoice in overdue_rows:
                session.add(
                    AuditLog(
                        user_id=None,
                        module="automation",
                        action="payment_reminder_enqueued",
                        old_value=None,
                        new_value={
                            "invoice_id": str(invoice.id),
                            "customer_id": str(invoice.customer_id),
                            "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
                        },
                    )
                )
            await session.commit()
            return f"Payment reminders queued for {len(overdue_rows)} overdue invoices"

    return asyncio.run(_run())


@celery.task(name="app.workers.celery_tasks.calculate_commissions")
def calculate_commissions() -> str:
    async def _run() -> str:
        window_start = date.today() - timedelta(days=1)
        async with SessionLocal() as session:
            bookings = (
                await session.execute(
                    select(Booking)
                    .where(Booking.booking_date >= window_start)
                    .where(Booking.status.in_(["BOOKED", "CONFIRMED"]))
                )
            ).scalars().all()

            created_requests = 0
            for booking in bookings:
                requester_id = booking.sales_executive_id or booking.partner_user_id
                if not requester_id:
                    continue

                existing = (
                    await session.execute(
                        select(ApprovalRequest)
                        .where(ApprovalRequest.module == "commissions")
                        .where(ApprovalRequest.entity_type == "booking")
                        .where(ApprovalRequest.entity_id == str(booking.id))
                        .where(ApprovalRequest.action == "commission_payout")
                        .where(ApprovalRequest.status == "PENDING")
                    )
                ).scalar_one_or_none()
                if existing:
                    continue

                estimated_commission = float(booking.booking_value) * 0.01
                session.add(
                    ApprovalRequest(
                        module="commissions",
                        entity_type="booking",
                        entity_id=str(booking.id),
                        action="commission_payout",
                        status="PENDING",
                        requested_by=requester_id,
                        approver_id=None,
                        reason="Auto-created by daily commission task",
                        payload={
                            "booking_value": str(booking.booking_value),
                            "estimated_commission": round(estimated_commission, 2),
                            "sales_executive_id": str(booking.sales_executive_id) if booking.sales_executive_id else None,
                            "partner_user_id": str(booking.partner_user_id) if booking.partner_user_id else None,
                        },
                    )
                )
                created_requests += 1

            await session.commit()
            return f"Commission calculation created {created_requests} approval requests"

    return asyncio.run(_run())


@celery.task(name="app.workers.celery_tasks.generate_daily_performance_report")
def generate_daily_performance_report() -> str:
    async def _run() -> str:
        today = date.today()
        async with SessionLocal() as session:
            booking_total = (
                await session.execute(select(func.coalesce(func.sum(Booking.booking_value), 0)).where(Booking.booking_date == today))
            ).scalar_one()
            payments_total = (
                await session.execute(
                    select(func.coalesce(func.sum(CustomerPayment.amount), 0)).where(CustomerPayment.payment_date == today)
                )
            ).scalar_one()
            bookings_count = (
                await session.execute(select(func.count()).select_from(Booking).where(Booking.booking_date == today))
            ).scalar_one()
            payments_count = (
                await session.execute(
                    select(func.count()).select_from(CustomerPayment).where(CustomerPayment.payment_date == today)
                )
            ).scalar_one()

            session.add(
                AuditLog(
                    user_id=None,
                    module="automation",
                    action="daily_performance_report",
                    old_value=None,
                    new_value={
                        "date": today.isoformat(),
                        "bookings_count": bookings_count,
                        "booking_total": str(booking_total),
                        "payments_count": payments_count,
                        "payments_total": str(payments_total),
                    },
                )
            )
            await session.commit()
            return "Daily performance report generated and logged"

    return asyncio.run(_run())


@celery.task(name="app.workers.celery_tasks.auto_approve_request")
def auto_approve_request(request_id: str) -> str:
    async def _run() -> str:
        async with SessionLocal() as session:
            row = await session.get(ApprovalRequest, request_id)
            if not row:
                return f"Approval request {request_id} not found"
            if row.status != "PENDING":
                return f"Approval request {request_id} already {row.status}"

            estimated_commission = float((row.payload or {}).get("estimated_commission", 0))
            row.status = "APPROVED" if estimated_commission <= 100000 else "PENDING"
            session.add(
                AuditLog(
                    user_id=None,
                    module="automation",
                    action="auto_approve_request",
                    old_value={"status": "PENDING"},
                    new_value={"status": row.status, "request_id": request_id},
                )
            )
            await session.commit()
            return f"Approval request {request_id} processed with status {row.status}"

    return asyncio.run(_run())
