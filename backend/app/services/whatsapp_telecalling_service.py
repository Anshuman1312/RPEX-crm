"""
Service layer for WhatsApp messaging and telecalling operations.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, desc, asc, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.core.exceptions import NotFoundException, ValidationException
from app.models.whatsapp_telecalling import (
    WhatsAppTemplate, WhatsAppInteraction, TelecallingScript, TelecallingCall
)
from app.repositories.base import BaseRepository


# ── Repositories ──────────────────────────────────────────────────────

class WhatsAppTemplateRepository(BaseRepository[WhatsAppTemplate]):
    async def get_by_name(self, name: str) -> Optional[WhatsAppTemplate]:
        q = select(WhatsAppTemplate).where(
            and_(WhatsAppTemplate.name == name, WhatsAppTemplate.is_deleted == False)
        )
        return (await self.session.execute(q)).scalars().first()

    async def list_active(self) -> List[WhatsAppTemplate]:
        q = select(WhatsAppTemplate).where(
            and_(WhatsAppTemplate.is_active == True, WhatsAppTemplate.is_deleted == False)
        ).order_by(asc(WhatsAppTemplate.name))
        return (await self.session.execute(q)).scalars().all()


class WhatsAppInteractionRepository(BaseRepository[WhatsAppInteraction]):
    async def get_by_external_id(self, external_id: str) -> Optional[WhatsAppInteraction]:
        q = select(WhatsAppInteraction).where(WhatsAppInteraction.external_message_id == external_id)
        return (await self.session.execute(q)).scalars().first()

    async def list_for_lead(self, lead_id: UUID, skip: int = 0, limit: int = 50) -> Tuple[List[WhatsAppInteraction], int]:
        filters = and_(WhatsAppInteraction.lead_id == lead_id, WhatsAppInteraction.is_deleted == False)
        total = (await self.session.execute(select(func.count(WhatsAppInteraction.id)).where(filters))).scalar() or 0
        rows = (await self.session.execute(
            select(WhatsAppInteraction).where(filters).order_by(desc(WhatsAppInteraction.created_at)).offset(skip).limit(limit)
        )).scalars().all()
        return rows, total

    async def list_for_customer(self, customer_id: UUID, skip: int = 0, limit: int = 50) -> Tuple[List[WhatsAppInteraction], int]:
        filters = and_(WhatsAppInteraction.customer_id == customer_id, WhatsAppInteraction.is_deleted == False)
        total = (await self.session.execute(select(func.count(WhatsAppInteraction.id)).where(filters))).scalar() or 0
        rows = (await self.session.execute(
            select(WhatsAppInteraction).where(filters).order_by(desc(WhatsAppInteraction.created_at)).offset(skip).limit(limit)
        )).scalars().all()
        return rows, total

    async def list_with_filter(
        self, lead_id: Optional[UUID] = None, customer_id: Optional[UUID] = None,
        direction: Optional[str] = None, status: Optional[str] = None,
        phone_number: Optional[str] = None, skip: int = 0, limit: int = 50,
    ) -> Tuple[List[WhatsAppInteraction], int]:
        filters = [WhatsAppInteraction.is_deleted == False]
        if lead_id:
            filters.append(WhatsAppInteraction.lead_id == lead_id)
        if customer_id:
            filters.append(WhatsAppInteraction.customer_id == customer_id)
        if direction:
            filters.append(WhatsAppInteraction.direction == direction)
        if status:
            filters.append(WhatsAppInteraction.status == status)
        if phone_number:
            filters.append(WhatsAppInteraction.phone_number == phone_number)
        where = and_(*filters)
        total = (await self.session.execute(select(func.count(WhatsAppInteraction.id)).where(where))).scalar() or 0
        rows = (await self.session.execute(
            select(WhatsAppInteraction).where(where).order_by(desc(WhatsAppInteraction.created_at)).offset(skip).limit(limit)
        )).scalars().all()
        return rows, total

    async def get_stats(self) -> dict:
        total_sent = (await self.session.execute(
            select(func.count(WhatsAppInteraction.id)).where(WhatsAppInteraction.direction == "OUTBOUND")
        )).scalar() or 0
        total_received = (await self.session.execute(
            select(func.count(WhatsAppInteraction.id)).where(WhatsAppInteraction.direction == "INBOUND")
        )).scalar() or 0
        delivered = (await self.session.execute(
            select(func.count(WhatsAppInteraction.id)).where(WhatsAppInteraction.status == "DELIVERED")
        )).scalar() or 0
        read = (await self.session.execute(
            select(func.count(WhatsAppInteraction.id)).where(WhatsAppInteraction.status == "READ")
        )).scalar() or 0
        failed = (await self.session.execute(
            select(func.count(WhatsAppInteraction.id)).where(WhatsAppInteraction.status == "FAILED")
        )).scalar() or 0
        delivery_rate = (delivered / total_sent * 100) if total_sent else 0
        read_rate = (read / total_sent * 100) if total_sent else 0
        return {
            "total_sent": total_sent, "total_received": total_received,
            "delivered_count": delivered, "read_count": read, "failed_count": failed,
            "delivery_rate": round(delivery_rate, 2), "read_rate": round(read_rate, 2),
        }


class TelecallingScriptRepository(BaseRepository[TelecallingScript]):
    async def list_active(self) -> List[TelecallingScript]:
        q = select(TelecallingScript).where(
            and_(TelecallingScript.is_active == True, TelecallingScript.is_deleted == False)
        ).order_by(asc(TelecallingScript.name))
        return (await self.session.execute(q)).scalars().all()


class TelecallingCallRepository(BaseRepository[TelecallingCall]):
    async def list_with_filter(
        self, agent_id: Optional[UUID] = None, lead_id: Optional[UUID] = None,
        customer_id: Optional[UUID] = None, direction: Optional[str] = None,
        call_status: Optional[str] = None, outcome: Optional[str] = None,
        followup_required: Optional[bool] = None, skip: int = 0, limit: int = 50,
    ) -> Tuple[List[TelecallingCall], int]:
        filters = [TelecallingCall.is_deleted == False]
        if agent_id:
            filters.append(TelecallingCall.agent_user_id == agent_id)
        if lead_id:
            filters.append(TelecallingCall.lead_id == lead_id)
        if customer_id:
            filters.append(TelecallingCall.customer_id == customer_id)
        if direction:
            filters.append(TelecallingCall.direction == direction)
        if call_status:
            filters.append(TelecallingCall.call_status == call_status)
        if outcome:
            filters.append(TelecallingCall.outcome == outcome)
        if followup_required is not None:
            filters.append(TelecallingCall.followup_required == followup_required)
        where = and_(*filters)
        total = (await self.session.execute(select(func.count(TelecallingCall.id)).where(where))).scalar() or 0
        rows = (await self.session.execute(
            select(TelecallingCall).where(where).order_by(desc(TelecallingCall.initiated_at)).offset(skip).limit(limit)
        )).scalars().all()
        return rows, total

    async def get_stats(self) -> dict:
        total = (await self.session.execute(
            select(func.count(TelecallingCall.id)).where(TelecallingCall.is_deleted == False)
        )).scalar() or 0
        outbound = (await self.session.execute(
            select(func.count(TelecallingCall.id)).where(
                and_(TelecallingCall.direction == "OUTBOUND", TelecallingCall.is_deleted == False)
            )
        )).scalar() or 0
        inbound = total - outbound
        answered = (await self.session.execute(
            select(func.count(TelecallingCall.id)).where(
                and_(TelecallingCall.call_status == "COMPLETED", TelecallingCall.is_deleted == False)
            )
        )).scalar() or 0
        no_answer = (await self.session.execute(
            select(func.count(TelecallingCall.id)).where(
                and_(TelecallingCall.call_status == "NO_ANSWER", TelecallingCall.is_deleted == False)
            )
        )).scalar() or 0
        followup_count = (await self.session.execute(
            select(func.count(TelecallingCall.id)).where(
                and_(TelecallingCall.followup_required == True, TelecallingCall.is_deleted == False)
            )
        )).scalar() or 0
        avg_duration = (await self.session.execute(
            select(func.avg(TelecallingCall.duration_seconds)).where(
                and_(TelecallingCall.duration_seconds.isnot(None), TelecallingCall.is_deleted == False)
            )
        )).scalar()

        by_outcome_q = select(TelecallingCall.outcome, func.count(TelecallingCall.id)).where(
            and_(TelecallingCall.outcome.isnot(None), TelecallingCall.is_deleted == False)
        ).group_by(TelecallingCall.outcome)
        by_outcome = dict((await self.session.execute(by_outcome_q)).all())

        return {
            "total_calls": total, "outbound_calls": outbound, "inbound_calls": inbound,
            "answered_calls": answered, "no_answer_calls": no_answer,
            "average_duration_seconds": float(avg_duration) if avg_duration else None,
            "by_outcome": by_outcome, "calls_requiring_followup": followup_count,
        }


# ── Services ──────────────────────────────────────────────────────────

class WhatsAppService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.template_repo = WhatsAppTemplateRepository(session)
        self.interaction_repo = WhatsAppInteractionRepository(session)

    async def send_message(
        self, phone_number: str, message_type: str, sent_by_user_id: UUID,
        lead_id: Optional[UUID] = None, customer_id: Optional[UUID] = None,
        message_body: Optional[str] = None, template_id: Optional[UUID] = None,
        template_variables: Optional[List[str]] = None, media_url: Optional[str] = None,
    ) -> WhatsAppInteraction:
        interaction = WhatsAppInteraction(
            phone_number=phone_number,
            direction="OUTBOUND",
            message_type=message_type,
            message_body=message_body,
            lead_id=lead_id,
            customer_id=customer_id,
            sent_by_user_id=sent_by_user_id,
            template_id=template_id,
            template_variables=template_variables or [],
            media_url=media_url,
            status="PENDING",
        )
        self.session.add(interaction)
        await self.session.flush()
        # TODO: integrate with actual WhatsApp Business API provider
        logger.info(f"WhatsApp message queued | phone={phone_number} | type={message_type}")
        return interaction

    async def handle_webhook(self, payload: dict) -> WhatsAppInteraction:
        """Handle inbound message from provider webhook."""
        interaction = WhatsAppInteraction(
            phone_number=payload.get("phone_number", ""),
            direction="INBOUND",
            message_type=payload.get("message_type", "TEXT"),
            message_body=payload.get("message_body"),
            media_url=payload.get("media_url"),
            external_message_id=payload.get("external_message_id"),
            status="RECEIVED",
        )
        self.session.add(interaction)
        await self.session.flush()
        logger.info(f"WhatsApp inbound received | phone={interaction.phone_number}")
        return interaction

    async def update_delivery_status(
        self, external_message_id: str, status: str,
        timestamp: Optional[datetime] = None, error_message: Optional[str] = None,
    ) -> WhatsAppInteraction:
        interaction = await self.interaction_repo.get_by_external_id(external_message_id)
        if not interaction:
            raise NotFoundException(f"WhatsApp message {external_message_id} not found")
        interaction.status = status
        if status == "DELIVERED" and timestamp:
            interaction.delivered_at = timestamp
        elif status == "READ" and timestamp:
            interaction.read_at = timestamp
        if error_message:
            interaction.error_message = error_message
        return interaction

    async def list_interactions(self, **kwargs) -> Tuple[List[WhatsAppInteraction], int]:
        return await self.interaction_repo.list_with_filter(**kwargs)

    async def get_stats(self) -> dict:
        return await self.interaction_repo.get_stats()

    # Template management
    async def create_template(self, **kwargs) -> WhatsAppTemplate:
        existing = await self.template_repo.get_by_name(kwargs.get("name", ""))
        if existing:
            raise ValidationException(f"Template '{kwargs.get('name')}' already exists")
        template = WhatsAppTemplate(**kwargs)
        self.session.add(template)
        await self.session.flush()
        return template

    async def list_templates(self, active_only: bool = True) -> List[WhatsAppTemplate]:
        if active_only:
            return await self.template_repo.list_active()
        q = select(WhatsAppTemplate).where(WhatsAppTemplate.is_deleted == False)
        return (await self.session.execute(q)).scalars().all()


class TelecallingService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.script_repo = TelecallingScriptRepository(session)
        self.call_repo = TelecallingCallRepository(session)

    async def log_call(
        self, phone_number: str, direction: str, agent_user_id: UUID,
        lead_id: Optional[UUID] = None, customer_id: Optional[UUID] = None,
        script_id: Optional[UUID] = None, notes: Optional[str] = None,
    ) -> TelecallingCall:
        call = TelecallingCall(
            phone_number=phone_number,
            direction=direction,
            agent_user_id=agent_user_id,
            lead_id=lead_id,
            customer_id=customer_id,
            script_id=script_id,
            notes=notes,
            call_status="INITIATED",
            initiated_at=datetime.utcnow(),
        )
        self.session.add(call)
        await self.session.flush()
        logger.info(f"Call logged | phone={phone_number} | direction={direction} | agent={agent_user_id}")
        return call

    async def update_call(self, call_id: UUID, **kwargs) -> TelecallingCall:
        call = await self.call_repo.get(call_id)
        if not call:
            raise NotFoundException(f"Call {call_id} not found")
        allowed = {
            "call_status", "outcome", "notes", "duration_seconds",
            "next_call_date", "followup_required", "call_recording_url",
            "answered_at", "ended_at",
        }
        for key, value in kwargs.items():
            if key in allowed and value is not None:
                setattr(call, key, value)
        return call

    async def get_call(self, call_id: UUID) -> TelecallingCall:
        call = await self.call_repo.get(call_id)
        if not call:
            raise NotFoundException(f"Call {call_id} not found")
        return call

    async def list_calls(self, **kwargs) -> Tuple[List[TelecallingCall], int]:
        return await self.call_repo.list_with_filter(**kwargs)

    async def get_stats(self) -> dict:
        return await self.call_repo.get_stats()

    async def create_script(self, created_by_user_id: UUID, **kwargs) -> TelecallingScript:
        script = TelecallingScript(created_by_user_id=created_by_user_id, **kwargs)
        self.session.add(script)
        await self.session.flush()
        return script

    async def list_scripts(self) -> List[TelecallingScript]:
        return await self.script_repo.list_active()
