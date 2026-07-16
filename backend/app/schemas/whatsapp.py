from datetime import datetime

from pydantic import BaseModel, Field


class WhatsAppTemplateCreate(BaseModel):
    name: str = Field(min_length=2, max_length=128)
    template_type: str = Field(default="AUTO_REPLY", max_length=32)
    body: str


class WhatsAppInteractionCreate(BaseModel):
    interaction_type: str = Field(max_length=32)
    phone: str = Field(min_length=7, max_length=20)
    message: str
    campaign_name: str | None = Field(default=None, max_length=128)
    direction: str = Field(default="OUTBOUND", max_length=16)
    sent_at: datetime
