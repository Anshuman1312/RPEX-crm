from app.repositories.whatsapp_repository import WhatsAppRepository


class WhatsAppService:
    def __init__(self, repo: WhatsAppRepository):
        self.repo = repo

    async def create_template(self, payload: dict):
        return await self.repo.create_template(payload)

    async def create_interaction(self, payload: dict):
        return await self.repo.create_interaction(payload)
