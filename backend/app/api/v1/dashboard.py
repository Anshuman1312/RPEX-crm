from fastapi import APIRouter, Depends
from app.core import deps
from app.services.dashboard_service import DashboardService

router = APIRouter()

@router.get("/overview")
async def get_dashboard_overview(
    service: DashboardService = Depends(deps.get_dashboard_service)
):
    return await service.get_business_dashboard()