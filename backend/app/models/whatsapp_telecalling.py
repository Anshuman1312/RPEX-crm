"""
WhatsApp and Telecalling models.

Models:
- WhatsAppTemplate: Approved message templates (HSM)
- WhatsAppInteraction: Individual messages sent/received
- TelecallingCall: Inbound/outbound call log
- TelecallingScript: Call scripts for agents
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import String, Integer, DateTime, ForeignKey, Boolean, Text, Numeric, JSON
from sqlalchemy import Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.mixins import BaseModelMixin, PrimaryKeyMixin, TimestampMixin, SoftDeleteMixin
from app.database.base import Base


# ── WhatsApp ──────────────────────────────────────────────────────────

class WhatsAppTemplate(Base, BaseModelMixin, PrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """
    Pre-approved HSM (Highly Structured Message) template.
    Used for outbound WhatsApp messages (business-initiated).
    """
    __tablename__ = "whatsapp_templates"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    language: Mapped[str] = mapped_column(String(10), nullable=False, default="en")
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    # MARKETING, UTILITY, AUTHENTICATION

    # Template body with {{1}}, {{2}} placeholders
    header_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    body_text: Mapped[str] = mapped_column(Text, nullable=False)
    footer_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    buttons: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    # Meta / approval status
    external_template_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="PENDING")
    # PENDING, APPROVED, REJECTED

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class WhatsAppInteraction(Base, BaseModelMixin, PrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """
    Individual WhatsApp message — inbound or outbound.
    """
    __tablename__ = "whatsapp_interactions"

    # Context
    lead_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("leads.id", ondelete="SET NULL"), nullable=True, index=True
    )
    customer_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("customers.id", ondelete="SET NULL"), nullable=True, index=True
    )
    sent_by_user_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    template_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("whatsapp_templates.id", ondelete="SET NULL"), nullable=True
    )

    # Message details
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    direction: Mapped[str] = mapped_column(String(10), nullable=False)  # INBOUND, OUTBOUND
    message_type: Mapped[str] = mapped_column(String(20), nullable=False, default="TEXT")
    # TEXT, IMAGE, DOCUMENT, AUDIO, VIDEO, TEMPLATE

    message_body: Mapped[str | None] = mapped_column(Text, nullable=True)
    media_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    template_variables: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    # Delivery tracking
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDING", index=True)
    # PENDING, SENT, DELIVERED, READ, FAILED
    external_message_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    lead = relationship("Lead", foreign_keys=[lead_id], viewonly=True)
    customer = relationship("Customer", foreign_keys=[customer_id], viewonly=True)
    sent_by = relationship("User", foreign_keys=[sent_by_user_id], viewonly=True)
    template = relationship("WhatsAppTemplate", foreign_keys=[template_id], viewonly=True)

    __table_args__ = (
        Index("ix_whatsapp_phone_direction", "phone_number", "direction"),
        Index("ix_whatsapp_lead_created", "lead_id", "created_at"),
    )


# ── Telecalling ───────────────────────────────────────────────────────

class TelecallingScript(Base, BaseModelMixin, PrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """
    Call script used by agents during telecalling.
    """
    __tablename__ = "telecalling_scripts"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    purpose: Mapped[str] = mapped_column(String(100), nullable=False)
    # COLD_CALL, FOLLOWUP, QUALIFICATION, CLOSING, etc.

    intro_text: Mapped[str] = mapped_column(Text, nullable=False)
    main_script: Mapped[str] = mapped_column(Text, nullable=False)
    objections: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    # {"objection": "response"} pairs
    closing_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by_user_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )


class TelecallingCall(Base, BaseModelMixin, PrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """
    Individual call log — inbound or outbound.
    """
    __tablename__ = "telecalling_calls"

    # Context
    lead_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("leads.id", ondelete="SET NULL"), nullable=True, index=True
    )
    customer_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("customers.id", ondelete="SET NULL"), nullable=True, index=True
    )
    agent_user_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    script_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("telecalling_scripts.id", ondelete="SET NULL"), nullable=True
    )

    # Call details
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    direction: Mapped[str] = mapped_column(String(10), nullable=False)  # INBOUND, OUTBOUND
    call_status: Mapped[str] = mapped_column(String(30), nullable=False, default="INITIATED", index=True)
    # INITIATED, RINGING, ANSWERED, NO_ANSWER, BUSY, FAILED, VOICEMAIL, COMPLETED

    # Timing
    initiated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    answered_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Outcome
    outcome: Mapped[str | None] = mapped_column(String(50), nullable=True)
    # INTERESTED, NOT_INTERESTED, CALLBACK, CONVERTED, DISCONNECTED, etc.
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    call_recording_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Next action
    next_call_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    followup_required: Mapped[bool] = mapped_column(Boolean, default=False)

    # External integration
    external_call_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)

    # Relationships
    lead = relationship("Lead", foreign_keys=[lead_id], viewonly=True)
    customer = relationship("Customer", foreign_keys=[customer_id], viewonly=True)
    agent = relationship("User", foreign_keys=[agent_user_id], viewonly=True)
    script = relationship("TelecallingScript", foreign_keys=[script_id], viewonly=True)

    __table_args__ = (
        Index("ix_call_agent_status", "agent_user_id", "call_status"),
        Index("ix_call_lead_created", "lead_id", "created_at"),
    )
