from app.repositories.audit_repository import AuditRepository
from app.repositories.sales_repository import SalesRepository


class SalesService:
    def __init__(self, repo: SalesRepository, audit_repo: AuditRepository):
        self.repo = repo
        self.audit_repo = audit_repo

    async def create_booking(self, payload: dict, actor_user_id: str):
        row = await self.repo.create_booking(payload)
        await self.audit_repo.log(
            actor_user_id,
            "sales",
            "booking_create",
            None,
            {
                "id": str(row.id),
                "customer_id": str(row.customer_id),
                "status": row.status,
            },
        )
        return row
