"""Prometheus metrics exporter for Dead Letter Queue (DLQ).

Exposes DLQ metrics to Prometheus:
- dlq_queue_depth: Number of failed tasks in DLQ
- dlq_oldest_task_age_hours: Age of oldest task in DLQ
- dlq_task_by_type: Count of failed tasks by task name
- dlq_error_by_type: Count of errors by error type

This should be integrated into the main FastAPI application metrics endpoint.
"""

from prometheus_client import Counter, Gauge, Histogram
from loguru import logger

# ── DLQ Metrics ────────────────────────────────────────────────────────────────

dlq_queue_depth = Gauge(
    "dlq_queue_depth",
    "Number of failed tasks in Dead Letter Queue",
    ["environment"],
)

dlq_oldest_task_age_hours = Gauge(
    "dlq_oldest_task_age_hours",
    "Age of oldest task in Dead Letter Queue (hours)",
    ["environment"],
)

dlq_task_total = Counter(
    "dlq_task_total",
    "Total number of tasks added to DLQ",
    ["task_name", "error_type", "environment"],
)

dlq_task_by_type = Gauge(
    "dlq_task_by_type",
    "Number of failed tasks by task type",
    ["task_name", "environment"],
)

dlq_error_by_type = Gauge(
    "dlq_error_by_type",
    "Number of tasks failed by error type",
    ["error_type", "environment"],
)

dlq_retry_attempts = Counter(
    "dlq_retry_attempts",
    "Total number of DLQ task retry attempts",
    ["task_name", "success", "environment"],
)

dlq_task_age_seconds = Histogram(
    "dlq_task_age_seconds",
    "Age of tasks in DLQ (seconds)",
    buckets=[3600, 7200, 14400, 28800, 86400],  # 1h, 2h, 4h, 8h, 24h
    labelnames=["environment"],
)


def update_dlq_metrics(dlq_manager, environment: str = "production"):
    """Update DLQ metrics from DLQ manager.
    
    Call this periodically (e.g., every 30 seconds) to sync metrics.
    """
    try:
        # Get DLQ statistics
        stats = dlq_manager.get_dlq_stats()
        
        # Update gauge metrics
        dlq_queue_depth.labels(environment=environment).set(stats.get("queue_depth", 0))
        dlq_oldest_task_age_hours.labels(environment=environment).set(
            stats.get("oldest_task_age_hours", 0)
        )
        
        # Get task breakdown by type
        all_tasks = dlq_manager.list_tasks(limit=1000)
        
        task_counts = {}
        error_counts = {}
        
        for task in all_tasks:
            # Count by task name
            task_name = task.get("task_name", "unknown")
            task_counts[task_name] = task_counts.get(task_name, 0) + 1
            
            # Count by error type
            error_type = task.get("error_type", "unknown")
            error_counts[error_type] = error_counts.get(error_type, 0) + 1
            
            # Update age histogram
            try:
                from datetime import datetime
                failed_at = datetime.fromisoformat(task.get("failed_at", ""))
                age_seconds = (datetime.utcnow() - failed_at).total_seconds()
                dlq_task_age_seconds.labels(environment=environment).observe(age_seconds)
            except Exception:
                pass
        
        # Update task breakdown metrics
        for task_name, count in task_counts.items():
            dlq_task_by_type.labels(task_name=task_name, environment=environment).set(count)
        
        # Update error breakdown metrics
        for error_type, count in error_counts.items():
            dlq_error_by_type.labels(error_type=error_type, environment=environment).set(count)
        
        logger.debug(
            f"Updated DLQ metrics: {stats.get('queue_depth', 0)} tasks in queue",
            extra={"queue_depth": stats.get("queue_depth", 0)}
        )
        
    except Exception as exc:
        logger.error(f"Failed to update DLQ metrics: {exc}")


# ── Integration with FastAPI ──────────────────────────────────────────────────

def add_dlq_metrics_to_app(app, dlq_manager, environment: str = "production"):
    """Add DLQ metrics update task to FastAPI lifespan.
    
    Usage in main.py:
        from app.metrics.dlq_metrics import add_dlq_metrics_to_app
        
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Startup
            add_dlq_metrics_to_app(app, dlq_manager)
            
            # Shutdown
            yield
    """
    import asyncio
    from app.workers.celery_app import dlq_manager as global_dlq_manager
    
    dlq_mgr = dlq_manager or global_dlq_manager
    
    async def update_metrics_periodically():
        """Update DLQ metrics every 30 seconds."""
        while True:
            try:
                update_dlq_metrics(dlq_mgr, environment)
                await asyncio.sleep(30)
            except Exception as exc:
                logger.error(f"Error in DLQ metrics update task: {exc}")
                await asyncio.sleep(30)
    
    # Create background task
    app.state.dlq_metrics_task = asyncio.create_task(update_metrics_periodically())
    
    return app
