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
        "auto-lead-assignment": {
            "task": "app.workers.celery_tasks.auto_assign_new_leads",
            "schedule": 60.0 * 30.0,
        },
        "duplicate-lead-detection": {
            "task": "app.workers.celery_tasks.detect_duplicate_leads",
            "schedule": 60.0 * 60.0,
        },
        "missed-followup-alerts": {
            "task": "app.workers.celery_tasks.send_missed_followup_alerts",
            "schedule": 60.0 * 30.0,
        },
        "whatsapp-reminders": {
            "task": "app.workers.celery_tasks.send_whatsapp_reminders",
            "schedule": 60.0 * 60.0,
        },
        "email-automation": {
            "task": "app.workers.celery_tasks.run_email_automation",
            "schedule": 60.0 * 60.0,
        },
        "booking-confirmation-dispatch": {
            "task": "app.workers.celery_tasks.send_booking_confirmations",
            "schedule": 60.0 * 60.0,
        },
        "auto-invoice-generation": {
            "task": "app.workers.celery_tasks.auto_generate_invoices",
            "schedule": 60.0 * 60.0 * 6.0,
        },
        "payment-reminder-sweep": {
            "task": "app.workers.celery_tasks.send_payment_reminders",
            "schedule": 60.0 * 60.0 * 6.0,
        },
        "customer-event-wishes": {
            "task": "app.workers.celery_tasks.send_anniversary_birthday_wishes",
            "schedule": 60.0 * 60.0 * 24.0,
        },
        "commission-calculation-daily": {
            "task": "app.workers.celery_tasks.calculate_commissions",
            "schedule": 60.0 * 60.0 * 24.0,
        },
        "daily-performance-report": {
            "task": "app.workers.celery_tasks.generate_daily_performance_report",
            "schedule": 60.0 * 60.0 * 24.0,
        },
        "ai-lead-scoring-refresh": {
            "task": "app.workers.celery_tasks.refresh_ai_lead_scoring",
            "schedule": 60.0 * 60.0 * 4.0,
        },
    },
)
