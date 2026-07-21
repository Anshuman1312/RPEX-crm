from datetime import date

from sqlalchemy import func, select, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.telecalling_call import TelecallingCall


class TelecallingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, payload: dict) -> TelecallingCall:
        row = TelecallingCall(**payload)
        self.db.add(row)
        await self.db.commit()
        await self.db.refresh(row)
        return row

    async def list_calls(self, limit: int = 100) -> list[TelecallingCall]:
        stmt = select(TelecallingCall).order_by(TelecallingCall.call_date.desc(), TelecallingCall.created_at.desc()).limit(limit)
        return list((await self.db.execute(stmt)).scalars().all())

    async def daily_summary(self, for_date):
    # Use 'case' instead of 'func.case'
        stmt = (
            select(
                TelecallingCall.telecaller_id,
                func.count(TelecallingCall.id).label("daily_calls"),
                func.sum(
                    case((TelecallingCall.status == "CONNECTED", 1), else_=0)
                ).label("connected"),
                func.sum(
                    case((TelecallingCall.status == "NOT_CONNECTED", 1), else_=0)
                ).label("not_connected"),
                func.sum(
                    case((TelecallingCall.status == "INTERESTED", 1), else_=0)
                ).label("interested"),
                func.sum(TelecallingCall.call_duration_sec).label("total_duration_sec"),
                func.max(TelecallingCall.daily_target).label("daily_target"),
            )
            .where(func.date(TelecallingCall.call_date) == for_date)
            .group_by(TelecallingCall.telecaller_id)
        )
        
        result = await self.db.execute(stmt)
        return result.all()