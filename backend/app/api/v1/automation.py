from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import CurrentUser, require_permissions
from app.core.permissions import PERMISSIONS
from app.workers import celery_tasks

router = APIRouter()

WORKFLOW_TASKS = {
    "auto_lead_assignment": celery_tasks.auto_assign_new_leads,
    "duplicate_lead_detection": celery_tasks.detect_duplicate_leads,
    "missed_followup_alerts": celery_tasks.send_missed_followup_alerts,
    "whatsapp_reminders": celery_tasks.send_whatsapp_reminders,
    "email_automation": celery_tasks.run_email_automation,
    "booking_confirmation": celery_tasks.send_booking_confirmations,
    "invoice_generation": celery_tasks.auto_generate_invoices,
    "payment_reminders": celery_tasks.send_payment_reminders,
    "anniversary_birthday_wishes": celery_tasks.send_anniversary_birthday_wishes,
    "daily_performance_reports": celery_tasks.generate_daily_performance_report,
    "manager_approval_workflow": celery_tasks.calculate_commissions,
    "commission_calculation": celery_tasks.calculate_commissions,
    "lead_scoring_ai": celery_tasks.refresh_ai_lead_scoring,
}


@router.get("/workflows", dependencies=[Depends(require_permissions({PERMISSIONS.SCHEDULE_REPORTS}))])
async def list_workflows(_: CurrentUser):
    return {
        "workflows": sorted(WORKFLOW_TASKS.keys()),
        "note": "Use POST /automation/run/{workflow_name} to enqueue a workflow.",
    }


@router.post("/run/{workflow_name}", dependencies=[Depends(require_permissions({PERMISSIONS.SCHEDULE_REPORTS}))])
async def run_workflow(workflow_name: str, _: CurrentUser):
    task_fn = WORKFLOW_TASKS.get(workflow_name)
    if not task_fn:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown workflow '{workflow_name}'",
        )

    task = task_fn.delay()
    return {"workflow": workflow_name, "task_id": task.id, "status": "queued"}
