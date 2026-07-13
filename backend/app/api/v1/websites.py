from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser, require_permissions
from app.core.permissions import PERMISSIONS
from app.database.postgres import get_db
from app.repositories.website_repository import WebsiteRepository
from app.schemas.website import WebsiteCreate

router = APIRouter()


@router.post("", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_WEBSITES}))])
async def create_website(payload: WebsiteCreate, _: CurrentUser, db: AsyncSession = Depends(get_db)):
    website = await WebsiteRepository(db).create(payload.name, payload.domain, payload.status)
    return {"id": str(website.id), "api_key": website.api_key, "domain": website.domain}


@router.get("", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_WEBSITES}))])
async def list_websites(_: CurrentUser, db: AsyncSession = Depends(get_db)):
    websites = await WebsiteRepository(db).list_all()
    return [{"id": str(w.id), "name": w.name, "domain": w.domain, "status": w.status} for w in websites]
