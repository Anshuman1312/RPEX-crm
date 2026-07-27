"""
Service layer for follow-up management business logic.

Services:
- FollowUpService: Follow-up lifecycle, status transitions
- FollowUpTaskService: Task management
- FollowUpOutcomeService: Outcome recording
"""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.core.exceptions import (
    NotFoundException, ConflictException, ValidationException,
    InvalidStateTransitionException
)
from app.models.followup import FollowUp, FollowUpTask, FollowUpOutcome
from app.models.lead import Lead
from app.models.customer import Customer
from app.repositories.followup_repository import (
    FollowUpRepository, FollowUpTaskRepository, FollowUpOutcomeRepository,
    FollowUpAttachmentRepository
)
from app.utils.enums import (
    FollowUpStatus, FollowUpType, FollowUpOutcomeType,
    FollowUpTaskStatus, FollowUpTaskType
)
from app.utils.numbering import NumberingService


class FollowUpService:
    """Service for follow-up operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = FollowUpRepository(session)
        self.task_repo = FollowUpTaskRepository(session)
        self.outcome_repo = FollowUpOutcomeRepository(session)
        self.attachment_repo = FollowUpAttachmentRepository(session)
        self.numbering = NumberingService(session)

    async def create_followup(
        self,
        type_: FollowUpType,
        subject: str,
        scheduled_at: datetime,
        created_by_user_id: UUID,
        description: Optional[str] = None,
        assigned_to_user_id: Optional[UUID] = None,
        lead_id: Optional[UUID] = None,
        customer_id: Optional[UUID] = None,
        priority: int = 0,
        is_critical: bool = False,
        notes: Optional[str] = None,
        tasks: Optional[List[dict]] = None,
    ) -> FollowUp:
        """Create new follow-up with tasks."""
        # Validate lead or customer provided
        if not lead_id and not customer_id:
            raise ValidationException("Either lead_id or customer_id must be provided")

        # Validate references exist
        if lead_id:
            lead = await self.session.get(Lead, lead_id)
            if not lead:
                raise NotFoundException(f"Lead {lead_id} not found")

        if customer_id:
            customer = await self.session.get(Customer, customer_id)
            if not customer:
                raise NotFoundException(f"Customer {customer_id} not found")

        # Generate follow-up number
        followup_number = await self.numbering.get_next_number("FOLUP")

        # Create follow-up
        followup = FollowUp(
            followup_number=followup_number,
            type=type_,
            subject=subject,
            description=description,
            scheduled_at=scheduled_at,
            status=FollowUpStatus.SCHEDULED,
            assigned_to_user_id=assigned_to_user_id,
            created_by_user_id=created_by_user_id,
            lead_id=lead_id,
            customer_id=customer_id,
            priority=priority,
            is_critical=is_critical,
            notes=notes,
        )
        self.session.add(followup)
        await self.session.flush()

        # Create tasks if provided
        if tasks:
            for index, task_data in enumerate(tasks, 1):
                task = FollowUpTask(
                    followup_id=followup.id,
                    task_type=task_data.get("task_type", FollowUpTaskType.FOLLOW_UP),
                    task_number=index,
                    title=task_data.get("title"),
                    description=task_data.get("description"),
                    scheduled_at=task_data.get("scheduled_at"),
                    is_required=task_data.get("is_required", False),
                )
                self.session.add(task)
            await self.session.flush()

        logger.info(f"Follow-up created | number={followup_number} | lead={lead_id} | customer={customer_id}")

        return followup

    async def get_followup(self, followup_id: UUID) -> FollowUp:
        """Get follow-up with all details."""
        followup = await self.repo.get_with_details(followup_id)
        if not followup:
            raise NotFoundException(f"Follow-up {followup_id} not found")
        return followup

    async def update_followup(
        self,
        followup_id: UUID,
        **kwargs,
    ) -> FollowUp:
        """Update follow-up (SCHEDULED only)."""
        followup = await self.repo.get(followup_id)
        if not followup:
            raise NotFoundException(f"Follow-up {followup_id} not found")

        # Only allow updates to SCHEDULED follow-ups
        if followup.status != FollowUpStatus.SCHEDULED:
            raise ValidationException(f"Cannot update {followup.status.value} follow-up")

        # Update allowed fields
        allowed_fields = {
            "subject", "description", "scheduled_at", "assigned_to_user_id",
            "priority", "is_critical", "notes"
        }
        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                setattr(followup, key, value)

        logger.info(f"Follow-up updated | id={followup_id}")

        return followup

    async def list_followups(
        self,
        lead_id: Optional[UUID] = None,
        customer_id: Optional[UUID] = None,
        assigned_to_user_id: Optional[UUID] = None,
        statuses: Optional[List[str]] = None,
        types: Optional[List[str]] = None,
        priority: Optional[int] = None,
        is_critical: Optional[bool] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
        sort_by: str = "scheduled_at",
        sort_direction: str = "asc",
    ) -> tuple[List[FollowUp], int]:
        """List follow-ups with filtering."""
        # Parse enums from strings if provided
        status_enums = None
        if statuses:
            status_enums = [FollowUpStatus[s.upper()] for s in statuses if s]

        type_enums = None
        if types:
            type_enums = [FollowUpType[t.upper()] for t in types if t]

        return await self.repo.list_with_filter(
            lead_id=lead_id,
            customer_id=customer_id,
            assigned_to_user_id=assigned_to_user_id,
            statuses=status_enums,
            types=type_enums,
            priority=priority,
            is_critical=is_critical,
            search=search,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_direction=sort_direction,
        )

    async def transition_status(
        self,
        followup_id: UUID,
        new_status: FollowUpStatus,
        notes: Optional[str] = None,
    ) -> FollowUp:
        """Transition follow-up status."""
        followup = await self.repo.get(followup_id)
        if not followup:
            raise NotFoundException(f"Follow-up {followup_id} not found")

        # Validate state transition
        valid_transitions = {
            FollowUpStatus.SCHEDULED: [FollowUpStatus.COMPLETED, FollowUpStatus.CANCELLED, FollowUpStatus.OVERDUE],
            FollowUpStatus.COMPLETED: [FollowUpStatus.CANCELLED],
            FollowUpStatus.CANCELLED: [],
            FollowUpStatus.OVERDUE: [FollowUpStatus.COMPLETED, FollowUpStatus.CANCELLED],
        }

        if new_status not in valid_transitions.get(followup.status, []):
            raise InvalidStateTransitionException(
                f"Cannot transition from {followup.status.value} to {new_status.value}"
            )

        # Update status
        followup.status = new_status
        if new_status == FollowUpStatus.COMPLETED:
            followup.completed_at = datetime.utcnow()
        if notes and not followup.notes:
            followup.notes = notes

        logger.info(f"Follow-up status updated | id={followup_id} | status={new_status.value}")

        return followup

    async def assign_followup(self, followup_id: UUID, assigned_to_user_id: UUID) -> FollowUp:
        """Assign follow-up to user."""
        followup = await self.repo.get(followup_id)
        if not followup:
            raise NotFoundException(f"Follow-up {followup_id} not found")

        followup.assigned_to_user_id = assigned_to_user_id

        logger.info(f"Follow-up assigned | id={followup_id} | user={assigned_to_user_id}")

        return followup

    async def delete_followup(self, followup_id: UUID) -> None:
        """Soft delete follow-up."""
        followup = await self.repo.get(followup_id)
        if not followup:
            raise NotFoundException(f"Follow-up {followup_id} not found")

        followup.is_deleted = True
        followup.deleted_at = datetime.utcnow()

        logger.info(f"Follow-up deleted | id={followup_id}")

    async def add_task(
        self,
        followup_id: UUID,
        task_type: FollowUpTaskType,
        title: str,
        description: Optional[str] = None,
        scheduled_at: Optional[datetime] = None,
        is_required: bool = False,
    ) -> FollowUpTask:
        """Add task to follow-up."""
        followup = await self.repo.get(followup_id)
        if not followup:
            raise NotFoundException(f"Follow-up {followup_id} not found")

        # Get next task number
        existing_tasks = await self.task_repo.get_followup_tasks(followup_id)
        task_number = len(existing_tasks) + 1

        task = FollowUpTask(
            followup_id=followup_id,
            task_type=task_type,
            task_number=task_number,
            title=title,
            description=description,
            scheduled_at=scheduled_at,
            is_required=is_required,
        )
        self.session.add(task)
        await self.session.flush()

        logger.info(f"Task added | followup={followup_id} | task_number={task_number}")

        return task

    async def update_task_status(
        self,
        task_id: UUID,
        new_status: FollowUpTaskStatus,
        result_notes: Optional[str] = None,
    ) -> FollowUpTask:
        """Update task status."""
        task = await self.task_repo.get(task_id)
        if not task:
            raise NotFoundException(f"Task {task_id} not found")

        # Validate state transition
        valid_transitions = {
            FollowUpTaskStatus.PENDING: [
                FollowUpTaskStatus.IN_PROGRESS,
                FollowUpTaskStatus.COMPLETED,
                FollowUpTaskStatus.CANCELLED,
                FollowUpTaskStatus.SKIPPED,
            ],
            FollowUpTaskStatus.IN_PROGRESS: [
                FollowUpTaskStatus.COMPLETED,
                FollowUpTaskStatus.CANCELLED,
            ],
            FollowUpTaskStatus.COMPLETED: [],
            FollowUpTaskStatus.CANCELLED: [],
            FollowUpTaskStatus.SKIPPED: [],
        }

        if new_status not in valid_transitions.get(task.status, []):
            raise InvalidStateTransitionException(
                f"Cannot transition task from {task.status.value} to {new_status.value}"
            )

        task.status = new_status
        if new_status == FollowUpTaskStatus.IN_PROGRESS:
            task.started_at = datetime.utcnow()
        elif new_status == FollowUpTaskStatus.COMPLETED:
            task.completed_at = datetime.utcnow()
        if result_notes:
            task.result_notes = result_notes

        logger.info(f"Task status updated | id={task_id} | status={new_status.value}")

        return task

    async def record_outcome(
        self,
        followup_id: UUID,
        outcome_type: FollowUpOutcomeType,
        summary: str,
        recorded_by_user_id: UUID,
        next_step: Optional[str] = None,
        next_followup_date: Optional[datetime] = None,
        estimated_deal_value: Optional[Decimal] = None,
        conversion_probability: Optional[int] = None,
        lost_reason: Optional[str] = None,
        discussed_projects: Optional[List[str]] = None,
        discussed_units: Optional[List[str]] = None,
    ) -> FollowUpOutcome:
        """Record outcome for follow-up."""
        followup = await self.repo.get(followup_id)
        if not followup:
            raise NotFoundException(f"Follow-up {followup_id} not found")

        outcome = FollowUpOutcome(
            followup_id=followup_id,
            outcome_type=outcome_type,
            summary=summary,
            next_step=next_step,
            next_followup_date=next_followup_date,
            estimated_deal_value=estimated_deal_value,
            conversion_probability=conversion_probability,
            lost_reason=lost_reason,
            discussed_projects=discussed_projects or [],
            discussed_units=discussed_units or [],
            recorded_by_user_id=recorded_by_user_id,
            recorded_at=datetime.utcnow(),
        )
        self.session.add(outcome)
        await self.session.flush()

        logger.info(f"Outcome recorded | followup={followup_id} | type={outcome_type.value}")

        return outcome

    async def get_followup_statistics(self) -> dict:
        """Get follow-up statistics."""
        from sqlalchemy import func, select

        # Total counts
        query = select(func.count(FollowUp.id)).where(FollowUp.is_deleted == False)
        result = await self.session.execute(query)
        total = result.scalars().first() or 0

        # Status counts
        status_counts = await self.repo.count_by_status()
        type_counts = await self.repo.count_by_type()
        outcome_counts = await self.outcome_repo.count_by_type()

        # Completion rate
        completed = status_counts.get(FollowUpStatus.COMPLETED, 0)
        completion_rate = (completed / total * 100) if total > 0 else 0

        # Total deal value
        total_deal_value = await self.outcome_repo.get_total_deal_value()

        return {
            "total_followups": total,
            "scheduled_count": status_counts.get(FollowUpStatus.SCHEDULED, 0),
            "completed_count": status_counts.get(FollowUpStatus.COMPLETED, 0),
            "overdue_count": status_counts.get(FollowUpStatus.OVERDUE, 0),
            "cancelled_count": status_counts.get(FollowUpStatus.CANCELLED, 0),
            "completion_rate": round(completion_rate, 2),
            "by_type": {t.value: count for t, count in type_counts.items()},
            "by_status": {s.value: count for s, count in status_counts.items()},
            "by_outcome": {o.value: count for o, count in outcome_counts.items()},
            "total_deal_value": float(total_deal_value),
        }

    async def get_lead_summary(self, lead_id: UUID) -> dict:
        """Get follow-up summary for a lead."""
        followups, total = await self.repo.get_lead_followups(
            lead_id,
            statuses=[FollowUpStatus.SCHEDULED, FollowUpStatus.COMPLETED],
        )

        completed = [f for f in followups if f.status == FollowUpStatus.COMPLETED]
        scheduled = [f for f in followups if f.status == FollowUpStatus.SCHEDULED]

        last_followup = max(
            (f for f in followups if f.completed_at),
            key=lambda x: x.completed_at,
            default=None,
        )
        next_followup = min(
            (f for f in followups if f.status == FollowUpStatus.SCHEDULED),
            key=lambda x: x.scheduled_at,
            default=None,
        )

        # Outcome counts
        outcome_counts = {}
        for followup in completed:
            outcomes = await self.outcome_repo.get_followup_outcomes(followup.id)
            for outcome in outcomes:
                outcome_type = outcome.outcome_type.value
                outcome_counts[outcome_type] = outcome_counts.get(outcome_type, 0) + 1

        return {
            "lead_id": lead_id,
            "total_followups": total,
            "scheduled_count": len(scheduled),
            "completed_count": len(completed),
            "last_followup_date": last_followup.completed_at if last_followup else None,
            "next_followup_date": next_followup.scheduled_at if next_followup else None,
            "outcome_summary": outcome_counts,
        }

    async def get_user_workload(self, user_id: UUID) -> dict:
        """Get follow-up workload for user."""
        followups, total = await self.repo.get_assigned_to_user(user_id)

        now = datetime.utcnow()
        scheduled = [f for f in followups if f.status == FollowUpStatus.SCHEDULED]
        overdue = [f for f in scheduled if f.scheduled_at < now]
        completed_today = [
            f
            for f in followups
            if f.status == FollowUpStatus.COMPLETED
            and f.completed_at.date() == now.date()
        ]

        by_priority = {0: 0, 1: 0, 2: 0}
        for followup in scheduled:
            by_priority[followup.priority] = by_priority.get(followup.priority, 0) + 1

        return {
            "user_id": user_id,
            "total_assigned": total,
            "scheduled_count": len(scheduled),
            "overdue_count": len(overdue),
            "completed_today": len(completed_today),
            "by_priority": by_priority,
        }

    async def get_scheduled_for_date(self, target_date: datetime) -> List[FollowUp]:
        """Get follow-ups scheduled for specific date."""
        return await self.repo.get_scheduled_for_date(target_date)

    async def get_overdue(self) -> List[FollowUp]:
        """Get overdue follow-ups."""
        return await self.repo.get_overdue()

    async def get_upcoming(self, days: int = 7) -> List[FollowUp]:
        """Get upcoming follow-ups."""
        return await self.repo.get_upcoming(days)
