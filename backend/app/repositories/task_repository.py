"""
Repository layer for task and activity data access and persistence.

Repositories:
- TaskRepository: Task CRUD with filtering, status transitions
- TaskChecklistRepository: Checklist management
- TaskCommentRepository: Comment management
- TaskAttachmentRepository: Attachment management
- ActivityRepository: Activity log queries
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, or_, desc, asc, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.repositories.base import BaseRepository
from app.models.task import Task, TaskChecklist, TaskComment, TaskAttachment, Activity
from app.utils.enums import TaskStatus, TaskPriority


class TaskRepository(BaseRepository[Task]):
    """Repository for task operations."""

    async def get_by_number(self, task_number: str) -> Optional[Task]:
        """Get task by number."""
        query = select(Task).where(
            and_(Task.task_number == task_number, Task.is_deleted == False)
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_with_details(self, task_id: UUID) -> Optional[Task]:
        """Get task with checklists and comments."""
        query = (
            select(Task)
            .where(and_(Task.id == task_id, Task.is_deleted == False))
            .options(
                joinedload(Task.checklists),
                joinedload(Task.comments),
                joinedload(Task.attachments),
            )
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_assigned_to_user(
        self,
        user_id: UUID,
        statuses: Optional[List[TaskStatus]] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[Task], int]:
        """Get tasks assigned to user."""
        filters = [Task.assigned_to_user_id == user_id, Task.is_deleted == False]
        if statuses:
            filters.append(Task.status.in_(statuses))

        count_query = select(func.count(Task.id)).where(and_(*filters))
        count_result = await self.session.execute(count_query)
        total = count_result.scalars().first() or 0

        query = (
            select(Task)
            .where(and_(*filters))
            .order_by(asc(Task.due_date), desc(Task.priority))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        tasks = result.scalars().all()

        return tasks, total

    async def get_overdue(self) -> List[Task]:
        """Get overdue tasks."""
        now = datetime.utcnow()
        query = select(Task).where(
            and_(
                Task.due_date < now,
                Task.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS]),
                Task.is_deleted == False,
            )
        ).order_by(asc(Task.due_date))
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_due_soon(self, days: int = 7) -> List[Task]:
        """Get tasks due within N days."""
        now = datetime.utcnow()
        future = now + timedelta(days=days)

        query = select(Task).where(
            and_(
                Task.due_date >= now,
                Task.due_date <= future,
                Task.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS]),
                Task.is_deleted == False,
            )
        ).order_by(asc(Task.due_date))
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_for_lead(
        self,
        lead_id: UUID,
        statuses: Optional[List[TaskStatus]] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[Task], int]:
        """Get tasks for a lead."""
        filters = [Task.lead_id == lead_id, Task.is_deleted == False]
        if statuses:
            filters.append(Task.status.in_(statuses))

        count_query = select(func.count(Task.id)).where(and_(*filters))
        count_result = await self.session.execute(count_query)
        total = count_result.scalars().first() or 0

        query = (
            select(Task)
            .where(and_(*filters))
            .order_by(desc(Task.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        tasks = result.scalars().all()

        return tasks, total

    async def get_for_customer(
        self,
        customer_id: UUID,
        statuses: Optional[List[TaskStatus]] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[Task], int]:
        """Get tasks for a customer."""
        filters = [Task.customer_id == customer_id, Task.is_deleted == False]
        if statuses:
            filters.append(Task.status.in_(statuses))

        count_query = select(func.count(Task.id)).where(and_(*filters))
        count_result = await self.session.execute(count_query)
        total = count_result.scalars().first() or 0

        query = (
            select(Task)
            .where(and_(*filters))
            .order_by(desc(Task.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        tasks = result.scalars().all()

        return tasks, total

    async def list_with_filter(
        self,
        assigned_to_user_id: Optional[UUID] = None,
        statuses: Optional[List[TaskStatus]] = None,
        priorities: Optional[List[TaskPriority]] = None,
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
    ) -> Tuple[List[Task], int]:
        """List tasks with comprehensive filtering."""
        filters = [Task.is_deleted == False]

        if assigned_to_user_id:
            filters.append(Task.assigned_to_user_id == assigned_to_user_id)
        if statuses:
            filters.append(Task.status.in_(statuses))
        if priorities:
            filters.append(Task.priority.in_(priorities))
        if categories:
            filters.append(Task.category.in_(categories))
        if lead_id:
            filters.append(Task.lead_id == lead_id)
        if customer_id:
            filters.append(Task.customer_id == customer_id)
        if project_id:
            filters.append(Task.project_id == project_id)
        if booking_id:
            filters.append(Task.booking_id == booking_id)
        if is_urgent is not None:
            filters.append(Task.is_urgent == is_urgent)
        if search:
            search_term = f"%{search}%"
            filters.append(
                or_(
                    Task.title.ilike(search_term),
                    Task.description.ilike(search_term),
                    Task.task_number.ilike(search_term),
                )
            )

        count_query = select(func.count(Task.id)).where(and_(*filters))
        count_result = await self.session.execute(count_query)
        total = count_result.scalars().first() or 0

        # Sort
        order_by = getattr(Task, sort_by, Task.due_date)
        if sort_direction == "desc":
            order_by = desc(order_by)
        else:
            order_by = asc(order_by)

        query = (
            select(Task)
            .where(and_(*filters))
            .order_by(order_by)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        tasks = result.scalars().all()

        return tasks, total

    async def count_by_status(self) -> dict:
        """Count tasks by status."""
        query = (
            select(Task.status, func.count(Task.id))
            .where(Task.is_deleted == False)
            .group_by(Task.status)
        )
        result = await self.session.execute(query)
        return {status: count for status, count in result.all()}

    async def count_by_priority(self) -> dict:
        """Count tasks by priority."""
        query = (
            select(Task.priority, func.count(Task.id))
            .where(Task.is_deleted == False)
            .group_by(Task.priority)
        )
        result = await self.session.execute(query)
        return {priority: count for priority, count in result.all()}


class TaskChecklistRepository(BaseRepository[TaskChecklist]):
    """Repository for task checklist operations."""

    async def get_task_checklists(self, task_id: UUID) -> List[TaskChecklist]:
        """Get all checklists for a task."""
        query = (
            select(TaskChecklist)
            .where(
                and_(
                    TaskChecklist.task_id == task_id,
                    TaskChecklist.is_deleted == False,
                )
            )
            .order_by(asc(TaskChecklist.item_number))
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def count_by_completion(self, task_id: UUID) -> Tuple[int, int]:
        """Get completion count for task checklists."""
        query = select(func.count(TaskChecklist.id)).where(
            and_(
                TaskChecklist.task_id == task_id,
                TaskChecklist.is_deleted == False,
            )
        )
        result = await self.session.execute(query)
        total = result.scalars().first() or 0

        query = select(func.count(TaskChecklist.id)).where(
            and_(
                TaskChecklist.task_id == task_id,
                TaskChecklist.is_completed == True,
                TaskChecklist.is_deleted == False,
            )
        )
        result = await self.session.execute(query)
        completed = result.scalars().first() or 0

        return completed, total


class TaskCommentRepository(BaseRepository[TaskComment]):
    """Repository for task comment operations."""

    async def get_task_comments(self, task_id: UUID) -> List[TaskComment]:
        """Get all comments for a task."""
        query = (
            select(TaskComment)
            .where(
                and_(
                    TaskComment.task_id == task_id,
                    TaskComment.is_deleted == False,
                )
            )
            .order_by(desc(TaskComment.created_at))
        )
        result = await self.session.execute(query)
        return result.scalars().all()


class TaskAttachmentRepository(BaseRepository[TaskAttachment]):
    """Repository for task attachment operations."""

    async def get_task_attachments(self, task_id: UUID) -> List[TaskAttachment]:
        """Get all attachments for a task."""
        query = (
            select(TaskAttachment)
            .where(
                and_(
                    TaskAttachment.task_id == task_id,
                    TaskAttachment.is_deleted == False,
                )
            )
            .order_by(desc(TaskAttachment.created_at))
        )
        result = await self.session.execute(query)
        return result.scalars().all()


class ActivityRepository(BaseRepository[Activity]):
    """Repository for activity log operations."""

    async def get_by_entity(
        self,
        entity_type: str,
        entity_id: UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[Activity], int]:
        """Get activities for an entity."""
        filters = [Activity.entity_type == entity_type, Activity.entity_id == entity_id]

        count_query = select(func.count(Activity.id)).where(and_(*filters))
        count_result = await self.session.execute(count_query)
        total = count_result.scalars().first() or 0

        query = (
            select(Activity)
            .where(and_(*filters))
            .order_by(desc(Activity.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        activities = result.scalars().all()

        return activities, total

    async def get_by_action(
        self,
        action: str,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[Activity], int]:
        """Get activities by action type."""
        filters = [Activity.action == action]

        count_query = select(func.count(Activity.id)).where(and_(*filters))
        count_result = await self.session.execute(count_query)
        total = count_result.scalars().first() or 0

        query = (
            select(Activity)
            .where(and_(*filters))
            .order_by(desc(Activity.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        activities = result.scalars().all()

        return activities, total

    async def get_by_user(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[Activity], int]:
        """Get activities performed by a user."""
        filters = [Activity.performed_by_user_id == user_id]

        count_query = select(func.count(Activity.id)).where(and_(*filters))
        count_result = await self.session.execute(count_query)
        total = count_result.scalars().first() or 0

        query = (
            select(Activity)
            .where(and_(*filters))
            .order_by(desc(Activity.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        activities = result.scalars().all()

        return activities, total

    async def get_recent(self, hours: int = 24, limit: int = 100) -> List[Activity]:
        """Get recent activities within last N hours."""
        since = datetime.utcnow() - timedelta(hours=hours)

        query = (
            select(Activity)
            .where(Activity.created_at >= since)
            .order_by(desc(Activity.created_at))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()
