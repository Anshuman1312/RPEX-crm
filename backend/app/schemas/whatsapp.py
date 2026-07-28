from __future__ import annotations

from pydantic import BaseModel, Field


class WhatsAppTemplateCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    template_type: str = Field(default="UTILITY", max_length=50)
    language: str = Field(default="en", max_length=10)
    body: str = Field(min_length=1)
    header: str | None = None
    footer: str | None = None
    buttons: list[dict] = []


class WhatsAppInteractionCreate(BaseModel):
    interaction_type: str = Field(default="TEXT", max_length=20)
    phone: str = Field(min_length=5, max_length=20)
    message: str | None = None
    direction: str = Field(default="OUTBOUND", max_length=10)
    lead_id: str | None = None
    customer_id: str | None = None
    campaign_name: str | None = None
