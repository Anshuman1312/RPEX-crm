from app.workers.celery_app import celery


@celery.task(name="app.workers.celery_tasks.generate_daily_lead_report")
def generate_daily_lead_report() -> str:
    return "Daily lead report generated"


@celery.task(name="app.workers.celery_tasks.generate_weekly_lead_report")
def generate_weekly_lead_report() -> str:
    return "Weekly lead report generated"
