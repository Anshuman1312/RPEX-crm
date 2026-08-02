"""
Service layer for task and activity management business logic.

Services:
- TaskService: Task lifecycle, status transitions
- TaskChecklistService: Checklist management
- TaskCommentService: Comment management
- ActivityService: Activity logging
"""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from loguru import logger

from app.core.exceptions import (
    NotFoundException, ValidationException,
    InvalidStateTransitionException
)
from app.models.task import Task, TaskChecklist, TaskComment, TaskAttachment, Activity
from app.repositories.task_repository import (
    TaskRepository, TaskChecklistRepository, TaskCommentRepository,
    TaskAttachmentRepository, ActivityRepository
)
from app.utils.enums import TaskStatus, TaskPriority
from app.utils.numbering import NumberingService


class TaskService:
    """Service for task operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = TaskRepository(session, Task)
        self.checklist_repo = TaskChecklistRepository(session, TaskChecklist)
        self.comment_repo = TaskCommentRepository(session, TaskComment)
        self.attachment_repo = TaskAttachmentRepository(session, TaskAttachment)
        self.numbering = NumberingService(session)

    async def create_task(
        self,
        title: str,
        created_by_user_id: UUID,
        description: Optional[str] = None,
        task_type: str = "general",
        category: str = "other",
        priority: TaskPriority = TaskPriority.MEDIUM,
        assigned_to_user_id: Optional[UUID] = None,
        due_date: Optional[datetime] = None,
        start_date: Optional[datetime] = None,
        estimated_hours: Optional[Decimal] = None,
        lead_id: Optional[UUID] = None,
        customer_id: Optional[UUID] = None,
        project_id: Optional[UUID] = None,
        booking_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        is_urgent: bool = False,
        is_recurring: bool = False,
        checklists: Optional[List[dict]] = None,
    ) -> Task:
        """Create new task with optional checklists."""
        # Generate task number
        task_number = await self.numbering.get_next_number("TASK")

        # Create task
        task = Task(
            task_number=task_number,
            title=title,
            description=description,
            task_type=task_type,
            category=category,
            status=TaskStatus.PENDING,
            priority=priority,
            assigned_to_user_id=assigned_to_user_id,
            created_by_user_id=created_by_user_id,
            due_date=due_date,
            start_date=start_date,
            estimated_hours=estimated_hours,
            lead_id=lead_id,
            customer_id=customer_id,
            project_id=project_id,
            booking_id=booking_id,
            tags=tags or [],
            is_urgent=is_urgent,
            is_recurring=is_recurring,
        )
        self.session.add(task)
        await self.session.flush()

        # Create checklists if provided
        if checklists:
            for index, checklist_data in enumerate(checklists, 1):
                checklist = TaskChecklist(
                    task_id=task.id,
                    item_number=index,
                    title=checklist_data.get("title"),
                    description=checklist_data.get("description"),
                )
                self.session.add(checklist)
            await self.session.flush()

        logger.info(f"Task created | number={task_number} | title={title}")

        return task

    async def get_task(self, task_id: UUID) -> Task:
        """Get task with all details."""
        task = await self.repo.get_with_details(task_id)
        if not task:
            raise NotFoundException(f"Task {task_id} not found")
        return task

    async def update_task(
        self,
        task_id: UUID,
        **kwargs,
    ) -> Task:
        """Update task."""
        task = await self.repo.get(task_id)
        if not task:
            raise NotFoundException(f"Task {task_id} not found")

        # Update allowed fields
        allowed_fields = {
            "title", "description", "category", "priority", "assigned_to_user_id",
            "due_date", "start_date", "estimated_hours", "progress", "tags", "is_urgent"
        }
        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                setattr(task, key, value)

        logger.info(f"Task updated | id={task_id}")

        return task

    async def list_tasks(
        self,
        assigned_to_user_id: Optional[UUID] = None,
        statuses: Optional[List[str]] = None,
        priorities: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        lead_id: Optional[UUID] = None,
        customer_id: Optional[UUID] = None,
        project_id: Optional[UUID] = None,
        booking_id: Optional[UUID] = None,
        is_urgent: Optional[bool] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
        sort_by: str = "due_date",
        sort_direction: str = "asc",
    ) -> tuple[List[Task], int]:
        """List tasks with filtering."""
        status_enums = None
        if statuses:
            status_enums = [TaskStatus[s.upper()] for s in statuses if s]

        priority_enums = None
        if priorities:
            priority_enums = [TaskPriority[p.upper()] for p in priorities if p]

        return await self.repo.list_with_filter(
            assigned_to_user_id=assigned_to_user_id,
            statuses=status_enums,
            priorities=priority_enums,
            categories=categories,
            lead_id=lead_id,
            customer_id=customer_id,
            project_id=project_id,
            booking_id=booking_id,
            is_urgent=is_urgent,
            search=search,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_direction=sort_direction,
        )

    async def transition_status(
        self,
        task_id: UUID,
        new_status: TaskStatus,
        notes: Optional[str] = None,
    ) -> Task:
        """Transition task status."""
        task = await self.repo.get(task_id)
        if not task:
            raise NotFoundException(f"Task {task_id} not found")

        # Validate state transition
        valid_transitions = {
            TaskStatus.PENDING: [TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED, TaskStatus.ON_HOLD],
            TaskStatus.IN_PROGRESS: [TaskStatus.COMPLETED, TaskStatus.CANCELLED, TaskStatus.ON_HOLD],
            TaskStatus.COMPLETED: [],
            TaskStatus.CANCELLED: [],
            TaskStatus.ON_HOLD: [TaskStatus.PENDING, TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED],
            TaskStatus.OVERDUE: [TaskStatus.COMPLETED, TaskStatus.CANCELLED, TaskStatus.IN_PROGRESS],
        }

        if new_status not in valid_transitions.get(task.status, []):
            raise InvalidStateTransitionException(
                f"Cannot transition from {task.status.value} to {new_status.value}"
            )

        # Update status
        task.status = new_status
        if new_status == TaskStatus.IN_PROGRESS:
            task.start_date = datetime.utcnow()
        elif new_status == TaskStatus.COMPLETED:
            task.completed_at = datetime.utcnow()

        logger.info(f"Task status updated | id={task_id} | status={new_status.value}")

        return task

    async def assign_task(self, task_id: UUID, assigned_to_user_id: Optional[UUID]) -> Task:
        """Assign task to user."""
        task = await self.repo.get(task_id)
        if not task:
            raise NotFoundException(f"Task {task_id} not found")

        task.assigned_to_user_id = assigned_to_user_id

        logger.info(f"Task assigned | id={task_id} | user={assigned_to_user_id}")

        return task

    async def update_progress(
        self,
        task_id: UUID,
        progress: int,
        actual_hours: Optional[Decimal] = None,
    ) -> Task:
        """Update task progress."""
        task = await self.repo.get(task_id)
        if not task:
            raise NotFoundException(f"Task {task_id} not found")

        if not 0 <= progress <= 100:
            raise ValidationException("Progress must be between 0 and 100")

        task.progress = progress
        if actual_hours is not None:
            task.actual_hours = actual_hours

        logger.info(f"Task progress updated | id={task_id} | progress={progress}%")

        return task

    async def delete_task(self, task_id: UUID) -> None:
        """Soft delete task."""
        task = await self.repo.get(task_id)
        if not task:
            raise NotFoundException(f"Task {task_id} not found")

        task.is_deleted = True
        task.deleted_at = datetime.utcnow()

        logger.info(f"Task deleted | id={task_id}")

    async def add_checklist_item(
        self,
        task_id: UUID,
        title: str,
        description: Optional[str] = None,
    ) -> TaskChecklist:
        """Add checklist item to task."""
        task = await self.repo.get(task_id)
        if not task:
            raise NotFoundException(f"Task {task_id} not found")

        # Get next item number
        existing_items = await self.checklist_repo.get_task_checklists(task_id)
        item_number = len(existing_items) + 1

        item = TaskChecklist(
            task_id=task_id,
            item_number=item_number,
            title=title,
            description=description,
        )
        self.session.add(item)
        await self.session.flush()

        logger.info(f"Checklist item added | task={task_id} | item_number={item_number}")

        return item

    async def complete_checklist_item(
        self,
        item_id: UUID,
        completed_by_user_id: UUID,
    ) -> TaskChecklist:
        """Mark checklist item as complete."""
        item = await self.checklist_repo.get(item_id)
        if not item:
            raise NotFoundException(f"Checklist item {item_id} not found")

        item.is_completed = True
        item.completed_by_user_id = completed_by_user_id
        item.completed_at = datetime.utcnow()

        logger.info(f"Checklist item completed | id={item_id}")

        return item

    async def add_comment(
        self,
        task_id: UUID,
        content: str,
        commented_by_user_id: UUID,
        is_internal: bool = False,
        mentions: Optional[List[str]] = None,
    ) -> TaskComment:
        """Add comment to task."""
        task = await self.repo.get(task_id)
        if not task:
            raise NotFoundException(f"Task {task_id} not found")

        comment = TaskComment(
            task_id=task_id,
            content=content,
            commented_by_user_id=commented_by_user_id,
            is_internal=is_internal,
            mentions=mentions or [],
        )
        self.session.add(comment)
        await self.session.flush()

        logger.info(f"Comment added | task={task_id} | by={commented_by_user_id}")

        return comment

    async def get_task_comments(self, task_id: UUID) -> List[TaskComment]:
        """Get comments for a task."""
        return await self.comment_repo.get_task_comments(task_id)

    async def get_task_statistics(self) -> dict:
        """Get task statistics."""
        total_query = await self.session.execute(
            select(func.count(Task.id)).where(Task.is_deleted == False)
        )
        total = total_query.scalars().first() or 0

        status_counts = await self.repo.count_by_status()
        priority_counts = await self.repo.count_by_priority()

        completed = status_counts.get(TaskStatus.COMPLETED, 0)
        completion_rate = (completed / total * 100) if total > 0 else 0

        return {
            "total_tasks": total,
            "pending_count": status_counts.get(TaskStatus.PENDING, 0),
            "in_progress_count": status_counts.get(TaskStatus.IN_PROGRESS, 0),
            "completed_count": status_counts.get(TaskStatus.COMPLETED, 0),
            "cancelled_count": status_counts.get(TaskStatus.CANCELLED, 0),
            "on_hold_count": status_counts.get(TaskStatus.ON_HOLD, 0),
            "overdue_count": status_counts.get(TaskStatus.OVERDUE, 0),
            "completion_rate": round(completion_rate, 2),
            "by_priority": {p.value: count for p, count in priority_counts.items()},
            "by_status": {s.value: count for s, count in status_counts.items()},
        }

    async def get_user_workload(self, user_id: UUID) -> dict:
        """Get task workload for user."""
        tasks, total = await self.repo.get_assigned_to_user(user_id)

        now = datetime.utcnow()
        pending = [t for t in tasks if t.status == TaskStatus.PENDING]
        in_progress = [t for t in tasks if t.status == TaskStatus.IN_PROGRESS]
        completed_today = [
            t for t in tasks if t.status == TaskStatus.COMPLETED and t.completed_at.date() == now.date()
        ]
        overdue = [
            t for t in tasks if t.due_date and t.due_date < now and t.status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]
        ]

        by_priority = {p.value: 0 for p in TaskPriority}
        for task in tasks:
            if task.status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]:
                by_priority[task.priority.value] += 1

        return {
            "user_id": user_id,
            "total_assigned": total,
            "pending_count": len(pending),
            "in_progress_count": len(in_progress),
            "completed_today": len(completed_today),
            "overdue_count": len(overdue),
            "by_priority": by_priority,
        }

    async def get_overdue(self) -> List[Task]:
        """Get overdue tasks."""
        return await self.repo.get_overdue()

    async def get_due_soon(self, days: int = 7) -> List[Task]:
        """Get tasks due soon."""
        return await self.repo.get_due_soon(days)


class ActivityService:
    """Service for activity logging."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ActivityRepository(session, Activity)

    async def log_activity(
        self,
        entity_type: str,
        entity_id: UUID,
        action: str,
        description: str,
        performed_by_user_id: Optional[UUID] = None,
        old_value: Optional[dict] = None,
        new_value: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Activity:
        """Log an activity."""
        activity = Activity(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            description=description,
            performed_by_user_id=performed_by_user_id,
            old_value=old_value,
            new_value=new_value,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.session.add(activity)
        await self.session.flush()

        logger.info(f"Activity logged | entity={entity_type} | action={action}")

        return activity

    async def get_entity_activities(
        self,
        entity_type: str,
        entity_id: UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[List[Activity], int]:
        """Get activities for an entity."""
        return await self.repo.get_by_entity(entity_type, entity_id, skip, limit)

    async def get_user_activities(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[List[Activity], int]:
        """Get activities performed by user."""
        return await self.repo.get_by_user(user_id, skip, limit)

    async def get_recent_activities(self, hours: int = 24, limit: int = 100) -> List[Activity]:
        """Get recent activities."""
        return await self.repo.get_recent(hours, limit)
