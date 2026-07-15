from app.repositories.audit_repository import AuditRepository
from app.repositories.document_repository import DocumentRepository


class DocumentService:
    def __init__(self, repo: DocumentRepository, audit_repo: AuditRepository):
        self.repo = repo
        self.audit_repo = audit_repo

    async def create_document(self, payload: dict, actor_user_id: str):
        row = await self.repo.create(payload)
        await self.audit_repo.log(
            actor_user_id,
            "documents",
            "create",
            None,
            {"id": str(row.id), "category": row.category, "storage_key": row.storage_key},
        )
        return row
