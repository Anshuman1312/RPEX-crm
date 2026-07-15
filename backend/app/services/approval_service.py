from app.repositories.approval_repository import ApprovalRepository
from app.repositories.audit_repository import AuditRepository


class ApprovalService:
    def __init__(self, repo: ApprovalRepository, audit_repo: AuditRepository):
        self.repo = repo
        self.audit_repo = audit_repo

    async def create_request(self, payload: dict, actor_user_id: str):
        row = await self.repo.create(payload)
        await self.audit_repo.log(
            actor_user_id,
            "approvals",
            "request_create",
            None,
            {
                "id": str(row.id),
                "module": row.module,
                "entity_type": row.entity_type,
                "entity_id": row.entity_id,
                "status": row.status,
            },
        )
        return row

    async def decide_request(self, request_id: str, status: str, approver_id: str):
        row = await self.repo.get_by_id(request_id)
        if not row:
            return None
        previous = row.status
        row = await self.repo.update_status(row, status=status, approver_id=approver_id)
        await self.audit_repo.log(
            approver_id,
            "approvals",
            "request_decide",
            {"status": previous},
            {"status": status, "request_id": request_id},
        )
        return row
