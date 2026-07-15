"""phase 2 core modules

Revision ID: 0002_phase2_core
Revises: 0001_initial
Create Date: 2026-07-15
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_phase2_core"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "approval_requests",
        sa.Column("module", sa.String(length=64), nullable=False),
        sa.Column("entity_type", sa.String(length=64), nullable=False),
        sa.Column("entity_id", sa.String(length=64), nullable=False),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("requested_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("approver_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["requested_by"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["approver_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_approval_requests_module", "approval_requests", ["module"], unique=False)
    op.create_index("ix_approval_requests_status", "approval_requests", ["status"], unique=False)
    op.create_index("ix_approval_requests_requested_by", "approval_requests", ["requested_by"], unique=False)
    op.create_index("ix_approval_requests_approver_id", "approval_requests", ["approver_id"], unique=False)

    op.create_table(
        "customers",
        sa.Column("full_name", sa.String(length=128), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=30), nullable=False),
        sa.Column("alternate_phone", sa.String(length=30), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("city", sa.String(length=64), nullable=True),
        sa.Column("state", sa.String(length=64), nullable=True),
        sa.Column("country", sa.String(length=64), nullable=True),
        sa.Column("pincode", sa.String(length=20), nullable=True),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("anniversary_date", sa.Date(), nullable=True),
        sa.Column("partner_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("extra_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["partner_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_customers_phone", "customers", ["phone"], unique=False)
    op.create_index("ix_customers_email", "customers", ["email"], unique=False)
    op.create_index("ix_customers_partner_user_id", "customers", ["partner_user_id"], unique=False)

    op.create_table(
        "bookings",
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_name", sa.String(length=128), nullable=False),
        sa.Column("unit_code", sa.String(length=64), nullable=True),
        sa.Column("booking_value", sa.Numeric(14, 2), nullable=False),
        sa.Column("booking_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("sales_executive_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("partner_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("extra_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["sales_executive_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["partner_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_bookings_customer_id", "bookings", ["customer_id"], unique=False)
    op.create_index("ix_bookings_sales_executive_id", "bookings", ["sales_executive_id"], unique=False)
    op.create_index("ix_bookings_partner_user_id", "bookings", ["partner_user_id"], unique=False)
    op.create_index("ix_bookings_status", "bookings", ["status"], unique=False)

    op.create_table(
        "customer_payments",
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("booking_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("payment_date", sa.Date(), nullable=False),
        sa.Column("payment_mode", sa.String(length=32), nullable=False),
        sa.Column("reference_no", sa.String(length=128), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("recorded_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("partner_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["recorded_by"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["partner_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_customer_payments_customer_id", "customer_payments", ["customer_id"], unique=False)
    op.create_index("ix_customer_payments_booking_id", "customer_payments", ["booking_id"], unique=False)
    op.create_index("ix_customer_payments_partner_user_id", "customer_payments", ["partner_user_id"], unique=False)
    op.create_index("ix_customer_payments_reference_no", "customer_payments", ["reference_no"], unique=False)
    op.create_index("ix_customer_payments_payment_date", "customer_payments", ["payment_date"], unique=False)

    op.create_table(
        "invoices",
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("booking_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("invoice_number", sa.String(length=64), nullable=False),
        sa.Column("invoice_date", sa.Date(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("gst_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("partner_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["partner_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_invoices_customer_id", "invoices", ["customer_id"], unique=False)
    op.create_index("ix_invoices_booking_id", "invoices", ["booking_id"], unique=False)
    op.create_index("ix_invoices_partner_user_id", "invoices", ["partner_user_id"], unique=False)
    op.create_index("ix_invoices_status", "invoices", ["status"], unique=False)
    op.create_index("ix_invoices_invoice_number", "invoices", ["invoice_number"], unique=True)

    op.create_table(
        "document_assets",
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("booking_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("storage_key", sa.String(length=512), nullable=False),
        sa.Column("content_type", sa.String(length=128), nullable=True),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("uploaded_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("partner_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("file_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["partner_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_document_assets_customer_id", "document_assets", ["customer_id"], unique=False)
    op.create_index("ix_document_assets_booking_id", "document_assets", ["booking_id"], unique=False)
    op.create_index("ix_document_assets_partner_user_id", "document_assets", ["partner_user_id"], unique=False)
    op.create_index("ix_document_assets_category", "document_assets", ["category"], unique=False)
    op.create_index("ix_document_assets_storage_key", "document_assets", ["storage_key"], unique=True)

    op.execute(
        """
        INSERT INTO roles (id, name, description, created_at, updated_at)
        VALUES
        (gen_random_uuid(), 'SUPER_ADMIN', 'RPEX management access', now(), now()),
        (gen_random_uuid(), 'DIRECTOR', 'Business oversight', now(), now()),
        (gen_random_uuid(), 'PROJECT_HEAD', 'Project-level operations', now(), now()),
        (gen_random_uuid(), 'MARKETING_MANAGER', 'Marketing operations', now(), now()),
        (gen_random_uuid(), 'SALES_MANAGER', 'Sales team leadership', now(), now()),
        (gen_random_uuid(), 'SALES_EXECUTIVE', 'Sales execution and bookings', now(), now()),
        (gen_random_uuid(), 'TELECALLER', 'Outbound calling operations', now(), now()),
        (gen_random_uuid(), 'CRM_EXECUTIVE', 'Customer profile and operations', now(), now()),
        (gen_random_uuid(), 'FINANCE', 'Finance operations', now(), now()),
        (gen_random_uuid(), 'LEGAL', 'Legal and document review', now(), now()),
        (gen_random_uuid(), 'HR', 'Human resources', now(), now()),
        (gen_random_uuid(), 'RECEPTIONIST', 'Front desk and lead intake', now(), now()),
        (gen_random_uuid(), 'CHANNEL_PARTNER', 'Partner portal access', now(), now()),
        (gen_random_uuid(), 'DEVELOPER', 'Limited developer access', now(), now()),
        (gen_random_uuid(), 'CUSTOMER_PORTAL', 'Customer self-service', now(), now())
        ON CONFLICT (name) DO NOTHING
        """
    )

    op.execute(
        """
        INSERT INTO permissions (id, name, module, created_at, updated_at)
        VALUES
        (gen_random_uuid(), 'manage_customers', 'customers', now(), now()),
        (gen_random_uuid(), 'manage_sales', 'sales', now(), now()),
        (gen_random_uuid(), 'manage_finance', 'finance', now(), now()),
        (gen_random_uuid(), 'manage_documents', 'documents', now(), now()),
        (gen_random_uuid(), 'access_partner_portal', 'partner', now(), now())
        ON CONFLICT (name) DO NOTHING
        """
    )

    op.execute(
        """
        INSERT INTO role_permissions (role_id, permission_id)
        SELECT r.id, p.id
        FROM roles r
        JOIN permissions p ON p.name = 'access_partner_portal'
        WHERE r.name = 'CHANNEL_PARTNER'
        ON CONFLICT DO NOTHING
        """
    )


def downgrade() -> None:
    op.drop_index("ix_approval_requests_approver_id", table_name="approval_requests")
    op.drop_index("ix_approval_requests_requested_by", table_name="approval_requests")
    op.drop_index("ix_approval_requests_status", table_name="approval_requests")
    op.drop_index("ix_approval_requests_module", table_name="approval_requests")
    op.drop_table("approval_requests")

    op.execute(
        """
        DELETE FROM role_permissions
        WHERE permission_id IN (
            SELECT id FROM permissions WHERE name IN (
                'manage_customers',
                'manage_sales',
                'manage_finance',
                'manage_documents',
                'access_partner_portal'
            )
        )
        """
    )

    op.execute(
        """
        DELETE FROM permissions
        WHERE name IN (
            'manage_customers',
            'manage_sales',
            'manage_finance',
            'manage_documents',
            'access_partner_portal'
        )
        """
    )

    op.execute(
        """
        DELETE FROM roles
        WHERE name IN (
            'SUPER_ADMIN',
            'DIRECTOR',
            'PROJECT_HEAD',
            'MARKETING_MANAGER',
            'SALES_MANAGER',
            'SALES_EXECUTIVE',
            'TELECALLER',
            'CRM_EXECUTIVE',
            'FINANCE',
            'LEGAL',
            'HR',
            'RECEPTIONIST',
            'CHANNEL_PARTNER',
            'DEVELOPER',
            'CUSTOMER_PORTAL'
        )
        """
    )

    op.drop_index("ix_document_assets_storage_key", table_name="document_assets")
    op.drop_index("ix_document_assets_category", table_name="document_assets")
    op.drop_index("ix_document_assets_partner_user_id", table_name="document_assets")
    op.drop_index("ix_document_assets_booking_id", table_name="document_assets")
    op.drop_index("ix_document_assets_customer_id", table_name="document_assets")
    op.drop_table("document_assets")

    op.drop_index("ix_invoices_invoice_number", table_name="invoices")
    op.drop_index("ix_invoices_status", table_name="invoices")
    op.drop_index("ix_invoices_partner_user_id", table_name="invoices")
    op.drop_index("ix_invoices_booking_id", table_name="invoices")
    op.drop_index("ix_invoices_customer_id", table_name="invoices")
    op.drop_table("invoices")

    op.drop_index("ix_customer_payments_payment_date", table_name="customer_payments")
    op.drop_index("ix_customer_payments_reference_no", table_name="customer_payments")
    op.drop_index("ix_customer_payments_partner_user_id", table_name="customer_payments")
    op.drop_index("ix_customer_payments_booking_id", table_name="customer_payments")
    op.drop_index("ix_customer_payments_customer_id", table_name="customer_payments")
    op.drop_table("customer_payments")

    op.drop_index("ix_bookings_status", table_name="bookings")
    op.drop_index("ix_bookings_partner_user_id", table_name="bookings")
    op.drop_index("ix_bookings_sales_executive_id", table_name="bookings")
    op.drop_index("ix_bookings_customer_id", table_name="bookings")
    op.drop_table("bookings")

    op.drop_index("ix_customers_partner_user_id", table_name="customers")
    op.drop_index("ix_customers_email", table_name="customers")
    op.drop_index("ix_customers_phone", table_name="customers")
    op.drop_table("customers")
