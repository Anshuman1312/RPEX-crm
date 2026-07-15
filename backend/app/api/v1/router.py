from fastapi import APIRouter

from app.api.v1 import (
	analytics,
	approvals,
	auth,
	campaigns,
	customers,
	documents,
	finance,
	followups,
	keywords,
	leads,
	partner,
	reports,
	sales,
	users,
	webhooks,
	websites,
	ws,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(websites.router, prefix="/websites", tags=["websites"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
api_router.include_router(leads.router, prefix="/leads", tags=["leads"])
api_router.include_router(followups.router, prefix="/followups", tags=["followups"])
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])
api_router.include_router(keywords.router, prefix="/keywords", tags=["keywords"])
api_router.include_router(approvals.router, prefix="/approvals", tags=["approvals"])
api_router.include_router(customers.router, prefix="/customers", tags=["customers"])
api_router.include_router(sales.router, prefix="/sales", tags=["sales"])
api_router.include_router(finance.router, prefix="/finance", tags=["finance"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(partner.router, prefix="/partner", tags=["partner"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(ws.router, tags=["websocket"])
