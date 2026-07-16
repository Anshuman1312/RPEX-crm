from app.models.campaign import Campaign
from app.repositories.campaign_repository import CampaignRepository


class CampaignService:
    def __init__(self, repo: CampaignRepository):
        self.repo = repo

    async def create(self, payload: dict, user_id: str) -> Campaign:
        extra_data = {
            "channel": payload.pop("channel", None),
            "reach": payload.pop("reach", 0),
            "leads": payload.pop("leads", 0),
            "roas": str(payload.pop("roas", 0)),
            "conversion": str(payload.pop("conversion", 0)),
        }
        campaign = Campaign(
            **payload,
            extra_data={k: v for k, v in extra_data.items() if v not in (None, "")},
            created_by=user_id,
        )
        return await self.repo.create(campaign)
