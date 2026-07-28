from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import CurrentUser, require_permissions
from app.core.permissions import PERMISSIONS
from app.workers import celery_tasks

router = APIRouter()

WORKFLOW_TASKS = {
    "auto_lead_assignment": getattr(celery_tasks, "auto_assign_new_leads", None),
    "duplicate_lead_detection": getattr(celery_tasks, "detect_duplicate_leads", None),
    "missed_followup_alerts": getattr(celery_tasks, "send_missed_followup_alerts", None),
    "whatsapp_reminders": getattr(celery_tasks, "send_whatsapp_reminders", None),
    "email_automation": getattr(celery_tasks, "run_email_automation", None),
    "booking_confirmation": getattr(celery_tasks, "send_booking_confirmations", None),
    "invoice_generation": getattr(celery_tasks, "auto_generate_invoices", None),
    "payment_reminders": getattr(celery_tasks, "send_payment_reminders", None),
    "anniversary_birthday_wishes": getattr(celery_tasks, "send_anniversary_birthday_wishes", None),
    "daily_performance_reports": getattr(celery_tasks, "generate_daily_performance_report", None),
    "manager_approval_workflow": getattr(celery_tasks, "calculate_commissions", None),
    "commission_calculation": getattr(celery_tasks, "calculate_commissions", None),
    "lead_scoring_ai": getattr(celery_tasks, "refresh_ai_lead_scoring", None),
}


@router.get("/workflows", dependencies=[Depends(require_permissions({PERMISSIONS.SCHEDULE_REPORTS}))])
async def list_workflows(_: CurrentUser):
    available = [k for k, v in WORKFLOW_TASKS.items() if v is not None]
    return {
        "workflows": sorted(available),
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
