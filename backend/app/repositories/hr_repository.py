from __future__ import annotations

from uuid import UUID

from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.hr import HREmployee, HRRecord
from app.repositories.base import BaseRepository


class HRRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.employee_repo = BaseRepository(session, HREmployee)
        self.record_repo = BaseRepository(session, HRRecord)

    @staticmethod
    def _coerce_uuid(value: str | None) -> UUID | None:
        return UUID(str(value)) if value else None

    async def create_employee(self, payload: dict):
        return await self.employee_repo.create(
            user_id=self._coerce_uuid(payload.get("user_id")),
            full_name=payload["full_name"],
            department=payload.get("department"),
            designation=payload.get("designation"),
            salary=payload.get("salary"),
            incentives=payload.get("incentives"),
            performance_score=payload.get("performance_score"),
        )

    async def list_employees(self, limit: int = 100):
        query = (
            select(HREmployee)
            .where(HREmployee.is_deleted == False)
            .order_by(desc(HREmployee.created_at))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create_record(self, payload: dict):
        return await self.record_repo.create(
            employee_id=self._coerce_uuid(payload.get("employee_id")),
            record_type=payload["record_type"],
            record_date=payload["record_date"],
            status=payload.get("status", "ACTIVE"),
            details=payload.get("details") or {},
            notes=payload.get("notes"),
        )

    async def list_records(self, limit: int = 200):
        query = (
            select(HRRecord)
            .where(HRRecord.is_deleted == False)
            .order_by(desc(HRRecord.record_date), desc(HRRecord.created_at))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()
