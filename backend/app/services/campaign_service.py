from app.models.campaign import Campaign
from app.repositories.campaign_repository import CampaignRepository


class CampaignService:
    def __init__(self, repo: CampaignRepository):
        self.repo = repo

    async def create(self, payload: dict, user_id: str) -> Campaign:
        campaign = Campaign(**payload, created_by=user_id)
        return await self.repo.create(campaign)
