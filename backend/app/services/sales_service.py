from __future__ import annotations

from app.repositories.audit_repository import AuditRepository
from app.repositories.sales_repository import SalesRepository


class SalesService:
    def __init__(self, repo: SalesRepository, audit_repo: AuditRepository):
        self.repo = repo
        self.audit_repo = audit_repo

    async def create_booking(self, payload: dict, actor_user_id: str):
        row = await self.repo.create_booking(payload)
        await self.audit_repo.create(
            user_id=actor_user_id,
            action="sales.booking.created",
            entity_type="sales_booking",
            entity_id=row.id,
            entity_display=row.unit_code,
            description=f"Sales booking created for {row.project_name}",
            new_value={"booking_value": str(row.booking_value), "status": row.status},
            extra_data={"project_name": row.project_name},
        )
        return row
