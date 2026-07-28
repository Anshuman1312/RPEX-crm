from __future__ import annotations

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.whatsapp_telecalling import WhatsAppInteraction, WhatsAppTemplate
from app.repositories.base import BaseRepository


class WhatsAppRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.template_repo = BaseRepository(session, WhatsAppTemplate)
        self.interaction_repo = BaseRepository(session, WhatsAppInteraction)

    @staticmethod
    def _normalize_interaction(row: WhatsAppInteraction) -> WhatsAppInteraction:
        row.interaction_type = getattr(row, "interaction_type", None) or row.message_type
        row.phone = getattr(row, "phone", None) or row.phone_number
        row.message = getattr(row, "message", None) or row.message_body
        row.campaign_name = getattr(row, "campaign_name", None)
        return row

    async def create_template(self, payload: dict) -> WhatsAppTemplate:
        return await self.template_repo.create(
            name=payload.get("name") or "",
            language=payload.get("language") or "en",
            category=payload.get("template_type") or payload.get("category") or "UTILITY",
            header_text=payload.get("header"),
            body_text=payload.get("body") or payload.get("body_text") or "",
            footer_text=payload.get("footer"),
            buttons=payload.get("buttons") or [],
            status=payload.get("status") or "APPROVED",
        )

    async def list_templates(self, limit: int = 200) -> list[WhatsAppTemplate]:
        query = select(WhatsAppTemplate).where(WhatsAppTemplate.is_deleted == False).order_by(desc(WhatsAppTemplate.created_at)).limit(limit)
        result = await self.session.execute(query)
        rows = result.scalars().all()
        for row in rows:
            row.template_type = getattr(row, "template_type", None) or row.category
            row.body = getattr(row, "body", None) or row.body_text
        return rows

    async def create_interaction(self, payload: dict) -> WhatsAppInteraction:
        row = await self.interaction_repo.create(
            lead_id=payload.get("lead_id"),
            customer_id=payload.get("customer_id"),
            sent_by_user_id=payload.get("sent_by_user_id"),
            template_id=payload.get("template_id"),
            phone_number=payload.get("phone") or payload.get("phone_number") or "",
            direction=payload.get("direction") or "OUTBOUND",
            message_type=payload.get("interaction_type") or payload.get("message_type") or "TEXT",
            message_body=payload.get("message"),
            status=payload.get("status") or "SENT",
        )
        return self._normalize_interaction(row)

    async def list_interactions(self, limit: int = 300) -> list[WhatsAppInteraction]:
        query = select(WhatsAppInteraction).where(WhatsAppInteraction.is_deleted == False).order_by(desc(WhatsAppInteraction.created_at)).limit(limit)
        result = await self.session.execute(query)
        return [self._normalize_interaction(row) for row in result.scalars().all()]
