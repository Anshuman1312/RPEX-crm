"""Celery configuration with Dead Letter Queue (DLQ) support.

DLQ Strategy:
- Failed tasks stored in Redis DB 5 (separate from task queue DB 3)
- Tracks: task_id, task_name, args, kwargs, error_message, traceback, retry_count, failed_at
- Auto-cleanup after 30 days
- Monitoring: DLQ depth, oldest task age, retry success rate
- Recovery: Manual retry via API or bulk retry endpoint
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any

import redis
from celery import Celery, Task
from loguru import logger

from app.core.config import get_settings

settings = get_settings()

# ── Dead Letter Queue Manager ──────────────────────────────────────────────────

class DLQManager:
    """Manager for Dead Letter Queue operations."""
    
    DLQ_DB = 5  # Separate Redis database for DLQ
    DLQ_KEY_PREFIX = "dlq:task:"
    DLQ_INDEX_KEY = "dlq:index"  # Sorted set of task IDs by timestamp
    DLQ_RETENTION_DAYS = 30
    
    def __init__(self):
        """Initialize DLQ Redis connection."""
        # Extract Redis URL components
        redis_url = settings.REDIS_URL
        if "://" in redis_url:
            redis_url = redis_url.split("://")[1]
        
        host = redis_url.split(":")[0] if ":" in redis_url else redis_url
        port = redis_url.split(":")[1].split("/")[0] if ":" in redis_url else "6379"
        password = None
        
        if "@" in redis_url:
            password = redis_url.split("@")[0]
        
        self.redis_sync = redis.Redis(
            host=host,
            port=int(port),
            password=password,
            db=self.DLQ_DB,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_keepalive=True,
        )
    
    def add_failed_task(
        self,
        task_id: str,
        task_name: str,
        args: tuple,
        kwargs: dict,
        exception: Exception,
        traceback_str: str,
        retry_count: int = 0,
    ) -> bool:
        """Add a failed task to the DLQ."""
        try:
            now = datetime.utcnow()
            
            task_data = {
                "task_id": task_id,
                "task_name": task_name,
                "args": json.dumps([str(a) for a in args]),
                "kwargs": json.dumps({k: str(v) for k, v in kwargs.items()}),
                "error_message": str(exception),
                "error_type": type(exception).__name__,
                "traceback": traceback_str[:1000],  # Truncate to 1000 chars
                "retry_count": str(retry_count),
                "failed_at": now.isoformat(),
                "failed_at_unix": str(int(now.timestamp())),
            }
            
            # Store task details
            key = f"{self.DLQ_KEY_PREFIX}{task_id}"
            self.redis_sync.hset(key, mapping=task_data)
            self.redis_sync.expire(key, self.DLQ_RETENTION_DAYS * 86400)  # 30-day TTL
            
            # Add to sorted set index (by timestamp for ordering)
            self.redis_sync.zadd(
                self.DLQ_INDEX_KEY,
                {task_id: int(now.timestamp())},
            )
            
            logger.error(
                f"Task {task_name}[{task_id}] added to DLQ after {retry_count} retries",
                extra={
                    "task_id": task_id,
                    "task_name": task_name,
                    "error": str(exception),
                    "retry_count": retry_count,
                }
            )
            
            return True
        except Exception as exc:
            logger.error(f"Failed to add task to DLQ: {exc}")
            return False
    
    def get_task(self, task_id: str) -> dict[str, Any] | None:
        """Retrieve a task from DLQ."""
        try:
            key = f"{self.DLQ_KEY_PREFIX}{task_id}"
            data = self.redis_sync.hgetall(key)
            
            if not data:
                return None
            
            return data
        except Exception as exc:
            logger.error(f"Failed to get DLQ task {task_id}: {exc}")
            return None
    
    def list_tasks(self, limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
        """List all tasks in DLQ (newest first)."""
        try:
            # Get task IDs from sorted set (newest first)
            task_ids = self.redis_sync.zrevrange(
                self.DLQ_INDEX_KEY,
                offset,
                offset + limit - 1,
            )
            
            tasks = []
            for task_id in task_ids:
                task = self.get_task(task_id)
                if task:
                    tasks.append(task)
            
            return tasks
        except Exception as exc:
            logger.error(f"Failed to list DLQ tasks: {exc}")
            return []
    
    def get_dlq_stats(self) -> dict[str, Any]:
        """Get DLQ statistics."""
        try:
            count = self.redis_sync.zcard(self.DLQ_INDEX_KEY)
            
            if count == 0:
                return {
                    "queue_depth": 0,
                    "oldest_task_age_hours": 0,
                    "retention_days": self.DLQ_RETENTION_DAYS,
                }
            
            # Get oldest task
            oldest_task_ids = self.redis_sync.zrange(
                self.DLQ_INDEX_KEY, 0, 0
            )
            
            if oldest_task_ids:
                oldest_task_id = oldest_task_ids[0]
                oldest_task = self.get_task(oldest_task_id)
                
                if oldest_task and "failed_at" in oldest_task:
                    failed_at = datetime.fromisoformat(oldest_task["failed_at"])
                    age_hours = (datetime.utcnow() - failed_at).total_seconds() / 3600
                else:
                    age_hours = 0
            else:
                age_hours = 0
            
            return {
                "queue_depth": count,
                "oldest_task_age_hours": age_hours,
                "retention_days": self.DLQ_RETENTION_DAYS,
            }
        except Exception as exc:
            logger.error(f"Failed to get DLQ stats: {exc}")
            return {"queue_depth": 0, "oldest_task_age_hours": 0}
    
    def remove_task(self, task_id: str) -> bool:
        """Remove a task from DLQ."""
        try:
            key = f"{self.DLQ_KEY_PREFIX}{task_id}"
            self.redis_sync.delete(key)
            self.redis_sync.zrem(self.DLQ_INDEX_KEY, task_id)
            return True
        except Exception as exc:
            logger.error(f"Failed to remove DLQ task {task_id}: {exc}")
            return False


# ── Global DLQ Manager Instance ────────────────────────────────────────────────

dlq_manager = DLQManager()

# ── Custom Task Class with Error Handling ──────────────────────────────────────

class RpexTask(Task):
    """Base task class with DLQ support."""
    
    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 3}
    retry_backoff = True
    retry_backoff_max = 600  # Max 10 minutes
    retry_jitter = True      # Add randomness to prevent thundering herd
    
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Called when task is retried."""
        logger.warning(
            f"Task {self.name}[{task_id}] retrying after error: {exc}",
            extra={"task_id": task_id, "retry_count": self.request.retries}
        )
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called when task fails permanently (all retries exhausted)."""
        logger.error(
            f"Task {self.name}[{task_id}] failed permanently",
            extra={
                "task_id": task_id,
                "error": str(exc),
                "retry_count": self.request.retries,
            }
        )
        
        # Add to DLQ
        dlq_manager.add_failed_task(
            task_id=task_id,
            task_name=self.name,
            args=args,
            kwargs=kwargs,
            exception=exc,
            traceback_str=str(einfo),
            retry_count=self.request.retries,
        )


celery = Celery(
    "rpex_crm",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery.conf.update(
    # ── Task Configuration ────────────────────────────────────────────────────
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # ── Retry Configuration ───────────────────────────────────────────────────
    task_acks_late=True,           # Worker acks after task completion
    task_reject_on_worker_lost=True, # Reject if worker dies
    worker_max_tasks_per_child=1000, # Restart worker periodically
    task_track_started=True,        # Track task start
    
    # ── Broker Configuration ──────────────────────────────────────────────────
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=10,
    
    # ── Result Backend Configuration ──────────────────────────────────────────
    result_expires=3600,
    
    # ── Task Class ───────────────────────────────────────────────────────────
    task_cls=RpexTask,
    
    # ── Schedules ─────────────────────────────────────────────────────────────
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