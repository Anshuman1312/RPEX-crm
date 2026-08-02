"""Add remarks field to leads table.

Revision ID: 003_add_lead_remarks_field
Revises: 002
Create Date: 2026-08-02
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision: str = "003_add_lead_remarks_field"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add remarks column to leads table."""
    op.add_column("leads", sa.Column("remarks", sa.Text(), nullable=True))


def downgrade() -> None:
    """Drop remarks column from leads table."""
    op.drop_column("leads", "remarks")
