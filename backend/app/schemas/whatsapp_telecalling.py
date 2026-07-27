"""
Schemas for WhatsApp messaging and telecalling operations.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


# ── WhatsApp Template ─────────────────────────────────────────────────

class WhatsAppTemplateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    language: str = Field("en", max_length=10)
    category: str = Field(..., pattern=r"^(MARKETING|UTILITY|AUTHENTICATION)$")
    header_text: Optional[str] = None
    body_text: str = Field(..., min_length=1)
    footer_text: Optional[str] = None
    buttons: List[dict] = Field(default_factory=list)


class WhatsAppTemplateResponse(BaseModel):
    id: UUID
    name: str
    language: str
    category: str
    header_text: Optional[str]
    body_text: str
    footer_text: Optional[str]
    buttons: List[dict]
    status: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── WhatsApp Interaction ──────────────────────────────────────────────

class WhatsAppSendRequest(BaseModel):
    """Send a WhatsApp message."""
    phone_number: str = Field(..., min_length=10, max_length=20)
    lead_id: Optional[UUID] = None
    customer_id: Optional[UUID] = None
    message_type: str = Field("TEXT", pattern=r"^(TEXT|TEMPLATE|IMAGE|DOCUMENT)$")
    message_body: Optional[str] = None
    template_id: Optional[UUID] = None
    template_variables: List[str] = Field(default_factory=list)
    media_url: Optional[str] = None


class WhatsAppWebhookPayload(BaseModel):
    """Inbound webhook from WhatsApp provider."""
    external_message_id: str
    phone_number: str
    direction: str = "INBOUND"
    message_type: str = "TEXT"
    message_body: Optional[str] = None
    media_url: Optional[str] = None
    received_at: Optional[datetime] = None


class WhatsAppStatusUpdate(BaseModel):
    """Delivery status update from provider webhook."""
    external_message_id: str
    status: str  # SENT, DELIVERED, READ, FAILED
    timestamp: Optional[datetime] = None
    error_message: Optional[str] = None


class WhatsAppInteractionResponse(BaseModel):
    id: UUID
    phone_number: str
    direction: str
    message_type: str
    message_body: Optional[str]
    status: str
    lead_id: Optional[UUID]
    customer_id: Optional[UUID]
    sent_by_user_id: Optional[UUID]
    template_id: Optional[UUID]
    external_message_id: Optional[str]
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    read_at: Optional[datetime]
    error_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class WhatsAppStats(BaseModel):
    total_sent: int
    total_received: int
    delivered_count: int
    read_count: int
    failed_count: int
    delivery_rate: float
    read_rate: float
    by_type: dict = Field(default_factory=dict)


# ── Telecalling Script ────────────────────────────────────────────────

class TelecallingScriptCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    purpose: str = Field(..., max_length=100)
    intro_text: str
    main_script: str
    objections: dict = Field(default_factory=dict)
    closing_text: Optional[str] = None


class TelecallingScriptResponse(BaseModel):
    id: UUID
    name: str
    purpose: str
    intro_text: str
    main_script: str
    objections: dict
    closing_text: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ── Telecalling Call ──────────────────────────────────────────────────

class TelecallingCallCreate(BaseModel):
    """Log a call (outbound initiated by agent)."""
    phone_number: str = Field(..., min_length=10, max_length=20)
    lead_id: Optional[UUID] = None
    customer_id: Optional[UUID] = None
    script_id: Optional[UUID] = None
    direction: str = Field("OUTBOUND", pattern=r"^(INBOUND|OUTBOUND)$")
    notes: Optional[str] = None


class TelecallingCallUpdate(BaseModel):
    """Update call with outcome after completion."""
    call_status: Optional[str] = None
    outcome: Optional[str] = None
    notes: Optional[str] = None
    duration_seconds: Optional[int] = None
    next_call_date: Optional[datetime] = None
    followup_required: Optional[bool] = None
    call_recording_url: Optional[str] = None
    answered_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None


class TelecallingCallResponse(BaseModel):
    id: UUID
    phone_number: str
    direction: str
    call_status: str
    lead_id: Optional[UUID]
    customer_id: Optional[UUID]
    agent_user_id: Optional[UUID]
    script_id: Optional[UUID]
    outcome: Optional[str]
    notes: Optional[str]
    duration_seconds: Optional[int]
    initiated_at: datetime
    answered_at: Optional[datetime]
    ended_at: Optional[datetime]
    next_call_date: Optional[datetime]
    followup_required: bool
    call_recording_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class TelecallingStats(BaseModel):
    total_calls: int
    outbound_calls: int
    inbound_calls: int
    answered_calls: int
    no_answer_calls: int
    average_duration_seconds: Optional[float]
    by_outcome: dict = Field(default_factory=dict)
    by_status: dict = Field(default_factory=dict)
    calls_requiring_followup: int
