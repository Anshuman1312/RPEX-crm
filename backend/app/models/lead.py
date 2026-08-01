from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from datetime import datetime

from sqlalchemy import String, Text, Integer, ForeignKey, Index, Boolean, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import BaseModelMixin, VersionedModelMixin
from app.utils.enums import LeadSource, LeadStatus, LeadPriority

if TYPE_CHECKING:
    from app.models.followup import FollowUp


class Lead(Base, BaseModelMixin):
    """
    Lead entity — prospect for business opportunity.

    Lifecycle: NEW → CONTACTED → QUALIFIED → PROPOSAL_SENT → NEGOTIATION → CONVERTED/LOST
    """

    __tablename__ = "leads"

    # ── Basic info ────────────────────────────────────────────────────────────

    lead_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    """Auto-generated lead ID (e.g., LEAD-000001)"""

    # ── Client Details ────────────────────────────────────────────────────────
    
    title: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    """Title: Mr, Miss, Mrs, Ms, Dr, Prof"""

    full_name: Mapped[str] = mapped_column(String(200), index=True)
    """Lead name"""

    phone: Mapped[Optional[str]] = mapped_column(String(20), index=True, nullable=True)
    """Primary phone number"""

    alternate_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    """Alternate phone number"""

    email: Mapped[Optional[str]] = mapped_column(String(255), index=True, nullable=True)
    """Email address"""

    occupation: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    """Occupation/profession"""

    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    """Residential address"""

    # ── Source & Classification ────────────────────────────────────────────────

    source: Mapped[str] = mapped_column(String(50), index=True)
    """Where lead came from (enum: walk_in, phone, email, etc.)"""

    campaign_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("campaigns.id", ondelete="SET NULL"), index=True, nullable=True
    )
    """Marketing campaign source reference"""

    status: Mapped[str] = mapped_column(String(50), index=True, default=LeadStatus.NEW.value)
    """Current lifecycle status"""

    priority: Mapped[str] = mapped_column(String(50), index=True, default=LeadPriority.MEDIUM.value)
    """Lead priority level: hot (🔥), warm (🟡), cold (🔵)"""

    # ── Assignment ─────────────────────────────────────────────────────────────

    assigned_to_user_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True
    )
    """Assigned sales person"""

    assignment_date: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    """When was this lead assigned"""

    # ── Budget & Time Duration ────────────────────────────────────────────────

    budget_min: Mapped[Optional[int]] = mapped_column(nullable=True)
    """Minimum budget range (in paise)"""

    budget_max: Mapped[Optional[int]] = mapped_column(nullable=True)
    """Maximum budget range (in paise)"""

    budget: Mapped[Optional[int]] = mapped_column(nullable=True)
    """Estimated budget (in paise) - for backward compatibility"""

    time_duration: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    """Timeline for purchase: immediate, 3-6 months, 6-12 months, 1+ year"""

    # ── Purpose & Property Details ────────────────────────────────────────────

    purpose: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    """Purpose: investment, self_use, business"""

    property_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    """Property type interested in: plot, villa, flat, commercial"""

    # ── Details ────────────────────────────────────────────────────────────────

    company_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    """Company lead works for"""

    designation: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    """Job title"""

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    """Internal remarks/notes"""

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

    activities: Mapped[list["LeadActivity"]] = relationship(
        back_populates="lead",
        cascade="all, delete-orphan",
        foreign_keys="LeadActivity.lead_id",
    )
    """Lead activities (calls, emails, meetings)"""

    followups: Mapped[list["FollowUp"]] = relationship(
        "FollowUp",
        back_populates="lead",
        cascade="all, delete-orphan",
        foreign_keys="FollowUp.lead_id",
    )
    """Lead follow-ups"""

    assigned_user: Mapped[Optional[object]] = relationship("User", foreign_keys=[assigned_to_user_id])
    """Sales person assigned to lead"""

    campaign: Mapped[Optional[object]] = relationship("Campaign", back_populates="leads", foreign_keys=[campaign_id])
    """Associated marketing campaign"""

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
