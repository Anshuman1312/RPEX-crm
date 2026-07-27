"""
Service layer for reports and analytics operations.

Orchestrates report generation, caching, and KPI calculations.
"""

from __future__ import annotations

from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.analytics_repository import (
    LeadAnalyticsRepository, BookingAnalyticsRepository,
    RevenueAnalyticsRepository, TeamPerformanceRepository,
    ProjectAnalyticsRepository, CustomerAnalyticsRepository,
    ActivityAnalyticsRepository
)
from app.schemas.report import (
    LeadMetricsReport, BookingMetricsReport, RevenueAnalyticsReport,
    TeamPerformanceReport, ProjectAnalyticsReport, CustomerAnalyticsReport,
    SalesPipelineReport, ActivitySummary, DashboardMetrics, PaymentAnalytics,
    LeadConversionFunnel, PeriodComparison, ComparisonReport, KPISummary,
    DateRangeFilter
)


class ReportService:
    """Service for generating reports and analytics."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.lead_repo = LeadAnalyticsRepository()
        self.booking_repo = BookingAnalyticsRepository()
        self.revenue_repo = RevenueAnalyticsRepository()
        self.team_repo = TeamPerformanceRepository()
        self.project_repo = ProjectAnalyticsRepository()
        self.customer_repo = CustomerAnalyticsRepository()
        self.activity_repo = ActivityAnalyticsRepository()

    # ── Lead Reports ──────────────────────────────────────────────────

    async def get_lead_metrics(
        self,
        start_date: date,
        end_date: date
    ) -> LeadMetricsReport:
        """Get lead metrics for date range."""
        return await self.lead_repo.get_lead_metrics(self.session, start_date, end_date)

    async def get_lead_conversion_funnel(self) -> LeadConversionFunnel:
        """Get lead conversion funnel."""
        return await self.lead_repo.get_lead_conversion_funnel(self.session)

    # ── Booking Reports ───────────────────────────────────────────────

    async def get_booking_metrics(
        self,
        start_date: date,
        end_date: date
    ) -> BookingMetricsReport:
        """Get booking metrics for date range."""
        return await self.booking_repo.get_booking_metrics(self.session, start_date, end_date)

    # ── Revenue Reports ───────────────────────────────────────────────

    async def get_revenue_analytics(
        self,
        start_date: date,
        end_date: date
    ) -> RevenueAnalyticsReport:
        """Get revenue analytics for date range."""
        return await self.revenue_repo.get_revenue_analytics(self.session, start_date, end_date)

    async def get_payment_analytics(self) -> PaymentAnalytics:
        """Get payment analytics."""
        return await self.revenue_repo.get_payment_analytics(self.session)

    # ── Team Performance Reports ──────────────────────────────────────

    async def get_team_performance(
        self,
        start_date: date,
        end_date: date
    ) -> TeamPerformanceReport:
        """Get team performance metrics."""
        return await self.team_repo.get_team_performance(self.session, start_date, end_date)

    # ── Project Reports ───────────────────────────────────────────────

    async def get_project_analytics(
        self,
        start_date: date,
        end_date: date
    ) -> ProjectAnalyticsReport:
        """Get project-wise analytics."""
        return await self.project_repo.get_project_analytics(self.session, start_date, end_date)

    # ── Customer Reports ──────────────────────────────────────────────

    async def get_customer_analytics(
        self,
        start_date: date,
        end_date: date
    ) -> CustomerAnalyticsReport:
        """Get customer analytics."""
        return await self.customer_repo.get_customer_analytics(self.session, start_date, end_date)

    # ── Activity Reports ──────────────────────────────────────────────

    async def get_activity_summary(
        self,
        start_date: date,
        end_date: date
    ) -> ActivitySummary:
        """Get activity summary."""
        return await self.activity_repo.get_activity_summary(self.session, start_date, end_date)

    # ── Dashboard Metrics ─────────────────────────────────────────────

    async def get_dashboard_metrics(
        self,
        period: str = "this_month"
    ) -> DashboardMetrics:
        """Get key metrics for dashboard.
        
        Period: today, this_week, this_month, this_quarter, this_year
        """
        start_date, end_date = self._get_period_dates(period)

        # Get all reports in parallel
        lead_metrics = await self.get_lead_metrics(start_date, end_date)
        booking_metrics = await self.get_booking_metrics(start_date, end_date)
        revenue_analytics = await self.get_revenue_analytics(start_date, end_date)
        team_perf = await self.get_team_performance(start_date, end_date)

        return DashboardMetrics(
            period=period,
            total_leads=lead_metrics.total_leads,
            new_leads=lead_metrics.new_leads_count,
            qualified_leads=lead_metrics.by_status.get("QUALIFIED", 0),
            total_bookings=booking_metrics.total_bookings,
            total_booking_value=booking_metrics.total_booking_value,
            total_invoiced=revenue_analytics.total_invoiced,
            total_collected=revenue_analytics.total_paid,
            pending_amount=revenue_analytics.total_pending,
            overdue_amount=revenue_analytics.total_overdue,
            active_team_members=team_perf.total_team_members,
            top_performer_name=(
                team_perf.team_members[0].full_name
                if team_perf.team_members
                else None
            ),
            generated_at=datetime.now()
        )

    # ── Comparison Reports ────────────────────────────────────────────

    async def get_comparison_report(
        self,
        current_period: str,
        previous_period: str
    ) -> ComparisonReport:
        """Get period-over-period comparison.
        
        Period strings: today, this_week, this_month, this_quarter, this_year
        """
        current_start, current_end = self._get_period_dates(current_period)
        prev_start, prev_end = self._get_period_dates(previous_period)

        # Get metrics for both periods
        curr_leads = await self.get_lead_metrics(current_start, current_end)
        prev_leads = await self.get_lead_metrics(prev_start, prev_end)

        curr_bookings = await self.get_booking_metrics(current_start, current_end)
        prev_bookings = await self.get_booking_metrics(prev_start, prev_end)

        curr_revenue = await self.get_revenue_analytics(current_start, current_end)
        prev_revenue = await self.get_revenue_analytics(prev_start, prev_end)

        # Calculate comparisons
        leads_comp = self._calculate_comparison(
            float(curr_leads.conversion_rate),
            float(prev_leads.conversion_rate)
        )

        bookings_comp = self._calculate_comparison(
            float(curr_bookings.total_booking_value or 0),
            float(prev_bookings.total_booking_value or 0)
        )

        revenue_comp = self._calculate_comparison(
            float(curr_revenue.total_paid or 0),
            float(prev_revenue.total_paid or 0)
        )

        conversion_comp = self._calculate_comparison(
            float(curr_leads.conversion_rate),
            float(prev_leads.conversion_rate)
        )

        return ComparisonReport(
            current_period=current_period,
            previous_period=previous_period,
            leads=leads_comp,
            bookings=bookings_comp,
            revenue=revenue_comp,
            conversion_rate=conversion_comp
        )

    # ── KPI Summary ───────────────────────────────────────────────────

    async def get_kpi_summary(
        self,
        start_date: date,
        end_date: date
    ) -> KPISummary:
        """Get key performance indicators summary."""
        lead_metrics = await self.get_lead_metrics(start_date, end_date)
        booking_metrics = await self.get_booking_metrics(start_date, end_date)
        revenue_analytics = await self.get_revenue_analytics(start_date, end_date)

        return KPISummary(
            period_start=start_date,
            period_end=end_date,
            lead_conversion_rate=lead_metrics.conversion_rate,
            lead_loss_rate=lead_metrics.loss_rate,
            average_lead_age_days=None,
            booking_conversion_rate=(
                (booking_metrics.confirmed_count / booking_metrics.total_bookings * 100)
                if booking_metrics.total_bookings > 0
                else 0
            ),
            booking_cancellation_rate=booking_metrics.cancellation_rate,
            average_booking_value=booking_metrics.average_booking_value,
            revenue_collection_rate=revenue_analytics.collection_rate,
            days_sales_outstanding=None,
            task_completion_rate=0,
            customer_satisfaction_score=None
        )

    # ── Helper Methods ────────────────────────────────────────────────

    def _get_period_dates(self, period: str) -> tuple[date, date]:
        """Get start and end dates for period string."""
        today = date.today()

        if period == "today":
            return today, today
        elif period == "this_week":
            start = today - timedelta(days=today.weekday())
            return start, today
        elif period == "this_month":
            start = today.replace(day=1)
            return start, today
        elif period == "this_quarter":
            quarter_start_month = ((today.month - 1) // 3) * 3 + 1
            start = today.replace(month=quarter_start_month, day=1)
            return start, today
        elif period == "this_year":
            start = today.replace(month=1, day=1)
            return start, today
        else:
            # Default to this month
            start = today.replace(day=1)
            return start, today

    def _calculate_comparison(
        self,
        current_value: float,
        previous_value: float
    ) -> PeriodComparison:
        """Calculate period-over-period comparison."""
        change_amount = current_value - previous_value
        change_percentage = (
            (change_amount / previous_value * 100)
            if previous_value != 0
            else 0
        )

        if change_amount > 0:
            trend = "up"
        elif change_amount < 0:
            trend = "down"
        else:
            trend = "stable"

        return PeriodComparison(
            current_period_value=current_value,
            previous_period_value=previous_value,
            change_amount=change_amount,
            change_percentage=change_percentage,
            trend=trend
        )


class CacheableReportService(ReportService):
    """Report service with caching support (placeholder for future cache integration)."""

    async def get_cached_metrics(
        self,
        report_type: str,
        cache_key: str,
        ttl_minutes: int = 60
    ):
        """Get cached metrics or generate if not cached."""
        # TODO: Implement Redis/cache integration
        # For now, just return generated metrics
        pass

    def invalidate_cache(self, pattern: str = "*") -> int:
        """Invalidate cache entries matching pattern."""
        # TODO: Implement cache invalidation
        return 0
