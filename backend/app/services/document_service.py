from __future__ import annotations

from typing import Any

from app.repositories.audit_repository import AuditRepository
from app.repositories.document_repository import DocumentRepository


class DocumentService:
    def __init__(self, repo: DocumentRepository, audit_repo: AuditRepository):
        self.repo = repo
        self.audit_repo = audit_repo

    async def create_document(self, payload: dict[str, Any], actor_user_id: str):
        row = await self.repo.create_document(payload)
        await self.audit_repo.create(
            user_id=payload.get("uploaded_by") or actor_user_id,
            action="document.created",
            entity_type="document",
            entity_id=row.id,
            entity_display=row.file_name,
            description=f"Document {row.file_name} created",
            new_value={
                "id": str(row.id),
                "category": row.category,
                "storage_key": row.storage_key,
            },
            extra_data={"category": row.category},
        )
        return row
