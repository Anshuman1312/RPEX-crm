from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.whatsapp_interaction import WhatsAppInteraction
from app.models.whatsapp_template import WhatsAppTemplate


class WhatsAppRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_template(self, payload: dict) -> WhatsAppTemplate:
        row = WhatsAppTemplate(**payload)
        self.db.add(row)
        await self.db.commit()
        await self.db.refresh(row)
        return row

    async def list_templates(self, limit: int = 200) -> list[WhatsAppTemplate]:
        stmt = select(WhatsAppTemplate).order_by(WhatsAppTemplate.created_at.desc()).limit(limit)
        return list((await self.db.execute(stmt)).scalars().all())

    async def create_interaction(self, payload: dict) -> WhatsAppInteraction:
        row = WhatsAppInteraction(**payload)
        self.db.add(row)
        await self.db.commit()
        await self.db.refresh(row)
        return row

    async def list_interactions(self, limit: int = 300) -> list[WhatsAppInteraction]:
        stmt = select(WhatsAppInteraction).order_by(WhatsAppInteraction.sent_at.desc()).limit(limit)
        return list((await self.db.execute(stmt)).scalars().all())
