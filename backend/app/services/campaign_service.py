from __future__ import annotations

from typing import Any

from app.models.campaign import Campaign
from app.repositories.campaign_repository import CampaignRepository


class CampaignService:
    def __init__(self, repo: CampaignRepository):
        self.repo = repo

    async def create(self, payload: dict[str, Any], created_by_user_id: str | None = None) -> Campaign:
        return await self.repo.create(payload, created_by_user_id)
