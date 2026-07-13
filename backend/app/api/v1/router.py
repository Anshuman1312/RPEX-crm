from fastapi import APIRouter

from app.api.v1 import analytics, auth, campaigns, followups, keywords, leads, reports, users, webhooks, websites, ws

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(websites.router, prefix="/websites", tags=["websites"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
api_router.include_router(leads.router, prefix="/leads", tags=["leads"])
api_router.include_router(followups.router, prefix="/followups", tags=["followups"])
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])
api_router.include_router(keywords.router, prefix="/keywords", tags=["keywords"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(ws.router, tags=["websocket"])
