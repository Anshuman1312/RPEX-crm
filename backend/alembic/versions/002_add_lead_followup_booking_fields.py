"""Add enhanced lead, follow-up, and booking fields.

Revision ID: 002_add_lead_followup_booking_fields
Revises: 001_initial_schema
Create Date: 2026-08-01
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = "002_add_lead_followup_booking_fields"
down_revision = "001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add new fields to leads, followups, site_visits, and bookings tables."""
    
    # ── Leads table ────────────────────────────────────────────────────────────
    # Add client detail fields
    op.add_column("leads", sa.Column("title", sa.String(20), nullable=True))
    op.add_column("leads", sa.Column("alternate_phone", sa.String(20), nullable=True))
    op.add_column("leads", sa.Column("occupation", sa.String(100), nullable=True))
    op.add_column("leads", sa.Column("address", sa.Text(), nullable=True))
    
    # Add budget range fields
    op.add_column("leads", sa.Column("budget_min", sa.Integer(), nullable=True))
    op.add_column("leads", sa.Column("budget_max", sa.Integer(), nullable=True))
    
    # Add timeline and property fields
    op.add_column("leads", sa.Column("time_duration", sa.String(50), nullable=True))
    op.add_column("leads", sa.Column("purpose", sa.String(50), nullable=True))
    op.add_column("leads", sa.Column("property_type", sa.String(50), nullable=True))
    
    # ── FollowUps table ────────────────────────────────────────────────────────
    # Add follow-up mode/channel field
    op.add_column(
        "followups",
        sa.Column("mode", sa.String(50), nullable=True, index=True),
    )
    
    # ── SiteVisits table ───────────────────────────────────────────────────────
    # Add site visit tracking fields
    op.add_column(
        "site_visits",
        sa.Column("site_visit_scheduled", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "site_visits",
        sa.Column("site_visit_completed", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "site_visits",
        sa.Column("number_of_visitors", sa.Integer(), nullable=False, server_default="1"),
    )
    
    # ── Bookings table ────────────────────────────────────────────────────────
    # Add booking detail fields
    op.add_column(
        "bookings",
        sa.Column("booking_interested", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.add_column("bookings", sa.Column("preferred_payment_mode", sa.String(100), nullable=True))
    op.add_column(
        "bookings",
        sa.Column("finance_required", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "bookings",
        sa.Column("self_funding", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "bookings",
        sa.Column("loan_assistance_required", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    """Revert changes."""
    
    # ── Bookings table ────────────────────────────────────────────────────────
    op.drop_column("bookings", "loan_assistance_required")
    op.drop_column("bookings", "self_funding")
    op.drop_column("bookings", "finance_required")
    op.drop_column("bookings", "preferred_payment_mode")
    op.drop_column("bookings", "booking_interested")
    
    # ── SiteVisits table ───────────────────────────────────────────────────────
    op.drop_column("site_visits", "number_of_visitors")
    op.drop_column("site_visits", "site_visit_completed")
    op.drop_column("site_visits", "site_visit_scheduled")
    
    # ── FollowUps table ────────────────────────────────────────────────────────
    op.drop_column("followups", "mode")
    
    # ── Leads table ────────────────────────────────────────────────────────────
    op.drop_column("leads", "property_type")
    op.drop_column("leads", "purpose")
    op.drop_column("leads", "time_duration")
    op.drop_column("leads", "budget_max")
    op.drop_column("leads", "budget_min")
    op.drop_column("leads", "address")
    op.drop_column("leads", "occupation")
    op.drop_column("leads", "alternate_phone")
    op.drop_column("leads", "title")
