from __future__ import annotations

from typing import Optional
from datetime import datetime

from sqlalchemy import String, Text, Integer, ForeignKey, Index, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import BaseModelMixin, VersionedModelMixin
from app.utils.enums import LeadSource, LeadStatus, LeadPriority


class Lead(Base, BaseModelMixin):
    """
    Lead entity — prospect for business opportunity.

    Lifecycle: NEW → CONTACTED → QUALIFIED → PROPOSAL_SENT → NEGOTIATION → CONVERTED/LOST
    """

    __tablename__ = "leads"

    # ── Basic info ────────────────────────────────────────────────────────────

    lead_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    """Auto-generated lead ID (e.g., LEAD-000001)"""

    full_name: Mapped[str] = mapped_column(String(200), index=True)
    """Lead name"""

    email: Mapped[Optional[str]] = mapped_column(String(255), index=True, nullable=True)
    """Email address"""

    phone: Mapped[Optional[str]] = mapped_column(String(20), index=True, nullable=True)
    """Phone number"""

    # ── Source & Classification ────────────────────────────────────────────────

    source: Mapped[str] = mapped_column(String(50), index=True)
    """Where lead came from (enum: walk_in, phone, email, etc.)"""

    status: Mapped[str] = mapped_column(String(50), index=True, default=LeadStatus.NEW.value)
    """Current lifecycle status"""

    priority: Mapped[str] = mapped_column(String(50), index=True, default=LeadPriority.MEDIUM.value)
    """Lead priority level"""

    # ── Assignment ─────────────────────────────────────────────────────────────

    assigned_to_user_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True
    )
    """Assigned sales person"""

    assignment_date: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    """When was this lead assigned"""

    # ── Details ────────────────────────────────────────────────────────────────

    company_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    """Company lead works for"""

    designation: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    """Job title"""

    budget: Mapped[Optional[int]] = mapped_column(nullable=True)
    """Estimated budget (in paise)"""

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    """Internal notes"""

    # ── Interest ───────────────────────────────────────────────────────────────

    interested_in_project: Mapped[Optional[str]] = mapped_column(
        ForeignKey("projects.id", ondelete="SET NULL"), index=True, nullable=True
    )
    """Project lead is interested in"""

    preferred_unit_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    """Preferred unit type (1bhk, 2bhk, etc.)"""

    # ── Activity tracking ──────────────────────────────────────────────────────

    last_contacted_at: Mapped[Optional[datetime]] = mapped_column(index=True, nullable=True)
    """Last contact date"""

    last_activity_at: Mapped[Optional[datetime]] = mapped_column(index=True, nullable=True)
    """Last activity (call, email, etc.)"""

    next_followup_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    """Scheduled next followup"""

    conversion_date: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    """Date converted to customer"""

    lost_reason: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    """Reason marked as lost"""

    # ── Relationships ─────────────────────────────────────────────────────────

    activities: Mapped[list[LeadActivity]] = relationship(
        back_populates="lead",
        cascade="all, delete-orphan",
        foreign_keys="LeadActivity.lead_id",
    )
    """Lead activities (calls, emails, meetings)"""

    followups: Mapped[list] = relationship(
        back_populates="lead",
        cascade="all, delete-orphan",
        foreign_keys="FollowUp.lead_id",
    )
    """Lead follow-ups"""

    assigned_user: Mapped[Optional[object]] = relationship("User", foreign_keys=[assigned_to_user_id])
    """Sales person assigned to lead"""

    interested_project: Mapped[Optional[object]] = relationship("Project", foreign_keys=[interested_in_project])
    """Interested project"""

    __table_args__ = (
        Index("ix_leads_status_created_at", "status", "created_at"),
        Index("ix_leads_source_created_at", "source", "created_at"),
        Index("ix_leads_assigned_to_user_id_status", "assigned_to_user_id", "status"),
    )

    def __repr__(self) -> str:
        return f"<Lead {self.lead_number} - {self.full_name}>"


class LeadActivity(Base, BaseModelMixin):
    """
    Activity log for a lead.

    Tracks interactions: calls, emails, meetings, site visits, notes, etc.
    """

    __tablename__ = "lead_activities"

    # ── Lead reference ────────────────────────────────────────────────────────

    lead_id: Mapped[str] = mapped_column(ForeignKey("leads.id", ondelete="CASCADE"), index=True)
    """Parent lead"""

    # ── Activity details ──────────────────────────────────────────────────────

    activity_type: Mapped[str] = mapped_column(String(50), index=True)
    """Type: phone_call, email, in_person, site_visit, etc."""

    subject: Mapped[str] = mapped_column(String(255))
    """Activity subject/title"""

    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    """Detailed notes"""

    outcome: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    """Result of activity"""

    # ── Actor ──────────────────────────────────────────────────────────────────

    performed_by_user_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True
    )
    """User who performed the activity"""

    # ── Timeline ───────────────────────────────────────────────────────────────

    activity_date: Mapped[datetime] = mapped_column(index=True)
    """When the activity occurred"""

    next_followup: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    """Scheduled next followup"""

    # ── Relationships ─────────────────────────────────────────────────────────

    lead: Mapped[Lead] = relationship(back_populates="activities")
    performed_by: Mapped[Optional[object]] = relationship("User", foreign_keys=[performed_by_user_id])

    __table_args__ = (Index("ix_lead_activities_lead_id_date", "lead_id", "activity_date"),)

    def __repr__(self) -> str:
        return f"<LeadActivity {self.id} - {self.activity_type}>"


class LeadAssignment(Base, BaseModelMixin):
    """
    Assignment history for leads.

    Tracks who was assigned to a lead and when.
    """

    __tablename__ = "lead_assignments"

    # ── Assignment details ────────────────────────────────────────────────────

    lead_id: Mapped[str] = mapped_column(ForeignKey("leads.id", ondelete="CASCADE"), index=True)
    """Lead being assigned"""

    assigned_to_user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    """User assigned to lead"""

    assigned_by_user_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    """User who made the assignment"""

    assigned_at: Mapped[datetime] = mapped_column(index=True)
    """Assignment timestamp"""

    unassigned_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    """When reassigned to another user"""

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    """Assignment notes/reason"""

    def __repr__(self) -> str:
        return f"<LeadAssignment {self.lead_id} → {self.assigned_to_user_id}>"
