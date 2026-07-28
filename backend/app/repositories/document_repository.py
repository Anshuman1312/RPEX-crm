from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import DocumentAsset
from app.repositories.base import BaseRepository


class DocumentRepository(BaseRepository[DocumentAsset]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, DocumentAsset)

    @staticmethod
    def _coerce_uuid(value: str | None) -> UUID | None:
        return UUID(str(value)) if value else None

    async def create_document(self, payload: dict[str, Any]) -> DocumentAsset:
        normalized = {
            **payload,
            "customer_id": self._coerce_uuid(payload.get("customer_id")),
            "booking_id": self._coerce_uuid(payload.get("booking_id")),
            "partner_user_id": self._coerce_uuid(payload.get("partner_user_id")),
            "uploaded_by": self._coerce_uuid(payload.get("uploaded_by")),
            "file_metadata": payload.get("file_metadata") or {},
        }
        return await super().create(**normalized)

    async def list_documents(
        self,
        customer_id: str | None = None,
        booking_id: str | None = None,
        limit: int = 100,
    ) -> list[DocumentAsset]:
        filters = [self.model.is_deleted == False]
        customer_uuid = self._coerce_uuid(customer_id)
        booking_uuid = self._coerce_uuid(booking_id)
        if customer_uuid:
            filters.append(self.model.customer_id == customer_uuid)
        if booking_uuid:
            filters.append(self.model.booking_id == booking_uuid)

        query = (
            select(self.model)
            .where(and_(*filters))
            .order_by(desc(self.model.created_at))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def list_by_partner(self, partner_user_id: str, limit: int = 100) -> list[DocumentAsset]:
        query = (
            select(self.model)
            .where(
                and_(
                    self.model.partner_user_id == self._coerce_uuid(partner_user_id),
                    self.model.is_deleted == False,
                )
            )
            .order_by(desc(self.model.created_at))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()
