from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    NotFoundException,
    ValidationException,
    BusinessRuleException,
    InvalidStateTransitionException,
)
from app.models.lead import Lead, LeadActivity, LeadAssignment
from app.repositories.lead_repository import (
    LeadRepository,
    LeadActivityRepository,
    LeadAssignmentRepository,
)
from app.utils.enums import LeadStatus
from app.utils.filters import LeadFilterParams
from app.utils.numbering import NumberingService, NumberingPrefix


def _utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _make_naive(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    if dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt


class LeadService:
    """Lead management business logic."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.lead_repo = LeadRepository(session, Lead)
        self.activity_repo = LeadActivityRepository(session, LeadActivity)
        self.assignment_repo = LeadAssignmentRepository(session, LeadAssignment)
        self.numbering = NumberingService(session)

    async def create_lead(
        self,
        full_name: str,
        email: Optional[str],
        phone: Optional[str],
        source: str,
        company_name: Optional[str] = None,
        designation: Optional[str] = None,
        budget: Optional[int] = None,
        notes: Optional[str] = None,
        interested_in_project: Optional[str] = None,
        preferred_unit_type: Optional[str] = None,
        assigned_to_user_id: Optional[str] = None,
        created_by: Optional[str] = None,
        next_followup_at: Optional[datetime] = None,
    ) -> Lead:
        """Create new lead."""
        # Generate lead number
        lead_number = await self.numbering.get_next_number(NumberingPrefix.LEAD)

        # Create lead
        lead = await self.lead_repo.create(
            lead_number=lead_number,
            full_name=full_name,
            email=email,
            phone=phone,
            source=source,
            status=LeadStatus.NEW.value,
            company_name=company_name,
            designation=designation,
            budget=budget,
            notes=notes,
            interested_in_project=uuid.UUID(interested_in_project) if interested_in_project else None,
            preferred_unit_type=preferred_unit_type,
            assigned_to_user_id=uuid.UUID(assigned_to_user_id) if assigned_to_user_id else None,
            created_by=uuid.UUID(created_by) if created_by else None,
            next_followup_at=_make_naive(next_followup_at),
        )

        # Create initial assignment if user specified
        if assigned_to_user_id:
            await self.assignment_repo.create(
                lead_id=lead.id,
                assigned_to_user_id=uuid.UUID(assigned_to_user_id),
                assigned_by_user_id=uuid.UUID(created_by) if created_by else None,
                assigned_at=_utc_now(),
                notes="Initial assignment on lead creation",
            )

        await self.session.flush()
        return lead

    async def get_lead(self, lead_id: str) -> Lead:
        """Get lead with all details."""
        lead = await self.lead_repo.get_with_activities(lead_id)
        if not lead:
            raise NotFoundException("Lead", lead_id)
        return lead

    async def list_leads(
        self, filters: LeadFilterParams, skip: int = 0, limit: int = 20
    ) -> tuple[list[Lead], int]:
        """List leads with filtering."""
        return await self.lead_repo.list_with_filter(filters, skip, limit)

    async def update_lead(self, lead_id: str, **updates) -> Lead:
        """Update lead details."""
        lead = await self.lead_repo.get_or_404(lead_id, "Lead")

        # Filter allowed fields
        allowed_fields = {
            "full_name", "email", "phone", "company_name", "designation",
            "budget", "notes", "interested_in_project", "preferred_unit_type",
            "next_followup_at"
        }
        filtered_updates = {k: v for k, v in updates.items() if k in allowed_fields and v is not None}

        # Convert string IDs to UUIDs for foreign keys
        if "interested_in_project" in filtered_updates and filtered_updates["interested_in_project"]:
            filtered_updates["interested_in_project"] = uuid.UUID(filtered_updates["interested_in_project"])

        if "next_followup_at" in filtered_updates:
            filtered_updates["next_followup_at"] = _make_naive(filtered_updates["next_followup_at"])

        if filtered_updates:
            lead = await self.lead_repo.update(lead_id, **filtered_updates)

        await self.session.flush()
        return lead

    async def transition_status(
        self, lead_id: str, new_status: str, notes: Optional[str] = None
    ) -> Lead:
        """
        Transition lead to new status.

        Validates status transitions.
        """
        lead = await self.lead_repo.get_or_404(lead_id, "Lead")

        # Verify transition is allowed
        allowed_statuses = [status.value for status in LeadStatus]

        # Validate transition
        if lead.status not in allowed_statuses:
            raise InvalidStateTransitionException(
                "Lead", lead.status or "unknown", "unknown"
            )

        if new_status not in allowed_statuses:
            raise InvalidStateTransitionException(
                "Lead", lead.status, new_status
            )

        # Update status
        lead = await self.lead_repo.update(lead_id, status=new_status)

        # Handle conversion
        if new_status == LeadStatus.CONVERTED.value:
            lead = await self.lead_repo.update(lead_id, conversion_date=_utc_now())

        # Handle lost
        if new_status == LeadStatus.LOST.value:
            if notes:
                lead = await self.lead_repo.update(lead_id, lost_reason=notes)

        # Log activity
        await self.activity_repo.create(
            lead_id=lead.id,
            activity_type="status_change",
            subject=f"Status changed to {new_status}",
            description=notes,
            outcome=new_status,
            activity_date=_utc_now(),
        )

        await self.session.flush()
        return lead

    async def assign_lead(
        self, lead_id: str, assigned_to_user_id: str, assigned_by_user_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Lead:
        """Assign lead to user."""
        lead = await self.lead_repo.get_or_404(lead_id, "Lead")

        # Mark previous assignment as unassigned
        active_assignment = await self.assignment_repo.get_active_assignment(str(lead.id))
        if active_assignment:
            await self.assignment_repo.update(
                str(active_assignment.id),
                unassigned_at=_utc_now(),
            )

        # Create new assignment
        await self.assignment_repo.create(
            lead_id=lead.id,
            assigned_to_user_id=uuid.UUID(assigned_to_user_id),
            assigned_by_user_id=uuid.UUID(assigned_by_user_id) if assigned_by_user_id else None,
            assigned_at=_utc_now(),
            notes=notes,
        )

        # Update lead
        lead = await self.lead_repo.update(
            lead_id,
            assigned_to_user_id=uuid.UUID(assigned_to_user_id),
            assignment_date=_utc_now(),
        )

        # Log activity
        await self.activity_repo.create(
            lead_id=lead.id,
            activity_type="assignment",
            subject=f"Assigned to user {assigned_to_user_id}",
            description=notes,
            activity_date=_utc_now(),
        )

        await self.session.flush()
        return lead

    async def add_activity(
        self,
        lead_id: str,
        activity_type: str,
        subject: str,
        description: Optional[str] = None,
        outcome: Optional[str] = None,
        activity_date: Optional[datetime] = None,
        next_followup: Optional[datetime] = None,
        performed_by_user_id: Optional[str] = None,
    ) -> LeadActivity:
        """Add activity to lead."""
        # Verify lead exists
        lead = await self.lead_repo.get_or_404(lead_id, "Lead")

        activity_date_naive = _make_naive(activity_date) or _utc_now()
        next_followup_naive = _make_naive(next_followup)

        activity = await self.activity_repo.create(
            lead_id=lead.id,
            activity_type=activity_type,
            subject=subject,
            description=description,
            outcome=outcome,
            activity_date=activity_date_naive,
            next_followup=next_followup_naive,
            performed_by_user_id=uuid.UUID(performed_by_user_id) if performed_by_user_id else None,
        )

        # Update lead's last activity timestamps
        await self.lead_repo.update(
            lead_id,
            last_activity_at=_utc_now(),
            last_contacted_at=activity_date_naive,
            next_followup_at=next_followup_naive,
        )

        await self.session.flush()
        return activity

    async def get_lead_statistics(self) -> dict:
        """Get lead statistics."""
        total = await self.lead_repo.count()
        by_status = await self.lead_repo.count_by_status()
        by_source = await self.lead_repo.count_by_source()

        return {
            "total": total,
            "by_status": by_status,
            "by_source": by_source,
        }

    async def delete_lead(self, lead_id: str) -> None:
        """Soft delete a lead."""
        await self.lead_repo.get_or_404(lead_id, "Lead")
        await self.lead_repo.soft_delete(lead_id)
        await self.session.flush()
