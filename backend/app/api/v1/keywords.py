from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser, require_permissions
from app.core.permissions import PERMISSIONS
from app.database.postgres import get_db
from app.repositories.keyword_repository import KeywordRepository
from app.schemas.seo_keyword import SEOKeywordCreate
from app.services.keyword_service import KeywordService

router = APIRouter()


@router.post("", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_KEYWORDS}))])
async def create_keyword(payload: SEOKeywordCreate, _: CurrentUser, db: AsyncSession = Depends(get_db)):
    keyword = await KeywordService(KeywordRepository(db)).create(payload.model_dump())
    return {"id": str(keyword.id), "keyword": keyword.keyword}


@router.get("", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_KEYWORDS}))])
async def list_keywords(_: CurrentUser, db: AsyncSession = Depends(get_db)):
    keywords = await KeywordRepository(db).list_all()
    return [
        {
            "id": str(k.id),
            "keyword": k.keyword,
            "url": k.url,
            "target_position": k.target_position,
            "current_position": k.current_position,
            "traffic": k.traffic,
            "clicks": k.clicks,
            "impressions": k.impressions,
        }
        for k in keywords
    ]
