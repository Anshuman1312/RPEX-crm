from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser, require_permissions
from app.core.permissions import PERMISSIONS
from app.database.postgres import get_db
from app.models.campaign import Campaign
from app.models.finance_ledger_entry import FinanceLedgerEntry
from app.models.hr_employee import HREmployee
from app.models.inventory_unit import InventoryUnit
from app.models.lead import Lead
from app.models.booking import Booking
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


@router.get("/summary", dependencies=[Depends(require_permissions({PERMISSIONS.EXPORT_REPORTS}))])
async def report_summary(_: CurrentUser, db: AsyncSession = Depends(get_db), period: str = "daily"):
    sales = (await db.execute(select(func.coalesce(func.sum(Booking.booking_value), 0)).select_from(Booking))).scalar_one()
    leads = (await db.execute(select(func.count()).select_from(Lead))).scalar_one()
    campaigns = (await db.execute(select(func.count()).select_from(Campaign))).scalar_one()
    inventory_total = (await db.execute(select(func.count()).select_from(InventoryUnit))).scalar_one()
    inventory_sold = (
        await db.execute(select(func.count()).select_from(InventoryUnit).where(InventoryUnit.booking_status.in_(["BOOKED", "SOLD"])))
    ).scalar_one()
    employee_total = (await db.execute(select(func.count()).select_from(HREmployee))).scalar_one()

    receipts = (
        await db.execute(select(func.coalesce(func.sum(FinanceLedgerEntry.amount), 0)).where(FinanceLedgerEntry.entry_type == "RECEIPT"))
    ).scalar_one()
    expenses = (
        await db.execute(
            select(func.coalesce(func.sum(FinanceLedgerEntry.amount), 0)).where(
                FinanceLedgerEntry.entry_type.in_(["DEVELOPER_PAYMENT", "MARKETING_EXPENSE", "COMMISSION", "VENDOR_PAYMENT", "GST"])
            )
        )
    ).scalar_one()
    profit = float(receipts) - float(expenses)

    return {
        "period": period,
        "daily_report": {"sales_report": float(sales), "lead_report": int(leads)},
        "weekly_report": {"campaign_report": int(campaigns), "inventory_report": {"total": int(inventory_total), "sold": int(inventory_sold)}},
        "monthly_report": {"profit_report": round(float(profit), 2), "employee_report": int(employee_total)},
    }
