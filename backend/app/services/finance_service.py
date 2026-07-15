from app.repositories.audit_repository import AuditRepository
from app.repositories.finance_repository import FinanceRepository


class FinanceService:
    def __init__(self, repo: FinanceRepository, audit_repo: AuditRepository):
        self.repo = repo
        self.audit_repo = audit_repo

    async def create_payment(self, payload: dict, actor_user_id: str):
        row = await self.repo.create_payment(payload)
        await self.audit_repo.log(
            actor_user_id,
            "finance",
            "payment_create",
            None,
            {"id": str(row.id), "customer_id": str(row.customer_id), "amount": str(row.amount)},
        )
        return row

    async def create_invoice(self, payload: dict, actor_user_id: str):
        row = await self.repo.create_invoice(payload)
        await self.audit_repo.log(
            actor_user_id,
            "finance",
            "invoice_create",
            None,
            {"id": str(row.id), "invoice_number": row.invoice_number, "amount": str(row.amount)},
        )
        return row
