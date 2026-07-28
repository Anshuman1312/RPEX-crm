from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from sqlalchemy import Date, and_, case, cast, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.whatsapp_telecalling import TelecallingCall
from app.repositories.base import BaseRepository


class TelecallingRepository(BaseRepository[TelecallingCall]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, TelecallingCall)

    @staticmethod
    def _coerce_uuid(value: str | None) -> UUID | None:
        return UUID(str(value)) if value else None

    @staticmethod
    def _normalize(row: TelecallingCall) -> TelecallingCall:
        row.call_date = getattr(row, "call_date", None) or row.initiated_at
        row.telecaller_id = getattr(row, "telecaller_id", None) or row.agent_user_id
        row.customer_name = getattr(row, "customer_name", None) or ""
        row.status = getattr(row, "status", None) or row.call_status
        row.call_duration_sec = getattr(row, "call_duration_sec", None) or row.duration_seconds or 0
        row.daily_target = getattr(row, "daily_target", None) or 0
        return row

    async def create_call(self, payload: dict) -> TelecallingCall:
        row = await super().create(
            lead_id=self._coerce_uuid(payload.get("lead_id")),
            customer_id=self._coerce_uuid(payload.get("customer_id")),
            agent_user_id=self._coerce_uuid(payload.get("telecaller_id")),
            phone_number=payload.get("phone") or payload.get("phone_number") or "",
            direction=payload.get("direction") or "OUTBOUND",
            call_status=payload.get("status") or "INITIATED",
            initiated_at=payload.get("call_date") or datetime.utcnow(),
            duration_seconds=payload.get("call_duration_sec"),
            call_recording_url=payload.get("call_recording_url"),
            notes=payload.get("notes"),
        )
        row.customer_name = payload.get("customer_name") or ""
        row.daily_target = payload.get("daily_target") or 0
        return self._normalize(row)

    async def list_calls(self, limit: int = 100) -> list[TelecallingCall]:
        query = select(self.model).where(self.model.is_deleted == False).order_by(desc(self.model.initiated_at), desc(self.model.created_at)).limit(limit)
        result = await self.session.execute(query)
        return [self._normalize(row) for row in result.scalars().all()]

    async def daily_summary(self, report_date: date):
        day_col = cast(self.model.initiated_at, Date)
        query = (
            select(
                self.model.agent_user_id.label("telecaller_id"),
                func.count(self.model.id).label("daily_calls"),
                func.sum(case((self.model.call_status.in_(["ANSWERED", "COMPLETED"]), 1), else_=0)).label("connected"),
                func.sum(case((self.model.call_status.in_(["NO_ANSWER", "BUSY", "FAILED"]), 1), else_=0)).label("not_connected"),
                func.sum(case((self.model.outcome == "INTERESTED", 1), else_=0)).label("interested"),
                func.coalesce(func.sum(self.model.duration_seconds), 0).label("total_duration_sec"),
                func.max(case((self.model.id.isnot(None), 0), else_=0)).label("daily_target"),
            )
            .where(and_(day_col == report_date, self.model.is_deleted == False, self.model.agent_user_id.isnot(None)))
            .group_by(self.model.agent_user_id)
        )
        result = await self.session.execute(query)
        return result.all()
