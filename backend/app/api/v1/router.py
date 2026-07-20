from fastapi import APIRouter

from app.api.v1 import (
	analytics,
	ai,
	automation,
	approvals,
	auth,
	campaigns,
	customers,
	documents,
	finance,
	followups,
	hr,
	inventory,
	keywords,
	leads,
	partner,
	projects,
	reports,
	sales,
	sales_team,
	site_visits,
	telecalling,
	users,
	vendors,
	whatsapp,
	webhooks,
	websites,
	ws,
	dashboard,
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
api_router.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(partner.router, prefix="/partner", tags=["partner"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(site_visits.router, prefix="/site-visits", tags=["site-visits"])
api_router.include_router(telecalling.router, prefix="/telecalling", tags=["telecalling"])
api_router.include_router(sales_team.router, prefix="/sales-team", tags=["sales-team"])
api_router.include_router(hr.router, prefix="/hr", tags=["hr"])
api_router.include_router(vendors.router, prefix="/vendors", tags=["vendors"])
api_router.include_router(whatsapp.router, prefix="/whatsapp", tags=["whatsapp"])
api_router.include_router(automation.router, prefix="/automation", tags=["automation"])
api_router.include_router(ws.router, tags=["websocket"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])