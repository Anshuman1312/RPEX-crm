from app.repositories.audit_repository import AuditRepository
from app.repositories.customer_repository import CustomerRepository


class CustomerService:
    def __init__(self, repo: CustomerRepository, audit_repo: AuditRepository):
        self.repo = repo
        self.audit_repo = audit_repo

    async def create_customer(self, payload: dict, actor_user_id: str):
        row = await self.repo.create(payload)
        await self.audit_repo.log(actor_user_id, "customers", "create", None, {"id": str(row.id), "phone": row.phone})
        return row
