"""
API v1 routes for reports and analytics.

Endpoints: Lead metrics, booking metrics, revenue analytics, team performance,
customer analytics, project analytics, KPIs, dashboard metrics, comparisons.
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db_session
from app.dependencies.auth import get_current_user
from app.models import User
from app.schemas.report import (
    LeadMetricsReport, BookingMetricsReport, RevenueAnalyticsReport,
    TeamPerformanceReport, ProjectAnalyticsReport, CustomerAnalyticsReport,
    ActivitySummary, DashboardMetrics, PaymentAnalytics, LeadConversionFunnel,
    ComparisonReport, KPISummary
)
from app.services.report_service import ReportService
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(tags=["reports"])


# ── Lead Reports ──────────────────────────────────────────────────────

@router.get("/leads/metrics", response_model=LeadMetricsReport)
async def get_lead_metrics(
    start_date: date = Query(..., description="Start date for report"),
    end_date: date = Query(..., description="End date for report"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Get lead metrics for date range.
    
    Returns:
    - Total leads in period
    - New leads count
    - Conversion rate (%)
    - Loss rate (%)
    - By status breakdown
    - By source breakdown
    """
    service = ReportService(session)
    return await service.get_lead_metrics(start_date, end_date)


@router.get("/leads/funnel", response_model=LeadConversionFunnel)
async def get_lead_conversion_funnel(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Get lead conversion funnel.
    
    Returns funnel stages: new → contacted → qualified → converted/lost
    """
    service = ReportService(session)
    return await service.get_lead_conversion_funnel()


# ── Booking Reports ───────────────────────────────────────────────────

@router.get("/bookings/metrics", response_model=BookingMetricsReport)
async def get_booking_metrics(
    start_date: date = Query(..., description="Start date for report"),
    end_date: date = Query(..., description="End date for report"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Get booking metrics for date range.
    
    Returns:
    - Total bookings
    - Confirmed/cancelled counts
    - Booking values (total, average)
    - Cancellation rate (%)
    - By status breakdown
    """
    service = ReportService(session)
    return await service.get_booking_metrics(start_date, end_date)


# ── Revenue Reports ───────────────────────────────────────────────────

@router.get("/revenue/analytics", response_model=RevenueAnalyticsReport)
async def get_revenue_analytics(
    start_date: date = Query(..., description="Start date for report"),
    end_date: date = Query(..., description="End date for report"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Get revenue analytics for date range.
    
    Returns:
    - Total invoiced amount
    - Paid/pending/overdue amounts
    - Collection rate (%)
    - By project breakdown
    - By invoice status breakdown
    """
    service = ReportService(session)
    return await service.get_revenue_analytics(start_date, end_date)


@router.get("/revenue/payments", response_model=PaymentAnalytics)
async def get_payment_analytics(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Get payment analytics.
    
    Returns current state of invoices, amounts, and collection metrics.
    """
    service = ReportService(session)
    return await service.get_payment_analytics()


# ── Team Performance Reports ──────────────────────────────────────────

@router.get("/team/performance", response_model=TeamPerformanceReport)
async def get_team_performance(
    start_date: date = Query(..., description="Start date for report"),
    end_date: date = Query(..., description="End date for report"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Get team performance metrics.
    
    Returns:
    - Total team members
    - Leads processed/converted
    - Average conversion rate (%)
    - Individual member metrics
    """
    service = ReportService(session)
    return await service.get_team_performance(start_date, end_date)


# ── Project Reports ───────────────────────────────────────────────────

@router.get("/projects/analytics", response_model=ProjectAnalyticsReport)
async def get_project_analytics(
    start_date: date = Query(..., description="Start date for report"),
    end_date: date = Query(..., description="End date for report"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Get project-wise analytics.
    
    Returns:
    - Total projects, units
    - Booking/sale rates (%)
    - By project breakdown
    - Booking values
    """
    service = ReportService(session)
    return await service.get_project_analytics(start_date, end_date)


# ── Customer Reports ──────────────────────────────────────────────────

@router.get("/customers/analytics", response_model=CustomerAnalyticsReport)
async def get_customer_analytics(
    start_date: date = Query(..., description="Start date for report"),
    end_date: date = Query(..., description="End date for report"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Get customer analytics.
    
    Returns:
    - Total/active customers
    - Customer value metrics
    - Repeat customer rate (%)
    - New customers in period
    """
    service = ReportService(session)
    return await service.get_customer_analytics(start_date, end_date)


# ── Activity Reports ──────────────────────────────────────────────────

@router.get("/activities/summary", response_model=ActivitySummary)
async def get_activity_summary(
    start_date: date = Query(..., description="Start date for report"),
    end_date: date = Query(..., description="End date for report"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Get activity summary for date range.
    
    Returns:
    - Total activities
    - By action breakdown
    - By entity type breakdown
    - By user breakdown
    """
    service = ReportService(session)
    return await service.get_activity_summary(start_date, end_date)


# ── Dashboard ─────────────────────────────────────────────────────────

@router.get("/dashboard/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    period: str = Query(
        "this_month",
        description="Period: today, this_week, this_month, this_quarter, this_year"
    ),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Get key metrics for dashboard.
    
    Returns high-level KPIs for the selected period:
    - Lead metrics (total, new, qualified)
    - Booking metrics (total, value)
    - Revenue metrics (invoiced, collected, pending, overdue)
    - Team metrics (active members, top performer)
    """
    service = ReportService(session)
    return await service.get_dashboard_metrics(period)


# ── KPI Reports ───────────────────────────────────────────────────────

@router.get("/kpis/summary", response_model=KPISummary)
async def get_kpi_summary(
    start_date: date = Query(..., description="Start date for report"),
    end_date: date = Query(..., description="End date for report"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Get KPI summary for date range.
    
    Returns key performance indicators:
    - Lead conversion rate (%)
    - Lead loss rate (%)
    - Booking conversion rate (%)
    - Booking cancellation rate (%)
    - Revenue collection rate (%)
    - Task completion rate (%)
    """
    service = ReportService(session)
    return await service.get_kpi_summary(start_date, end_date)


# ── Comparison Reports ────────────────────────────────────────────────

@router.get("/comparison", response_model=ComparisonReport)
async def get_comparison_report(
    current_period: str = Query(
        "this_month",
        description="Current period: today, this_week, this_month, this_quarter, this_year"
    ),
    previous_period: str = Query(
        "this_month",
        description="Previous period: same options as current_period"
    ),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Get period-over-period comparison.
    
    Compares metrics between two time periods showing:
    - Change amount and percentage
    - Trend (up/down/stable)
    """
    service = ReportService(session)
    return await service.get_comparison_report(current_period, previous_period)


# ── Health Check ──────────────────────────────────────────────────────

@router.get("/health")
async def health_check(
    current_user: User = Depends(get_current_user)
):
    """Health check for reports service."""
    return {
        "status": "healthy",
        "service": "reports",
        "timestamp": str(date.today())
    }
