from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser, require_permissions
from app.core.permissions import PERMISSIONS
from app.database.postgres import get_db
from app.repositories.project_repository import ProjectRepository
from app.schemas.project import ProjectCreate
from app.services.project_service import ProjectService

router = APIRouter()


@router.post("", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_PROJECTS}))])
async def create_project(payload: ProjectCreate, current_user: CurrentUser, db: AsyncSession = Depends(get_db)):
    project = await ProjectService(ProjectRepository(db)).create(payload.model_dump(), str(current_user.id))
    available_inventory = max(project.total_inventory - project.sold_inventory, 0)
    return {
        "id": str(project.id),
        "name": project.name,
        "project_status": project.project_status,
        "available_inventory": available_inventory,
    }


@router.get("", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_PROJECTS}))])
async def list_projects(_: CurrentUser, db: AsyncSession = Depends(get_db)):
    projects = await ProjectRepository(db).list_all()
    response = []
    for project in projects:
        available_inventory = max(project.total_inventory - project.sold_inventory, 0)
        response.append(
            {
                "id": str(project.id),
                "name": project.name,
                "developer_name": project.developer_name,
                "sole_selling_partner": project.sole_selling_partner,
                "location": project.location,
                "google_maps_url": project.google_maps_url,
                "project_status": project.project_status,
                "total_inventory": project.total_inventory,
                "sold_inventory": project.sold_inventory,
                "available_inventory": available_inventory,
                "price_list": project.price_list,
                "payment_plans": project.payment_plans,
                "documents": project.documents,
                "gallery": project.gallery,
                "videos": project.videos,
                "brochure": project.brochure,
                "legal_status": project.legal_status,
                "amenities": project.amenities,
                "nearby_landmarks": project.nearby_landmarks,
                "created_at": project.created_at,
                "updated_at": project.updated_at,
                "created_by": str(project.created_by),
            }
        )

    return response
