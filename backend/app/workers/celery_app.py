from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery = Celery(
    "rpex_crm",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery.conf.update(
    timezone="UTC",
    beat_schedule={
        "daily-lead-report": {
            "task": "app.workers.celery_tasks.generate_daily_lead_report",
            "schedule": 60.0 * 60.0 * 24.0,
        },
        "weekly-lead-report": {
            "task": "app.workers.celery_tasks.generate_weekly_lead_report",
            "schedule": 60.0 * 60.0 * 24.0 * 7.0,
        },
        "payment-reminder-sweep": {
            "task": "app.workers.celery_tasks.send_payment_reminders",
            "schedule": 60.0 * 60.0 * 6.0,
        },
        "commission-calculation-daily": {
            "task": "app.workers.celery_tasks.calculate_commissions",
            "schedule": 60.0 * 60.0 * 24.0,
        },
        "daily-performance-report": {
            "task": "app.workers.celery_tasks.generate_daily_performance_report",
            "schedule": 60.0 * 60.0 * 24.0,
        },
    },
)
