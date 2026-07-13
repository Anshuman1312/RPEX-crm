from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser, require_permissions
from app.core.permissions import PERMISSIONS
from app.database.postgres import get_db
from app.repositories.lead_repository import LeadRepository
from app.services.report_service import ReportService
from app.workers.celery_tasks import generate_daily_lead_report, generate_weekly_lead_report

router = APIRouter()


@router.get("/export/leads", dependencies=[Depends(require_permissions({PERMISSIONS.EXPORT_REPORTS}))])
async def export_leads(_: CurrentUser, db: AsyncSession = Depends(get_db), status: str | None = None):
    report_service = ReportService(LeadRepository(db))
    return StreamingResponse(
        report_service.leads_csv_chunk(status=status),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=leads_report.csv"},
    )


@router.post("/schedule/daily", dependencies=[Depends(require_permissions({PERMISSIONS.SCHEDULE_REPORTS}))])
async def schedule_daily_report(_: CurrentUser):
    task = generate_daily_lead_report.delay()
    return {"task_id": task.id, "status": "queued"}


@router.post("/schedule/weekly", dependencies=[Depends(require_permissions({PERMISSIONS.SCHEDULE_REPORTS}))])
async def schedule_weekly_report(_: CurrentUser):
    task = generate_weekly_lead_report.delay()
    return {"task_id": task.id, "status": "queued"}
