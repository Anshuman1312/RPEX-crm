from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser, require_permissions
from app.core.permissions import PERMISSIONS
from app.database.postgres import get_db
from app.repositories.followup_repository import FollowUpRepository
from app.schemas.followup import FollowUpCreate

router = APIRouter()


@router.post("", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_FOLLOWUPS}))])
async def create_followup(payload: FollowUpCreate, _: CurrentUser, db: AsyncSession = Depends(get_db)):
    followup = await FollowUpRepository(db).create(payload.model_dump())
    return {"id": str(followup.id), "status": followup.status}


@router.get("", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_FOLLOWUPS}))])
async def list_followups(current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    items = await FollowUpRepository(db).list_by_assignee(str(current_user.id))
    return [
        {
            "id": str(item.id),
            "lead_id": str(item.lead_id),
            "followup_date": item.followup_date,
            "remark": item.remark,
            "status": item.status,
        }
        for item in items
    ]
