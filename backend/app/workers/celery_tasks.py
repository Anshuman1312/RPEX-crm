import asyncio
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func, or_, select

from app.database.postgres import SessionLocal
from app.models.approval_request import ApprovalRequest
from app.models.audit_log import AuditLog
from app.models.booking import Booking
from app.models.customer import Customer
from app.models.customer_payment import CustomerPayment
from app.models.followup import FollowUp
from app.models.invoice import Invoice
from app.models.lead import Lead
from app.models.role import Role
from app.models.user import User
from app.workers.celery_app import celery


@celery.task(name="app.workers.celery_tasks.generate_daily_lead_report")
def generate_daily_lead_report() -> str:
    return "Daily lead report generated"


@celery.task(name="app.workers.celery_tasks.generate_weekly_lead_report")
def generate_weekly_lead_report() -> str:
    return "Weekly lead report generated"


@celery.task(name="app.workers.celery_tasks.auto_assign_new_leads")
def auto_assign_new_leads() -> str:
    async def _run() -> str:
        async with SessionLocal() as session:
            assignees = (
                await session.execute(
                    select(User)
                    .join(Role, Role.id == User.role_id)
                    .where(User.is_active.is_(True))
                    .where(Role.name.in_(["SALES_MANAGER", "SALES_EXECUTIVE", "TELECALLER", "CRM_EXECUTIVE", "SALES"]))
                    .order_by(User.created_at.asc())
                )
            ).scalars().all()
            if not assignees:
                return "Auto lead assignment skipped: no active assignees"

            pending_leads = (
                await session.execute(
                    select(Lead)
                    .where(Lead.assigned_to.is_(None))
                    .where(Lead.status.in_(["NEW", "CONTACTED", "FOLLOW_UP"]))
                    .order_by(Lead.created_at.asc())
                    .limit(500)
                )
            ).scalars().all()

            if not pending_leads:
                return "Auto lead assignment: no unassigned leads"

            assigned_count = 0
            for index, lead in enumerate(pending_leads):
                assignee = assignees[index % len(assignees)]
                lead.assigned_to = assignee.id
                assigned_count += 1
                session.add(
                    AuditLog(
                        user_id=None,
                        module="automation",
                        action="auto_lead_assignment",
                        old_value={"lead_id": str(lead.id), "assigned_to": None},
                        new_value={"lead_id": str(lead.id), "assigned_to": str(assignee.id)},
                    )
                )

            await session.commit()
            return f"Auto lead assignment completed for {assigned_count} leads"

    return asyncio.run(_run())


@celery.task(name="app.workers.celery_tasks.detect_duplicate_leads")
def detect_duplicate_leads() -> str:
    async def _run() -> str:
        async with SessionLocal() as session:
            email_dupes = (
                await session.execute(
                    select(Lead.email, func.count(Lead.id).label("hits"))
                    .group_by(Lead.email)
                    .having(func.count(Lead.id) > 1)
                )
            ).all()
            phone_dupes = (
                await session.execute(
                    select(Lead.phone, func.count(Lead.id).label("hits"))
                    .group_by(Lead.phone)
                    .having(func.count(Lead.id) > 1)
                )
            ).all()

            if not email_dupes and not phone_dupes:
                return "Duplicate lead detection completed: no duplicates found"

            session.add(
                AuditLog(
                    user_id=None,
                    module="automation",
                    action="duplicate_lead_detection",
                    old_value=None,
                    new_value={
                        "duplicate_emails": [{"email": row[0], "count": row[1]} for row in email_dupes],
                        "duplicate_phones": [{"phone": row[0], "count": row[1]} for row in phone_dupes],
                    },
                )
            )
            await session.commit()
            return f"Duplicate lead detection logged {len(email_dupes)} email groups and {len(phone_dupes)} phone groups"

    return asyncio.run(_run())


@celery.task(name="app.workers.celery_tasks.send_missed_followup_alerts")
def send_missed_followup_alerts() -> str:
    async def _run() -> str:
        now = datetime.now(timezone.utc)
        async with SessionLocal() as session:
            overdue_followups = (
                await session.execute(
                    select(FollowUp)
                    .where(FollowUp.status.in_(["PENDING", "SCHEDULED"]))
                    .where(FollowUp.auto_reminder_enabled.is_(True))
                    .where(FollowUp.followup_date < now)
                    .order_by(FollowUp.followup_date.asc())
                    .limit(500)
                )
            ).scalars().all()

            for row in overdue_followups:
                session.add(
                    AuditLog(
                        user_id=None,
                        module="automation",
                        action="missed_followup_alert",
                        old_value=None,
                        new_value={
                            "followup_id": str(row.id),
                            "lead_id": str(row.lead_id),
                            "assigned_to": str(row.assigned_to),
                            "followup_date": row.followup_date.isoformat(),
                        },
                    )
                )

            await session.commit()
            return f"Missed follow-up alerts queued for {len(overdue_followups)} follow-ups"

    return asyncio.run(_run())


@celery.task(name="app.workers.celery_tasks.send_whatsapp_reminders")
def send_whatsapp_reminders() -> str:
    async def _run() -> str:
        today = date.today()
        async with SessionLocal() as session:
            overdue_invoices = (
                await session.execute(
                    select(func.count())
                    .select_from(Invoice)
                    .where(Invoice.due_date.is_not(None))
                    .where(Invoice.due_date < today)
                    .where(Invoice.status.in_(["ISSUED", "PARTIAL", "OVERDUE"]))
                )
            ).scalar_one()
            upcoming_followups = (
                await session.execute(
                    select(func.count())
                    .select_from(FollowUp)
                    .where(FollowUp.status.in_(["PENDING", "SCHEDULED"]))
                    .where(FollowUp.followup_date >= datetime.now(timezone.utc))
                )
            ).scalar_one()

            session.add(
                AuditLog(
                    user_id=None,
                    module="automation",
                    action="whatsapp_reminders_enqueued",
                    old_value=None,
                    new_value={
                        "overdue_invoices": overdue_invoices,
                        "upcoming_followups": upcoming_followups,
                    },
                )
            )
            await session.commit()
            return "WhatsApp reminders queued"

    return asyncio.run(_run())


@celery.task(name="app.workers.celery_tasks.run_email_automation")
def run_email_automation() -> str:
    async def _run() -> str:
        today = date.today()
        async with SessionLocal() as session:
            new_leads_count = (
                await session.execute(
                    select(func.count()).select_from(Lead).where(func.date(Lead.created_at) == today)
                )
            ).scalar_one()
            due_followups_count = (
                await session.execute(
                    select(func.count())
                    .select_from(FollowUp)
                    .where(FollowUp.status.in_(["PENDING", "SCHEDULED"]))
                    .where(func.date(FollowUp.followup_date) == today)
                )
            ).scalar_one()

            session.add(
                AuditLog(
                    user_id=None,
                    module="automation",
                    action="email_automation_enqueued",
                    old_value=None,
                    new_value={
                        "new_leads": new_leads_count,
                        "due_followups": due_followups_count,
                    },
                )
            )
            await session.commit()
            return "Email automation queued"

    return asyncio.run(_run())


@celery.task(name="app.workers.celery_tasks.send_booking_confirmations")
def send_booking_confirmations() -> str:
    async def _run() -> str:
        today = date.today()
        async with SessionLocal() as session:
            todays_bookings = (
                await session.execute(
                    select(Booking)
                    .where(Booking.booking_date == today)
                    .where(Booking.status.in_(["BOOKED", "CONFIRMED"]))
                    .order_by(Booking.created_at.desc())
                    .limit(500)
                )
            ).scalars().all()

            for booking in todays_bookings:
                session.add(
                    AuditLog(
                        user_id=None,
                        module="automation",
                        action="booking_confirmation_enqueued",
                        old_value=None,
                        new_value={
                            "booking_id": str(booking.id),
                            "customer_id": str(booking.customer_id),
                            "booking_date": booking.booking_date.isoformat(),
                            "status": booking.status,
                        },
                    )
                )

            await session.commit()
            return f"Booking confirmations queued for {len(todays_bookings)} bookings"

    return asyncio.run(_run())


@celery.task(name="app.workers.celery_tasks.auto_generate_invoices")
def auto_generate_invoices() -> str:
    async def _run() -> str:
        today = date.today()
        async with SessionLocal() as session:
            eligible_bookings = (
                await session.execute(
                    select(Booking)
                    .where(Booking.status.in_(["BOOKED", "CONFIRMED"]))
                    .where(
                        ~Booking.id.in_(
                            select(Invoice.booking_id).where(Invoice.booking_id.is_not(None))
                        )
                    )
                    .order_by(Booking.created_at.asc())
                    .limit(300)
                )
            ).scalars().all()

            created = 0
            for booking in eligible_bookings:
                creator_id = booking.sales_executive_id or booking.partner_user_id
                if not creator_id:
                    continue

                invoice_number = f"INV-{today.strftime('%Y%m%d')}-{str(booking.id)[:8].upper()}"
                invoice = Invoice(
                    customer_id=booking.customer_id,
                    booking_id=booking.id,
                    invoice_number=invoice_number,
                    invoice_date=today,
                    due_date=today + timedelta(days=7),
                    amount=booking.booking_value,
                    gst_amount=0,
                    status="ISSUED",
                    notes="Auto-generated from booking",
                    created_by=creator_id,
                    partner_user_id=booking.partner_user_id,
                )
                session.add(invoice)
                created += 1

                session.add(
                    AuditLog(
                        user_id=None,
                        module="automation",
                        action="invoice_auto_generated",
                        old_value=None,
                        new_value={
                            "booking_id": str(booking.id),
                            "invoice_number": invoice_number,
                            "amount": str(booking.booking_value),
                        },
                    )
                )

            await session.commit()
            return f"Invoice generation completed for {created} bookings"

    return asyncio.run(_run())


@celery.task(name="app.workers.celery_tasks.send_anniversary_birthday_wishes")
def send_anniversary_birthday_wishes() -> str:
    async def _run() -> str:
        today = date.today()
        async with SessionLocal() as session:
            celebrants = (
                await session.execute(
                    select(Customer).where(
                        or_(
                            func.to_char(Customer.birth_date, "MM-DD") == today.strftime("%m-%d"),
                            func.to_char(Customer.anniversary_date, "MM-DD") == today.strftime("%m-%d"),
                        )
                    )
                )
            ).scalars().all()

            for customer in celebrants:
                event_type = "birthday" if customer.birth_date and customer.birth_date.strftime("%m-%d") == today.strftime("%m-%d") else "anniversary"
                session.add(
                    AuditLog(
                        user_id=None,
                        module="automation",
                        action="customer_greeting_enqueued",
                        old_value=None,
                        new_value={
                            "customer_id": str(customer.id),
                            "event_type": event_type,
                            "phone": customer.phone,
                            "email": customer.email,
                        },
                    )
                )

            await session.commit()
            return f"Anniversary/Birthday wishes queued for {len(celebrants)} customers"

    return asyncio.run(_run())


@celery.task(name="app.workers.celery_tasks.refresh_ai_lead_scoring")
def refresh_ai_lead_scoring() -> str:
    async def _run() -> str:
        async with SessionLocal() as session:
            leads = (await session.execute(select(Lead).order_by(Lead.created_at.desc()).limit(1000))).scalars().all()
            for lead in leads:
                score = 40
                if lead.status in {"SITE_VISIT", "NEGOTIATION", "BOOKING"}:
                    score += 25
                if lead.source in {"REFERRAL", "ORGANIC", "GOOGLE"}:
                    score += 15
                if lead.medium in {"whatsapp", "email", "social"}:
                    score += 10
                if lead.assigned_to:
                    score += 10

                bounded_score = max(0, min(score, 100))
                lead.extra_data = {
                    **(lead.extra_data or {}),
                    "ai_score": bounded_score,
                    "ai_scored_at": datetime.now(timezone.utc).isoformat(),
                    "ai_score_model": "heuristic-v1",
                }

            session.add(
                AuditLog(
                    user_id=None,
                    module="automation",
                    action="ai_lead_scoring_refresh",
                    old_value=None,
                    new_value={"leads_scored": len(leads)},
                )
            )
            await session.commit()
            return f"AI lead scoring refreshed for {len(leads)} leads"

    return asyncio.run(_run())


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
