"""initial schema

Revision ID: 0001_initial
Revises: None
Create Date: 2026-07-13
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_roles_name", "roles", ["name"], unique=True)

    op.create_table(
        "permissions",
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("module", sa.String(length=64), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_permissions_name", "permissions", ["name"], unique=True)
    op.create_index("ix_permissions_module", "permissions", ["module"], unique=False)

    op.create_table(
        "role_permissions",
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("permission_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["permission_id"], ["permissions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("role_id", "permission_id"),
    )

    op.create_table(
        "users",
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "websites",
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("domain", sa.String(length=255), nullable=False),
        sa.Column("api_key", sa.String(length=255), nullable=False),
        sa.Column("status", sa.Boolean(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_websites_domain", "websites", ["domain"], unique=True)
    op.create_index("ix_websites_api_key", "websites", ["api_key"], unique=True)

    op.create_table(
        "campaigns",
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("type", sa.String(length=64), nullable=False),
        sa.Column("platform", sa.String(length=64), nullable=False),
        sa.Column("budget", sa.Numeric(14, 2), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "lead_status",
        sa.Column("name", sa.String(length=32), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_lead_status_name", "lead_status", ["name"], unique=True)

    op.create_table(
        "leads",
        sa.Column("website_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=30), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=True),
        sa.Column("medium", sa.String(length=64), nullable=True),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("assigned_to", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("extra_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["assigned_to"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["website_id"], ["websites.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_leads_email", "leads", ["email"], unique=False)
    op.create_index("ix_leads_status", "leads", ["status"], unique=False)
    op.create_index("ix_leads_created_at", "leads", ["created_at"], unique=False)
    op.create_index("ix_leads_status_created_at", "leads", ["status", "created_at"], unique=False)
    op.create_index("ix_leads_campaign_created_at", "leads", ["campaign_id", "created_at"], unique=False)
    op.create_index("ix_leads_assigned_status", "leads", ["assigned_to", "status"], unique=False)
    op.create_index("ix_leads_campaign_id", "leads", ["campaign_id"], unique=False)
    op.create_index("ix_leads_assigned_to", "leads", ["assigned_to"], unique=False)
    op.create_index("ix_leads_extra_data_gin", "leads", ["extra_data"], unique=False, postgresql_using="gin")

    op.create_table(
        "lead_activity",
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("activity_type", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["lead_id"], ["leads.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "followups",
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("assigned_to", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("followup_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("remark", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["assigned_to"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["lead_id"], ["leads.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "seo_keywords",
        sa.Column("keyword", sa.String(length=255), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column("target_position", sa.Integer(), nullable=True),
        sa.Column("current_position", sa.Integer(), nullable=True),
        sa.Column("traffic", sa.Integer(), nullable=False),
        sa.Column("clicks", sa.Integer(), nullable=False),
        sa.Column("impressions", sa.Integer(), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "lead_saved_views",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("filters", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("is_public", sa.Boolean(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_lead_saved_views_user_id", "lead_saved_views", ["user_id"], unique=False)

    op.create_table(
        "audit_logs",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("module", sa.String(length=64), nullable=False),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("old_value", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("new_value", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_logs_module", "audit_logs", ["module"], unique=False)

    op.execute("INSERT INTO lead_status (id, name) VALUES (gen_random_uuid(), 'NEW'), (gen_random_uuid(), 'CONTACTED'), (gen_random_uuid(), 'FOLLOW_UP'), (gen_random_uuid(), 'DEMO'), (gen_random_uuid(), 'CONVERTED'), (gen_random_uuid(), 'LOST')")
    op.execute("INSERT INTO roles (id, name, description) VALUES (gen_random_uuid(), 'ADMIN', 'Full access'), (gen_random_uuid(), 'SEO_MANAGER', 'SEO operations'), (gen_random_uuid(), 'SALES', 'Lead follow-up and closure'), (gen_random_uuid(), 'ANALYST', 'Reporting and analytics')")
    op.execute(
        """
        INSERT INTO permissions (id, name, module, created_at, updated_at) VALUES
        (gen_random_uuid(), 'manage_users', 'users', now(), now()),
        (gen_random_uuid(), 'manage_websites', 'websites', now(), now()),
        (gen_random_uuid(), 'view_leads', 'leads', now(), now()),
        (gen_random_uuid(), 'edit_leads', 'leads', now(), now()),
        (gen_random_uuid(), 'manage_followups', 'followups', now(), now()),
        (gen_random_uuid(), 'view_analytics', 'analytics', now(), now()),
        (gen_random_uuid(), 'export_reports', 'reports', now(), now()),
        (gen_random_uuid(), 'schedule_reports', 'reports', now(), now()),
        (gen_random_uuid(), 'manage_campaigns', 'campaigns', now(), now()),
        (gen_random_uuid(), 'manage_keywords', 'keywords', now(), now())
        """
    )
    op.execute(
        """
        INSERT INTO role_permissions (role_id, permission_id)
        SELECT r.id, p.id
        FROM roles r
        JOIN permissions p ON p.name IN (
            'manage_users', 'manage_websites', 'view_leads', 'edit_leads', 'manage_followups',
            'view_analytics', 'export_reports', 'schedule_reports', 'manage_campaigns', 'manage_keywords'
        )
        WHERE r.name = 'ADMIN'
        """
    )
    op.execute(
        """
        INSERT INTO role_permissions (role_id, permission_id)
        SELECT r.id, p.id
        FROM roles r
        JOIN permissions p ON p.name IN ('view_leads', 'manage_campaigns', 'manage_keywords', 'view_analytics', 'manage_websites')
        WHERE r.name = 'SEO_MANAGER'
        """
    )
    op.execute(
        """
        INSERT INTO role_permissions (role_id, permission_id)
        SELECT r.id, p.id
        FROM roles r
        JOIN permissions p ON p.name IN ('view_leads', 'edit_leads', 'manage_followups')
        WHERE r.name = 'SALES'
        """
    )
    op.execute(
        """
        INSERT INTO role_permissions (role_id, permission_id)
        SELECT r.id, p.id
        FROM roles r
        JOIN permissions p ON p.name IN ('view_leads', 'view_analytics', 'export_reports', 'schedule_reports')
        WHERE r.name = 'ANALYST'
        """
    )


def downgrade() -> None:
    op.drop_index("ix_audit_logs_module", table_name="audit_logs")
    op.drop_table("audit_logs")
    op.drop_index("ix_lead_saved_views_user_id", table_name="lead_saved_views")
    op.drop_table("lead_saved_views")
    op.drop_table("seo_keywords")
    op.drop_table("followups")
    op.drop_table("lead_activity")
    op.drop_index("ix_leads_extra_data_gin", table_name="leads")
    op.drop_index("ix_leads_assigned_status", table_name="leads")
    op.drop_index("ix_leads_campaign_created_at", table_name="leads")
    op.drop_index("ix_leads_status_created_at", table_name="leads")
    op.drop_index("ix_leads_assigned_to", table_name="leads")
    op.drop_index("ix_leads_campaign_id", table_name="leads")
    op.drop_index("ix_leads_created_at", table_name="leads")
    op.drop_index("ix_leads_status", table_name="leads")
    op.drop_index("ix_leads_email", table_name="leads")
    op.drop_table("leads")
    op.drop_index("ix_lead_status_name", table_name="lead_status")
    op.drop_table("lead_status")
    op.drop_table("campaigns")
    op.drop_index("ix_websites_api_key", table_name="websites")
    op.drop_index("ix_websites_domain", table_name="websites")
    op.drop_table("websites")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    op.drop_table("role_permissions")
    op.drop_index("ix_permissions_module", table_name="permissions")
    op.drop_index("ix_permissions_name", table_name="permissions")
    op.drop_table("permissions")
    op.drop_index("ix_roles_name", table_name="roles")
    op.drop_table("roles")
