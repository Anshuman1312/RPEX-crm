"""
Schemas for reports and analytics operations.

Includes: Lead metrics, booking metrics, revenue analytics, team performance, conversion funnels.
"""

from __future__ import annotations

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


# ── Date Range Filter ─────────────────────────────────────────────────

class DateRangeFilter(BaseModel):
    """Date range for filtering reports."""
    start_date: date
    end_date: date


# ── Lead Metrics ──────────────────────────────────────────────────────

class LeadMetric(BaseModel):
    """Lead metric data point."""
    date: date
    total_leads: int
    new_leads: int
    contacted_leads: int
    qualified_leads: int
    converted_leads: int
    lost_leads: int


class LeadMetricsReport(BaseModel):
    """Lead metrics over time period."""
    period_start: date
    period_end: date
    total_leads: int
    new_leads_count: int
    conversion_rate: float  # percentage
    loss_rate: float  # percentage
    average_time_to_conversion: Optional[float]  # days
    by_source: dict = Field(default_factory=dict)  # {source: count}
    by_status: dict = Field(default_factory=dict)  # {status: count}
    by_priority: dict = Field(default_factory=dict)  # {priority: count}
    daily_metrics: List[LeadMetric] = Field(default_factory=list)


class LeadConversionFunnel(BaseModel):
    """Lead conversion funnel."""
    new: int
    contacted: int
    qualified: int
    proposal_sent: int
    negotiation: int
    converted: int
    lost: int
    contact_rate: float
    qualification_rate: float
    proposal_rate: float
    conversion_rate: float


# ── Booking Metrics ───────────────────────────────────────────────────

class BookingMetric(BaseModel):
    """Booking metric data point."""
    date: date
    total_bookings: int
    new_bookings: int
    confirmed_bookings: int
    cancelled_bookings: int
    total_value: Decimal


class BookingMetricsReport(BaseModel):
    """Booking metrics over time period."""
    period_start: date
    period_end: date
    total_bookings: int
    confirmed_count: int
    cancelled_count: int
    total_booking_value: Decimal
    average_booking_value: Decimal
    cancellation_rate: float  # percentage
    by_status: dict = Field(default_factory=dict)  # {status: count}
    by_project: dict = Field(default_factory=dict)  # {project_id: count}
    daily_metrics: List[BookingMetric] = Field(default_factory=list)


# ── Revenue Analytics ─────────────────────────────────────────────────

class RevenueMetric(BaseModel):
    """Revenue metric data point."""
    date: date
    invoiced: Decimal
    paid: Decimal
    pending: Decimal
    overdue: Decimal


class RevenueAnalyticsReport(BaseModel):
    """Revenue analytics over time period."""
    period_start: date
    period_end: date
    total_invoiced: Decimal
    total_paid: Decimal
    total_pending: Decimal
    total_overdue: Decimal
    collection_rate: float  # percentage
    by_project: dict = Field(default_factory=dict)  # {project_id: amount}
    by_status: dict = Field(default_factory=dict)  # {status: amount}
    daily_metrics: List[RevenueMetric] = Field(default_factory=list)


class PaymentAnalytics(BaseModel):
    """Payment analytics."""
    total_invoices: int
    paid_invoices: int
    pending_invoices: int
    overdue_invoices: int
    partial_invoices: int
    total_amount: Decimal
    paid_amount: Decimal
    pending_amount: Decimal
    overdue_amount: Decimal
    average_payment_days: Optional[float]


# ── Team Performance ──────────────────────────────────────────────────

class TeamMemberPerformance(BaseModel):
    """Individual team member performance."""
    user_id: UUID
    full_name: str
    role: str
    leads_assigned: int
    leads_converted: int
    conversion_rate: float
    bookings_assigned: int
    booking_value: Decimal
    tasks_completed: int
    tasks_completion_rate: float


class TeamPerformanceReport(BaseModel):
    """Team performance metrics."""
    period_start: date
    period_end: date
    total_team_members: int
    total_leads_processed: int
    total_leads_converted: int
    total_bookings: int
    total_booking_value: Decimal
    average_conversion_rate: float
    team_members: List[TeamMemberPerformance] = Field(default_factory=list)


# ── Project Analytics ─────────────────────────────────────────────────

class ProjectSalesMetrics(BaseModel):
    """Sales metrics for a project."""
    project_id: UUID
    project_name: str
    total_units: int
    available_units: int
    booked_units: int
    sold_units: int
    booking_rate: float  # percentage
    sale_rate: float  # percentage
    total_booking_value: Decimal
    total_sale_value: Decimal


class ProjectAnalyticsReport(BaseModel):
    """Project-wise analytics."""
    period_start: date
    period_end: date
    total_projects: int
    total_units: int
    total_booked_units: int
    total_sold_units: int
    overall_booking_rate: float
    overall_sale_rate: float
    total_booking_value: Decimal
    total_sale_value: Decimal
    projects: List[ProjectSalesMetrics] = Field(default_factory=list)


# ── Customer Metrics ──────────────────────────────────────────────────

class CustomerSegment(BaseModel):
    """Customer segment metrics."""
    segment_name: str
    customer_count: int
    total_value: Decimal
    average_value: Decimal
    active_count: int


class CustomerAnalyticsReport(BaseModel):
    """Customer analytics."""
    period_start: date
    period_end: date
    total_customers: int
    active_customers: int
    total_customer_value: Decimal
    average_customer_value: Decimal
    repeat_customers: int
    repeat_customer_rate: float
    new_customers: int
    segments: List[CustomerSegment] = Field(default_factory=list)


# ── Sales Pipeline ────────────────────────────────────────────────────

class PipelineStage(BaseModel):
    """Sales pipeline stage."""
    stage_name: str
    lead_count: int
    total_value: Decimal
    average_value: Decimal
    days_in_stage: Optional[float]


class SalesPipelineReport(BaseModel):
    """Sales pipeline analysis."""
    as_of_date: date
    total_leads: int
    total_pipeline_value: Decimal
    stages: List[PipelineStage] = Field(default_factory=list)


# ── Activity Summary ──────────────────────────────────────────────────

class ActivitySummary(BaseModel):
    """Activity summary for a date range."""
    period_start: date
    period_end: date
    total_activities: int
    by_action: dict = Field(default_factory=dict)  # {action: count}
    by_entity_type: dict = Field(default_factory=dict)  # {entity_type: count}
    by_user: dict = Field(default_factory=dict)  # {user_id: count}


# ── Dashboard Data ────────────────────────────────────────────────────

class DashboardMetrics(BaseModel):
    """Key metrics for dashboard."""
    period: str  # "today", "this_week", "this_month", "this_quarter", "this_year"
    
    # Lead metrics
    total_leads: int
    new_leads: int
    qualified_leads: int
    
    # Booking metrics
    total_bookings: int
    total_booking_value: Decimal
    
    # Revenue metrics
    total_invoiced: Decimal
    total_collected: Decimal
    pending_amount: Decimal
    overdue_amount: Decimal
    
    # Team metrics
    active_team_members: int
    top_performer_name: Optional[str]
    
    # Generated at
    generated_at: datetime


# ── Export Request/Response ───────────────────────────────────────────

class ReportExportRequest(BaseModel):
    """Request to export report."""
    report_type: str  # lead_metrics, booking_metrics, revenue_analytics, etc.
    format: str = "csv"  # csv, json, pdf
    start_date: date
    end_date: date
    filters: Optional[dict] = None


class ReportExportResponse(BaseModel):
    """Response with export details."""
    export_id: str
    report_type: str
    format: str
    file_url: str
    generated_at: datetime
    expires_at: datetime


# ── Comparison Reports ────────────────────────────────────────────────

class PeriodComparison(BaseModel):
    """Period-over-period comparison."""
    current_period_value: float
    previous_period_value: float
    change_amount: float
    change_percentage: float
    trend: str  # up, down, stable


class ComparisonReport(BaseModel):
    """Comparison between two periods."""
    current_period: str
    previous_period: str
    leads: PeriodComparison
    bookings: PeriodComparison
    revenue: PeriodComparison
    conversion_rate: PeriodComparison


# ── KPI Summary ───────────────────────────────────────────────────────

class KPISummary(BaseModel):
    """Key Performance Indicators summary."""
    period_start: date
    period_end: date
    
    # Lead KPIs
    lead_conversion_rate: float
    lead_loss_rate: float
    average_lead_age_days: Optional[float]
    
    # Booking KPIs
    booking_conversion_rate: float
    booking_cancellation_rate: float
    average_booking_value: Decimal
    
    # Revenue KPIs
    revenue_collection_rate: float
    days_sales_outstanding: Optional[float]
    
    # Operational KPIs
    task_completion_rate: float
    customer_satisfaction_score: Optional[float]
