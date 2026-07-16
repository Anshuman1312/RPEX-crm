from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser, require_permissions
from app.core.permissions import PERMISSIONS
from app.database.postgres import get_db
from app.models.user import User
from app.repositories.telecalling_repository import TelecallingRepository
from app.schemas.telecalling import TelecallingCallCreate
from app.services.telecalling_service import TelecallingService

router = APIRouter()


@router.post("/calls", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_TELECALLING}))])
async def create_call(payload: TelecallingCallCreate, _: CurrentUser, db: AsyncSession = Depends(get_db)):
    row = await TelecallingService(TelecallingRepository(db)).create_call(payload.model_dump())
    return {
        "id": str(row.id),
        "call_date": row.call_date,
        "customer_name": row.customer_name,
        "status": row.status,
    }


@router.get("/calls", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_TELECALLING}))])
async def list_calls(_: CurrentUser, db: AsyncSession = Depends(get_db), limit: int = Query(default=100, ge=1, le=500)):
    rows = await TelecallingRepository(db).list_calls(limit=limit)
    return [
        {
            "id": str(row.id),
            "call_date": row.call_date,
            "telecaller_id": str(row.telecaller_id),
            "lead_id": str(row.lead_id) if row.lead_id else None,
            "customer_name": row.customer_name,
            "status": row.status,
            "call_duration_sec": row.call_duration_sec,
            "call_recording_url": row.call_recording_url,
            "daily_target": row.daily_target,
            "notes": row.notes,
            "created_at": row.created_at,
        }
        for row in rows
    ]


@router.get("/performance", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_TELECALLING}))])
async def telecalling_performance(
    _: CurrentUser,
    db: AsyncSession = Depends(get_db),
    for_date: date | None = None,
):
    report_date = for_date or datetime.now(timezone.utc).date()
    rows = await TelecallingRepository(db).daily_summary(report_date)
    user_ids = [row.telecaller_id for row in rows]
    user_names = {}
    if user_ids:
        users = (await db.execute(select(User.id, User.name).where(User.id.in_(user_ids)))).all()
        user_names = {str(user.id): user.name for user in users}

    return [
        {
            "telecaller_id": str(row.telecaller_id),
            "telecaller_name": user_names.get(str(row.telecaller_id), "Unknown"),
            "date": report_date,
            "daily_calls": int(row.daily_calls or 0),
            "connected": int(row.connected or 0),
            "not_connected": int(row.not_connected or 0),
            "interested": int(row.interested or 0),
            "total_duration_sec": int(row.total_duration_sec or 0),
            "daily_target": int(row.daily_target or 0),
            "performance_percent": round((int(row.daily_calls or 0) / int(row.daily_target or 1)) * 100, 2)
            if int(row.daily_target or 0)
            else 0,
        }
        for row in rows
    ]
