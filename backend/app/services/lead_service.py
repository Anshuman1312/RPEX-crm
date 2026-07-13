from typing import Any

from app.repositories.audit_repository import AuditRepository
from app.repositories.lead_repository import LeadRepository
from app.websocket.publisher import publish_lead_event


class LeadService:
    def __init__(self, lead_repo: LeadRepository, audit_repo: AuditRepository):
        self.lead_repo = lead_repo
        self.audit_repo = audit_repo

    async def create_lead(self, payload: dict[str, Any], actor_user_id: str | None = None):
        lead = await self.lead_repo.create(payload)
        await self.audit_repo.log(actor_user_id, "leads", "create", None, {"id": str(lead.id), "status": lead.status})
        await publish_lead_event({"event": "lead_created", "lead_id": str(lead.id), "status": lead.status})
        return lead

    async def update_status(self, lead_id: str, user_id: str, status: str, description: str | None = None):
        lead = await self.lead_repo.get_by_id(lead_id)
        if not lead:
            return None
        previous = lead.status
        lead = await self.lead_repo.update_status(lead, status)
        await self.lead_repo.add_activity(lead_id, user_id, "status_change", description or f"Status changed {previous} -> {status}")
        await self.audit_repo.log(user_id, "leads", "status_update", {"status": previous}, {"status": status})
        await publish_lead_event({"event": "lead_status_updated", "lead_id": lead_id, "status": status})
        return lead
