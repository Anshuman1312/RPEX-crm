from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.approval_request import ApprovalRequest


class ApprovalRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, payload: dict[str, Any]) -> ApprovalRequest:
        row = ApprovalRequest(**payload)
        self.db.add(row)
        await self.db.commit()
        await self.db.refresh(row)
        return row

    async def list_requests(self, status: str | None = None, limit: int = 100) -> list[ApprovalRequest]:
        stmt = select(ApprovalRequest)
        if status:
            stmt = stmt.where(ApprovalRequest.status == status)
        stmt = stmt.order_by(ApprovalRequest.created_at.desc()).limit(limit)
        return list((await self.db.execute(stmt)).scalars().all())

    async def get_by_id(self, request_id: str) -> ApprovalRequest | None:
        return await self.db.get(ApprovalRequest, request_id)

    async def update_status(self, row: ApprovalRequest, status: str, approver_id: str | None = None) -> ApprovalRequest:
        row.status = status
        if approver_id:
            row.approver_id = approver_id
        await self.db.commit()
        await self.db.refresh(row)
        return row
