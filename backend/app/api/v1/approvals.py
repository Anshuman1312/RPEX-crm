from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser, require_permissions
from app.core.permissions import PERMISSIONS
from app.database.postgres import get_db
from app.repositories.approval_repository import ApprovalRepository
from app.repositories.audit_repository import AuditRepository
from app.schemas.approval import ApprovalDecision, ApprovalRequestCreate
from app.services.approval_service import ApprovalService

router = APIRouter()


@router.post("", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_FINANCE}))])
async def create_approval_request(payload: ApprovalRequestCreate, current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = ApprovalService(ApprovalRepository(db), AuditRepository(db))
    row = await service.create_request(
        {
            **payload.model_dump(),
            "requested_by": current_user.id,
            "status": "PENDING",
        },
        str(current_user.id),
    )
    return {
        "id": str(row.id),
        "module": row.module,
        "entity_type": row.entity_type,
        "entity_id": row.entity_id,
        "status": row.status,
    }


@router.get("", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_FINANCE}))])
async def list_approval_requests(
    _: CurrentUser,
    db: AsyncSession = Depends(get_db),
    status_filter: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=100, ge=1, le=500),
):
    rows = await ApprovalRepository(db).list_requests(status=status_filter, limit=limit)
    return [
        {
            "id": str(row.id),
            "module": row.module,
            "entity_type": row.entity_type,
            "entity_id": row.entity_id,
            "action": row.action,
            "status": row.status,
            "requested_by": str(row.requested_by),
            "approver_id": str(row.approver_id) if row.approver_id else None,
            "reason": row.reason,
            "created_at": row.created_at,
            "updated_at": row.updated_at,
        }
        for row in rows
    ]


@router.post("/{request_id}/decision", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_FINANCE}))])
async def approval_decision(request_id: str, payload: ApprovalDecision, current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    service = ApprovalService(ApprovalRepository(db), AuditRepository(db))
    row = await service.decide_request(request_id, payload.status, str(current_user.id))
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval request not found")
    return {
        "id": str(row.id),
        "status": row.status,
        "approver_id": str(row.approver_id) if row.approver_id else None,
    }
