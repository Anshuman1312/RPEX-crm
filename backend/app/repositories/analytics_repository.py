"""
Repositories for reports and analytics data aggregation.

Provides queries for KPIs, metrics, and analytics across all entities.
"""

from __future__ import annotations

from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Optional, Dict, List
from uuid import UUID

from sqlalchemy import select, func, and_, or_, Text
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from app.models import (
    Lead, Booking, Invoice, Task,
    User, Project, Customer, FollowUp, Activity
)
from app.utils.enums import LeadStatus, BookingStatus, PaymentStatus
from app.schemas.report import (
    LeadMetricsReport, LeadMetric, BookingMetricsReport, BookingMetric,
    RevenueAnalyticsReport, RevenueMetric, TeamPerformanceReport,
    TeamMemberPerformance, ProjectAnalyticsReport, ProjectSalesMetrics,
    CustomerAnalyticsReport, CustomerSegment, SalesPipelineReport,
    PipelineStage, ActivitySummary, DashboardMetrics, PaymentAnalytics,
    LeadConversionFunnel, PeriodComparison, ComparisonReport, KPISummary,
    DateRangeFilter
)


class LeadAnalyticsRepository(BaseRepository):
    """Analytics queries for leads."""

    async def get_lead_metrics(
        self,
        session: AsyncSession,
        start_date: date,
        end_date: date
    ) -> LeadMetricsReport:
        """Get lead metrics for date range."""
        # Total leads in range
        total_stmt = select(func.count(Lead.id)).where(
            and_(
                Lead.created_at >= datetime.combine(start_date, datetime.min.time()),
                Lead.created_at < datetime.combine(end_date + timedelta(days=1), datetime.min.time())
            )
        )
        total_leads = (await session.execute(total_stmt)).scalar() or 0

        # New leads (created in range)
        new_stmt = select(func.count(Lead.id)).where(
            and_(
                Lead.created_at >= datetime.combine(start_date, datetime.min.time()),
                Lead.created_at < datetime.combine(end_date + timedelta(days=1), datetime.min.time()),
                Lead.is_deleted == False
            )
        )
        new_leads = (await session.execute(new_stmt)).scalar() or 0

        # Converted leads
        converted_stmt = select(func.count(Lead.id)).where(
            and_(
                Lead.status == LeadStatus.CONVERTED.value,
                Lead.updated_at >= datetime.combine(start_date, datetime.min.time()),
                Lead.updated_at < datetime.combine(end_date + timedelta(days=1), datetime.min.time())
            )
        )
        converted = (await session.execute(converted_stmt)).scalar() or 0

        # Lost leads
        lost_stmt = select(func.count(Lead.id)).where(
            and_(
                Lead.status == LeadStatus.LOST.value,
                Lead.updated_at >= datetime.combine(start_date, datetime.min.time()),
                Lead.updated_at < datetime.combine(end_date + timedelta(days=1), datetime.min.time())
            )
        )
        lost = (await session.execute(lost_stmt)).scalar() or 0

        conversion_rate = (converted / new_leads * 100) if new_leads > 0 else 0
        loss_rate = (lost / new_leads * 100) if new_leads > 0 else 0

        # By status
        status_stmt = select(
            Lead.status,
            func.count(Lead.id)
        ).where(
            Lead.is_deleted == False
        ).group_by(Lead.status)
        status_counts = dict((await session.execute(status_stmt)).all() or [])

        # By source
        source_stmt = select(
            Lead.source,
            func.count(Lead.id)
        ).where(
            Lead.is_deleted == False
        ).group_by(Lead.source)
        source_counts = dict((await session.execute(source_stmt)).all() or [])

        return LeadMetricsReport(
            period_start=start_date,
            period_end=end_date,
            total_leads=total_leads,
            new_leads_count=new_leads,
            conversion_rate=conversion_rate,
            loss_rate=loss_rate,
            by_status=status_counts,
            by_source=source_counts
        )

    async def get_lead_conversion_funnel(
        self,
        session: AsyncSession
    ) -> LeadConversionFunnel:
        """Get lead conversion funnel."""
        new_stmt = select(func.count(Lead.id)).where(Lead.status == LeadStatus.NEW.value)
        new = (await session.execute(new_stmt)).scalar() or 0

        contacted_stmt = select(func.count(Lead.id)).where(Lead.status == LeadStatus.CONTACTED.value)
        contacted = (await session.execute(contacted_stmt)).scalar() or 0

        qualified_stmt = select(func.count(Lead.id)).where(Lead.status == LeadStatus.QUALIFIED.value)
        qualified = (await session.execute(qualified_stmt)).scalar() or 0

        converted_stmt = select(func.count(Lead.id)).where(Lead.status == LeadStatus.CONVERTED.value)
        converted = (await session.execute(converted_stmt)).scalar() or 0

        lost_stmt = select(func.count(Lead.id)).where(Lead.status == LeadStatus.LOST.value)
        lost = (await session.execute(lost_stmt)).scalar() or 0

        total = new + contacted + qualified + converted + lost
        
        return LeadConversionFunnel(
            new=new,
            contacted=contacted,
            qualified=qualified,
            proposal_sent=0,  # Not tracked separately in current model
            negotiation=0,    # Not tracked separately
            converted=converted,
            lost=lost,
            contact_rate=(contacted / new * 100) if new > 0 else 0,
            qualification_rate=(qualified / new * 100) if new > 0 else 0,
            proposal_rate=0,
            conversion_rate=(converted / new * 100) if new > 0 else 0
        )


class BookingAnalyticsRepository(BaseRepository):
    """Analytics queries for bookings."""

    async def get_booking_metrics(
        self,
        session: AsyncSession,
        start_date: date,
        end_date: date
    ) -> BookingMetricsReport:
        """Get booking metrics for date range."""
        # Total bookings
        total_stmt = select(func.count(Booking.id)).where(
            and_(
                Booking.created_at >= datetime.combine(start_date, datetime.min.time()),
                Booking.created_at < datetime.combine(end_date + timedelta(days=1), datetime.min.time()),
                Booking.is_deleted == False
            )
        )
        total_bookings = (await session.execute(total_stmt)).scalar() or 0

        # Confirmed bookings
        confirmed_stmt = select(func.count(Booking.id)).where(
            and_(
                Booking.status == BookingStatus.CONFIRMED.value,
                Booking.is_deleted == False
            )
        )
        confirmed = (await session.execute(confirmed_stmt)).scalar() or 0

        # Cancelled bookings
        cancelled_stmt = select(func.count(Booking.id)).where(
            and_(
                Booking.status == BookingStatus.CANCELLED.value,
                Booking.is_deleted == False
            )
        )
        cancelled = (await session.execute(cancelled_stmt)).scalar() or 0

        # Total booking value
        value_stmt = select(func.sum(Booking.booking_amount)).where(
            Booking.is_deleted == False
        )
        total_value = (await session.execute(value_stmt)).scalar() or Decimal(0)

        avg_value = (total_value / total_bookings) if total_bookings > 0 else Decimal(0)
        cancellation_rate = (cancelled / total_bookings * 100) if total_bookings > 0 else 0

        # By status
        status_stmt = select(
            Booking.status,
            func.count(Booking.id)
        ).where(
            Booking.is_deleted == False
        ).group_by(Booking.status)
        status_counts = dict((await session.execute(status_stmt)).all() or [])

        return BookingMetricsReport(
            period_start=start_date,
            period_end=end_date,
            total_bookings=total_bookings,
            confirmed_count=confirmed,
            cancelled_count=cancelled,
            total_booking_value=total_value,
            average_booking_value=avg_value,
            cancellation_rate=cancellation_rate,
            by_status=status_counts
        )


class RevenueAnalyticsRepository(BaseRepository):
    """Analytics queries for revenue."""

    async def get_revenue_analytics(
        self,
        session: AsyncSession,
        start_date: date,
        end_date: date
    ) -> RevenueAnalyticsReport:
        """Get revenue analytics for date range."""
        # Invoiced amount (all paid invoices)
        invoiced_stmt = select(func.sum(Invoice.total_amount)).where(
            and_(
                Invoice.created_at >= datetime.combine(start_date, datetime.min.time()),
                Invoice.created_at < datetime.combine(end_date + timedelta(days=1), datetime.min.time()),
                Invoice.is_deleted == False
            )
        )
        total_invoiced = (await session.execute(invoiced_stmt)).scalar() or Decimal(0)

        # Paid amount
        paid_stmt = select(func.sum(Invoice.paid_amount)).where(
            and_(
                Invoice.is_deleted == False,
                Invoice.payment_status == PaymentStatus.PAID.value
            )
        )
        total_paid = (await session.execute(paid_stmt)).scalar() or Decimal(0)

        # Pending amount
        pending_stmt = select(func.sum(Invoice.total_amount - Invoice.paid_amount)).where(
            and_(
                Invoice.is_deleted == False,
                Invoice.payment_status.in_([PaymentStatus.PENDING.value, PaymentStatus.PARTIALLY_PAID.value])
            )
        )
        total_pending = (await session.execute(pending_stmt)).scalar() or Decimal(0)

        # Overdue amount (due_date < today and status not PAID)
        overdue_stmt = select(func.sum(Invoice.total_amount - Invoice.paid_amount)).where(
            and_(
                Invoice.due_date < date.today(),
                Invoice.payment_status != PaymentStatus.PAID.value,
                Invoice.is_deleted == False
            )
        )
        total_overdue = (await session.execute(overdue_stmt)).scalar() or Decimal(0)

        collection_rate = (total_paid / total_invoiced * 100) if total_invoiced > 0 else 0

        return RevenueAnalyticsReport(
            period_start=start_date,
            period_end=end_date,
            total_invoiced=total_invoiced,
            total_paid=total_paid,
            total_pending=total_pending,
            total_overdue=total_overdue,
            collection_rate=collection_rate
        )

    async def get_payment_analytics(
        self,
        session: AsyncSession
    ) -> PaymentAnalytics:
        """Get payment analytics."""
        # Total invoices
        total_inv_stmt = select(func.count(Invoice.id)).where(Invoice.is_deleted == False)
        total_invoices = (await session.execute(total_inv_stmt)).scalar() or 0

        # Paid invoices
        paid_inv_stmt = select(func.count(Invoice.id)).where(
            and_(Invoice.payment_status == PaymentStatus.PAID.value, Invoice.is_deleted == False)
        )
        paid_invoices = (await session.execute(paid_inv_stmt)).scalar() or 0

        # Pending invoices
        pending_inv_stmt = select(func.count(Invoice.id)).where(
            and_(Invoice.payment_status == PaymentStatus.PENDING.value, Invoice.is_deleted == False)
        )
        pending_invoices = (await session.execute(pending_inv_stmt)).scalar() or 0

        # Overdue invoices
        overdue_inv_stmt = select(func.count(Invoice.id)).where(
            and_(
                Invoice.due_date < date.today(),
                Invoice.payment_status != PaymentStatus.PAID.value,
                Invoice.is_deleted == False
            )
        )
        overdue_invoices = (await session.execute(overdue_inv_stmt)).scalar() or 0

        # Partial invoices
        partial_inv_stmt = select(func.count(Invoice.id)).where(
            and_(
                Invoice.payment_status == PaymentStatus.PARTIALLY_PAID.value,
                Invoice.is_deleted == False
            )
        )
        partial_invoices = (await session.execute(partial_inv_stmt)).scalar() or 0

        # Amounts
        total_amt_stmt = select(func.sum(Invoice.total_amount)).where(Invoice.is_deleted == False)
        total_amount = (await session.execute(total_amt_stmt)).scalar() or Decimal(0)

        paid_amt_stmt = select(func.sum(Invoice.paid_amount)).where(Invoice.is_deleted == False)
        paid_amount = (await session.execute(paid_amt_stmt)).scalar() or Decimal(0)

        pending_amount = total_amount - paid_amount

        overdue_amt_stmt = select(func.sum(Invoice.total_amount - Invoice.paid_amount)).where(
            and_(
                Invoice.due_date < date.today(),
                Invoice.status != InvoiceStatusValue.PAID,
                Invoice.is_deleted == False
            )
        )
        overdue_amount = (await session.execute(overdue_amt_stmt)).scalar() or Decimal(0)

        return PaymentAnalytics(
            total_invoices=total_invoices,
            paid_invoices=paid_invoices,
            pending_invoices=pending_invoices,
            overdue_invoices=overdue_invoices,
            partial_invoices=partial_invoices,
            total_amount=total_amount,
            paid_amount=paid_amount,
            pending_amount=pending_amount,
            overdue_amount=overdue_amount
        )


class TeamPerformanceRepository(BaseRepository):
    """Analytics queries for team performance."""

    async def get_team_performance(
        self,
        session: AsyncSession,
        start_date: date,
        end_date: date
    ) -> TeamPerformanceReport:
        """Get team performance metrics."""
        # Get all active users
        user_stmt = select(User).where(User.is_active == True)
        users = (await session.execute(user_stmt)).scalars().all()

        team_members: List[TeamMemberPerformance] = []

        for user in users:
            # Leads assigned to user
            leads_stmt = select(func.count(Lead.id)).where(Lead.assigned_to_user_id == user.id)
            leads_assigned = (await session.execute(leads_stmt)).scalar() or 0

            # Leads converted by user
            converted_stmt = select(func.count(Lead.id)).where(
                and_(
                    Lead.assigned_to_user_id == user.id,
                    Lead.status == LeadStatus.CONVERTED.value
                )
            )
            leads_converted = (await session.execute(converted_stmt)).scalar() or 0

            # Tasks completed by user
            tasks_stmt = select(func.count(Task.id)).where(
                Task.assigned_to_user_id == user.id
            )
            tasks_completed = (await session.execute(tasks_stmt)).scalar() or 0

            if leads_assigned > 0:
                conversion_rate = (leads_converted / leads_assigned * 100)
                team_members.append(
                    TeamMemberPerformance(
                        user_id=user.id,
                        full_name=user.full_name,
                        role=user.role or "Staff",
                        leads_assigned=leads_assigned,
                        leads_converted=leads_converted,
                        conversion_rate=conversion_rate,
                        bookings_assigned=0,
                        booking_value=Decimal(0),
                        tasks_completed=tasks_completed,
                        tasks_completion_rate=0
                    )
                )

        total_leads = sum(m.leads_assigned for m in team_members)
        total_converted = sum(m.leads_converted for m in team_members)
        avg_conversion = (total_converted / total_leads * 100) if total_leads > 0 else 0

        return TeamPerformanceReport(
            period_start=start_date,
            period_end=end_date,
            total_team_members=len(team_members),
            total_leads_processed=total_leads,
            total_leads_converted=total_converted,
            total_bookings=0,
            total_booking_value=Decimal(0),
            average_conversion_rate=avg_conversion,
            team_members=team_members
        )


class ProjectAnalyticsRepository(BaseRepository):
    """Analytics queries for projects."""

    async def get_project_analytics(
        self,
        session: AsyncSession,
        start_date: date,
        end_date: date
    ) -> ProjectAnalyticsReport:
        """Get project-wise analytics."""
        # Get all projects
        project_stmt = select(Project).where(Project.is_deleted == False)
        projects = (await session.execute(project_stmt)).scalars().all()

        project_metrics: List[ProjectSalesMetrics] = []
        total_units = 0
        total_booked = 0
        total_sold = 0
        total_booking_val = Decimal(0)
        total_sale_val = Decimal(0)

        for project in projects:
            # Get units for project
            units_stmt = select(func.count(func.distinct(Booking.unit_id))).where(
                Booking.project_id == project.id
            )
            booked_units = (await session.execute(units_stmt)).scalar() or 0
            
            total_units += (project.total_units or 0)
            total_booked += booked_units

            booking_rate = (booked_units / (project.total_units or 1) * 100) if project.total_units else 0

            project_metrics.append(
                ProjectSalesMetrics(
                    project_id=project.id,
                    project_name=project.name,
                    total_units=project.total_units or 0,
                    available_units=(project.total_units or 0) - booked_units,
                    booked_units=booked_units,
                    sold_units=booked_units,
                    booking_rate=booking_rate,
                    sale_rate=booking_rate,
                    total_booking_value=Decimal(0),
                    total_sale_value=Decimal(0)
                )
            )

        overall_booking_rate = (total_booked / total_units * 100) if total_units > 0 else 0

        return ProjectAnalyticsReport(
            period_start=start_date,
            period_end=end_date,
            total_projects=len(project_metrics),
            total_units=total_units,
            total_booked_units=total_booked,
            total_sold_units=total_booked,
            overall_booking_rate=overall_booking_rate,
            overall_sale_rate=overall_booking_rate,
            total_booking_value=total_booking_val,
            total_sale_value=total_sale_val,
            projects=project_metrics
        )


class CustomerAnalyticsRepository(BaseRepository):
    """Analytics queries for customers."""

    async def get_customer_analytics(
        self,
        session: AsyncSession,
        start_date: date,
        end_date: date
    ) -> CustomerAnalyticsReport:
        """Get customer analytics."""
        # Total customers
        total_stmt = select(func.count(Customer.id)).where(Customer.is_deleted == False)
        total_customers = (await session.execute(total_stmt)).scalar() or 0

        # Active customers (have bookings)
        active_stmt = select(func.count(func.distinct(Booking.customer_id))).where(
            Booking.is_deleted == False
        )
        active_customers = (await session.execute(active_stmt)).scalar() or 0

        # New customers in range
        new_stmt = select(func.count(Customer.id)).where(
            and_(
                Customer.created_at >= datetime.combine(start_date, datetime.min.time()),
                Customer.created_at < datetime.combine(end_date + timedelta(days=1), datetime.min.time()),
                Customer.is_deleted == False
            )
        )
        new_customers = (await session.execute(new_stmt)).scalar() or 0

        # Total customer value (bookings)
        value_stmt = select(func.sum(Booking.booking_amount)).where(Booking.is_deleted == False)
        total_value = (await session.execute(value_stmt)).scalar() or Decimal(0)

        avg_value = (total_value / total_customers) if total_customers > 0 else Decimal(0)

        return CustomerAnalyticsReport(
            period_start=start_date,
            period_end=end_date,
            total_customers=total_customers,
            active_customers=active_customers,
            total_customer_value=total_value,
            average_customer_value=avg_value,
            repeat_customers=0,
            repeat_customer_rate=0,
            new_customers=new_customers,
            segments=[]
        )


class ActivityAnalyticsRepository(BaseRepository):
    """Analytics queries for activities."""

    async def get_activity_summary(
        self,
        session: AsyncSession,
        start_date: date,
        end_date: date
    ) -> ActivitySummary:
        """Get activity summary."""
        # Total activities
        total_stmt = select(func.count(Activity.id)).where(
            and_(
                Activity.created_at >= datetime.combine(start_date, datetime.min.time()),
                Activity.created_at < datetime.combine(end_date + timedelta(days=1), datetime.min.time())
            )
        )
        total_activities = (await session.execute(total_stmt)).scalar() or 0

        # By action
        action_stmt = select(
            Activity.action,
            func.count(Activity.id)
        ).group_by(Activity.action)
        by_action = dict((await session.execute(action_stmt)).all() or [])

        # By entity type
        entity_stmt = select(
            Activity.entity_type,
            func.count(Activity.id)
        ).group_by(Activity.entity_type)
        by_entity = dict((await session.execute(entity_stmt)).all() or [])

        # By user
        user_stmt = select(
            Activity.performed_by_user_id,
            func.count(Activity.id)
        ).group_by(Activity.performed_by_user_id)
        by_user = dict((await session.execute(user_stmt)).all() or [])

        return ActivitySummary(
            period_start=start_date,
            period_end=end_date,
            total_activities=total_activities,
            by_action=by_action,
            by_entity_type=by_entity,
            by_user={str(k): v for k, v in by_user.items() if k}
        )
