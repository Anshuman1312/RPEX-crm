"""Dead Letter Queue (DLQ) management API endpoints.

Provides endpoints to:
- List failed tasks in the DLQ
- View task details and error information
- Retry individual failed tasks
- Bulk retry operations
- Monitor DLQ health
"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from loguru import logger
from pydantic import BaseModel

from app.core.deps import get_current_user
from app.models.user import User
from app.workers.celery_app import celery, dlq_manager

# ── Schemas ────────────────────────────────────────────────────────────────────

class DLQTaskResponse(BaseModel):
    """Schema for a failed task in the DLQ."""
    
    task_id: str
    task_name: str
    error_message: str
    error_type: str
    failed_at: str
    retry_count: int
    
    class Config:
        from_attributes = True


class DLQStatsResponse(BaseModel):
    """Schema for DLQ statistics."""
    
    queue_depth: int
    oldest_task_age_hours: float
    retention_days: int


class DLQListResponse(BaseModel):
    """Schema for DLQ task list response."""
    
    total: int
    limit: int
    offset: int
    tasks: list[DLQTaskResponse]


class DLQRetryResponse(BaseModel):
    """Schema for DLQ retry operation response."""
    
    success: bool
    message: str
    task_ids: list[str] | None = None


# ── Router ─────────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/api/v1/dlq", tags=["DLQ"])


# ── Public Endpoints ───────────────────────────────────────────────────────────

@router.get("/stats", response_model=DLQStatsResponse)
async def get_dlq_stats(current_user: User = None) -> dict[str, Any]:
    """Get Dead Letter Queue statistics.
    
    Returns:
        - queue_depth: Number of failed tasks in DLQ
        - oldest_task_age_hours: Age of oldest task
        - retention_days: How long tasks are kept
    
    Example:
        GET /api/v1/dlq/stats
        
        Response:
        {
            "queue_depth": 5,
            "oldest_task_age_hours": 23.5,
            "retention_days": 30
        }
    """
    stats = dlq_manager.get_dlq_stats()
    return stats


@router.get("/tasks", response_model=DLQListResponse)
async def list_dlq_tasks(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = None,
) -> dict[str, Any]:
    """List all failed tasks in the DLQ.
    
    Query Parameters:
        - limit: Number of tasks to return (1-500, default 50)
        - offset: Number of tasks to skip (for pagination)
    
    Returns list of failed tasks ordered by failure time (newest first).
    
    Example:
        GET /api/v1/dlq/tasks?limit=20&offset=0
        
        Response:
        {
            "total": 5,
            "limit": 20,
            "offset": 0,
            "tasks": [
                {
                    "task_id": "abc123",
                    "task_name": "app.tasks.send_email",
                    "error_message": "Connection timeout",
                    "error_type": "TimeoutError",
                    "failed_at": "2026-08-01T10:30:00",
                    "retry_count": 3
                }
            ]
        }
    """
    tasks = dlq_manager.list_tasks(limit=limit, offset=offset)
    stats = dlq_manager.get_dlq_stats()
    
    # Convert string retry_count to int
    for task in tasks:
        if "retry_count" in task:
            task["retry_count"] = int(task["retry_count"])
    
    return {
        "total": stats.get("queue_depth", 0),
        "limit": limit,
        "offset": offset,
        "tasks": tasks,
    }


@router.get("/tasks/{task_id}", response_model=dict[str, Any])
async def get_dlq_task_details(
    task_id: str,
    current_user: User = None,
) -> dict[str, Any]:
    """Get details of a specific failed task.
    
    Path Parameters:
        - task_id: ID of the task to retrieve
    
    Returns full task details including error traceback.
    
    Example:
        GET /api/v1/dlq/tasks/abc123
        
        Response:
        {
            "task_id": "abc123",
            "task_name": "app.tasks.send_email",
            "args": "[user_id=123, email='user@example.com']",
            "kwargs": "{}",
            "error_message": "SMTP connection timeout",
            "error_type": "TimeoutError",
            "traceback": "Traceback...",
            "failed_at": "2026-08-01T10:30:00",
            "retry_count": 3
        }
    """
    task = dlq_manager.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found in DLQ")
    
    # Convert retry_count to int
    if "retry_count" in task:
        task["retry_count"] = int(task["retry_count"])
    
    return task


@router.post("/tasks/{task_id}/retry", response_model=DLQRetryResponse)
async def retry_dlq_task(
    task_id: str,
    current_user: User = None,
) -> dict[str, Any]:
    """Retry a single failed task from the DLQ.
    
    Path Parameters:
        - task_id: ID of the task to retry
    
    Removes task from DLQ and resubmits it to the task queue.
    If task fails again, it will be added back to DLQ.
    
    Example:
        POST /api/v1/dlq/tasks/abc123/retry
        
        Response:
        {
            "success": true,
            "message": "Task resubmitted for execution",
            "task_ids": ["abc123"]
        }
    """
    task = dlq_manager.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found in DLQ")
    
    try:
        # Extract task details
        task_name = task.get("task_name")
        
        # Try to parse args and kwargs
        try:
            import json
            args = json.loads(task.get("args", "[]"))
            kwargs = json.loads(task.get("kwargs", "{}"))
        except Exception:
            args = []
            kwargs = {}
        
        # Resubmit task
        celery.send_task(
            task_name,
            args=tuple(args),
            kwargs=kwargs,
            task_id=task_id,
        )
        
        # Remove from DLQ
        dlq_manager.remove_task(task_id)
        
        logger.info(
            f"Retried DLQ task {task_id}[{task_name}]",
            extra={"task_id": task_id, "task_name": task_name}
        )
        
        return {
            "success": True,
            "message": "Task resubmitted for execution",
            "task_ids": [task_id],
        }
    except Exception as exc:
        logger.error(f"Failed to retry DLQ task {task_id}: {exc}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retry task: {str(exc)}"
        )


@router.post("/tasks/retry-all", response_model=DLQRetryResponse)
async def retry_all_dlq_tasks(
    task_name_filter: str | None = Query(None),
    max_age_hours: int | None = Query(None),
    current_user: User = None,
) -> dict[str, Any]:
    """Retry all failed tasks in the DLQ (bulk operation).
    
    Query Parameters:
        - task_name_filter: Optional filter by task name (partial match)
        - max_age_hours: Only retry tasks newer than this age
    
    Returns list of task IDs that were resubmitted.
    
    Example:
        POST /api/v1/dlq/tasks/retry-all?task_name_filter=send_email&max_age_hours=24
        
        Response:
        {
            "success": true,
            "message": "5 tasks resubmitted for execution",
            "task_ids": ["abc123", "def456", "ghi789", "jkl012", "mno345"]
        }
    """
    try:
        # Get all tasks
        all_tasks = dlq_manager.list_tasks(limit=1000)
        
        retried_ids = []
        now = datetime.utcnow()
        
        for task in all_tasks:
            # Apply filters
            if task_name_filter and task_name_filter not in task.get("task_name", ""):
                continue
            
            if max_age_hours:
                try:
                    failed_at = datetime.fromisoformat(task.get("failed_at", ""))
                    age_hours = (now - failed_at).total_seconds() / 3600
                    if age_hours > max_age_hours:
                        continue
                except Exception:
                    pass
            
            # Retry this task
            try:
                task_id = task.get("task_id")
                task_name = task.get("task_name")
                
                import json
                args = json.loads(task.get("args", "[]"))
                kwargs = json.loads(task.get("kwargs", "{}"))
                
                celery.send_task(
                    task_name,
                    args=tuple(args),
                    kwargs=kwargs,
                    task_id=task_id,
                )
                
                dlq_manager.remove_task(task_id)
                retried_ids.append(task_id)
                
            except Exception as exc:
                logger.error(f"Failed to retry task {task.get('task_id')}: {exc}")
        
        logger.info(
            f"Bulk retried {len(retried_ids)} DLQ tasks",
            extra={"count": len(retried_ids)}
        )
        
        return {
            "success": True,
            "message": f"{len(retried_ids)} tasks resubmitted for execution",
            "task_ids": retried_ids,
        }
    except Exception as exc:
        logger.error(f"Failed to bulk retry DLQ tasks: {exc}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retry tasks: {str(exc)}"
        )


@router.delete("/tasks/{task_id}", response_model=dict[str, str])
async def delete_dlq_task(
    task_id: str,
    current_user: User = None,
) -> dict[str, str]:
    """Delete a failed task from the DLQ.
    
    **WARNING**: This permanently removes the task from DLQ.
    Use only for tasks that should not be retried (e.g., malformed data).
    
    Path Parameters:
        - task_id: ID of the task to delete
    
    Example:
        DELETE /api/v1/dlq/tasks/abc123
        
        Response:
        {
            "success": "Task deleted from DLQ"
        }
    """
    task = dlq_manager.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found in DLQ")
    
    if dlq_manager.remove_task(task_id):
        logger.info(f"Deleted DLQ task {task_id}")
        return {"success": "Task deleted from DLQ"}
    else:
        raise HTTPException(
            status_code=500,
            detail="Failed to delete task"
        )


@router.post("/tasks/cleanup", response_model=dict[str, Any])
async def cleanup_old_dlq_tasks(
    days_old: int = Query(30, ge=1),
    current_user: User = None,
) -> dict[str, Any]:
    """Cleanup (delete) old tasks from the DLQ.
    
    Query Parameters:
        - days_old: Delete tasks older than this many days
    
    Example:
        POST /api/v1/dlq/tasks/cleanup?days_old=30
        
        Response:
        {
            "deleted_count": 5,
            "message": "Deleted 5 tasks older than 30 days"
        }
    """
    try:
        all_tasks = dlq_manager.list_tasks(limit=1000)
        deleted_count = 0
        now = datetime.utcnow()
        cutoff_seconds = days_old * 86400
        
        for task in all_tasks:
            try:
                failed_at = datetime.fromisoformat(task.get("failed_at", ""))
                age_seconds = (now - failed_at).total_seconds()
                
                if age_seconds > cutoff_seconds:
                    if dlq_manager.remove_task(task.get("task_id")):
                        deleted_count += 1
            except Exception:
                pass
        
        logger.info(f"Cleaned up {deleted_count} old DLQ tasks")
        
        return {
            "deleted_count": deleted_count,
            "message": f"Deleted {deleted_count} tasks older than {days_old} days"
        }
    except Exception as exc:
        logger.error(f"Failed to cleanup DLQ tasks: {exc}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cleanup tasks: {str(exc)}"
        )
