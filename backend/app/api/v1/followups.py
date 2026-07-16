from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser, require_permissions
from app.core.permissions import PERMISSIONS
from app.database.postgres import get_db
from app.repositories.followup_repository import FollowUpRepository
from app.schemas.followup import FollowUpCreate, FollowUpUpdate

router = APIRouter()


@router.post("", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_FOLLOWUPS}))])
async def create_followup(payload: FollowUpCreate, _: CurrentUser, db: AsyncSession = Depends(get_db)):
    data = payload.model_dump()
    history_entry = {
        "at": datetime.now(timezone.utc).isoformat(),
        "action": "created",
        "status": data.get("status", "PENDING"),
        "remark": data.get("remark"),
    }
    data["followup_history"] = [history_entry]
    followup = await FollowUpRepository(db).create(data)
    return {"id": str(followup.id), "status": followup.status, "auto_reminder_enabled": followup.auto_reminder_enabled}


@router.get("", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_FOLLOWUPS}))])
async def list_followups(current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    items = await FollowUpRepository(db).list_by_assignee(str(current_user.id))
    return [
        {
            "id": str(item.id),
            "lead_id": str(item.lead_id),
            "assigned_to": str(item.assigned_to),
            "followup_date": item.followup_date,
            "next_followup_date": item.next_followup_date,
            "remark": item.remark,
            "call_notes": item.call_notes,
            "whatsapp_notes": item.whatsapp_notes,
            "meeting_notes": item.meeting_notes,
            "voice_recording_url": item.voice_recording_url,
            "sms_log": item.sms_log,
            "followup_history": item.followup_history,
            "auto_reminder_enabled": item.auto_reminder_enabled,
            "status": item.status,
        }
        for item in items
    ]


@router.patch("/{followup_id}", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_FOLLOWUPS}))])
async def update_followup(
    followup_id: str,
    payload: FollowUpUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    repo = FollowUpRepository(db)
    followup = await repo.get_by_id(followup_id)
    if not followup:
        return {"updated": False, "detail": "Follow-up not found"}

    data = payload.model_dump(exclude_unset=True)
    if not data:
        return {"updated": True, "id": str(followup.id), "status": followup.status}

    current_history = list(followup.followup_history or [])
    current_history.append(
        {
            "at": datetime.now(timezone.utc).isoformat(),
            "action": "updated",
            "by": str(current_user.id),
            "changes": data,
        }
    )
    data["followup_history"] = current_history

    row = await repo.update(followup, data)
    return {"updated": True, "id": str(row.id), "status": row.status}
