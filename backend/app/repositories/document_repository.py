from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document_asset import DocumentAsset


class DocumentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, payload: dict[str, Any]) -> DocumentAsset:
        row = DocumentAsset(**payload)
        self.db.add(row)
        await self.db.commit()
        await self.db.refresh(row)
        return row

    async def list_documents(
        self,
        customer_id: str | None = None,
        booking_id: str | None = None,
        limit: int = 100,
    ) -> list[DocumentAsset]:
        stmt = select(DocumentAsset)
        if customer_id:
            stmt = stmt.where(DocumentAsset.customer_id == customer_id)
        if booking_id:
            stmt = stmt.where(DocumentAsset.booking_id == booking_id)
        stmt = stmt.order_by(DocumentAsset.created_at.desc()).limit(limit)
        return list((await self.db.execute(stmt)).scalars().all())

    async def list_by_partner(self, partner_user_id: str, limit: int = 100) -> list[DocumentAsset]:
        stmt = (
            select(DocumentAsset)
            .where(DocumentAsset.partner_user_id == partner_user_id)
            .order_by(DocumentAsset.created_at.desc())
            .limit(limit)
        )
        return list((await self.db.execute(stmt)).scalars().all())

    async def get_by_id(self, document_id: str) -> DocumentAsset | None:
        return await self.db.get(DocumentAsset, document_id)
