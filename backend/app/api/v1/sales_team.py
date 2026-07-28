from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser, require_permissions
from app.core.permissions import PERMISSIONS
from app.database.postgres import get_db
from app.repositories.sales_team_repository import SalesTeamRepository
from app.schemas.sales_team import SalesTeamReportCreate
from app.services.sales_team_service import SalesTeamService

router = APIRouter()


@router.post("/reports", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_SALES_TEAM}))])
async def create_sales_team_report(payload: SalesTeamReportCreate, _: CurrentUser, db: AsyncSession = Depends(get_db)):
    row = await SalesTeamService(SalesTeamRepository(db)).create_report(payload.model_dump())
    return {
        "id": str(row.id),
        "report_date": row.report_date,
        "sales_executive_name": row.sales_executive_name,
    }


@router.get("/reports", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_SALES_TEAM}))])
async def list_sales_team_reports(_: CurrentUser, db: AsyncSession = Depends(get_db), limit: int = Query(default=100, ge=1, le=500)):
    rows = await SalesTeamRepository(db).list_reports(limit=limit)
    return [
        {
            "id": str(row.id),
            "report_date": row.report_date,
            "sales_executive_id": str(row.sales_executive_id),
            "sales_executive_name": row.sales_executive_name,
            "target_value": row.target_value,
            "achieved_sales_value": row.achieved_sales_value,
            "bookings_count": row.bookings_count,
            "commission_value": row.commission_value,
            "site_visits_count": row.site_visits_count,
            "attendance_status": row.attendance_status,
            "daily_report": row.daily_report,
            "created_at": row.created_at,
        }
        for row in rows
    ]


@router.get("/leaderboard", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_SALES_TEAM}))])
async def sales_team_leaderboard(_: CurrentUser, db: AsyncSession = Depends(get_db), limit: int = Query(default=20, ge=1, le=100)):
    rows = await SalesTeamRepository(db).list_reports(limit=500)
    by_exec: dict[str, dict] = {}
    for row in rows:
        key = str(row.sales_executive_id)
        current = by_exec.get(
            key,
            {
                "sales_executive_id": key,
                "sales_executive_name": row.sales_executive_name,
                "target_value": 0.0,
                "achieved_sales_value": 0.0,
                "bookings_count": 0,
                "commission_value": 0.0,
                "site_visits_count": 0,
                "present_days": 0,
            },
        )
        current["target_value"] += float(row.target_value or 0)
        current["achieved_sales_value"] += float(row.achieved_sales_value or 0)
        current["bookings_count"] += int(row.bookings_count or 0)
        current["commission_value"] += float(row.commission_value or 0)
        current["site_visits_count"] += int(row.site_visits_count or 0)
        if row.attendance_status == "PRESENT":
            current["present_days"] += 1
        by_exec[key] = current

    leaderboard = list(by_exec.values())
    for item in leaderboard:
        target = item["target_value"]
        achieved = item["achieved_sales_value"]
        item["achievement_percent"] = round((achieved / target) * 100, 2) if target else 0

    leaderboard.sort(key=lambda x: (x["achieved_sales_value"], x["bookings_count"]), reverse=True)
    return leaderboard[:limit]
