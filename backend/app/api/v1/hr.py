from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser, require_permissions
from app.core.permissions import PERMISSIONS
from app.database.postgres import get_db
from app.repositories.hr_repository import HRRepository
from app.schemas.hr import HREmployeeCreate, HRRecordCreate
from app.services.hr_service import HRService

router = APIRouter()


@router.post("/employees", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_HR}))])
async def create_employee(payload: HREmployeeCreate, _: CurrentUser, db: AsyncSession = Depends(get_db)):
    row = await HRService(HRRepository(db)).create_employee(payload.model_dump())
    return {"id": str(row.id), "full_name": row.full_name}


@router.get("/employees", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_HR}))])
async def list_employees(_: CurrentUser, db: AsyncSession = Depends(get_db), limit: int = Query(default=100, ge=1, le=500)):
    rows = await HRRepository(db).list_employees(limit=limit)
    return [
        {
            "id": str(row.id),
            "user_id": str(row.user_id) if row.user_id else None,
            "full_name": row.full_name,
            "department": row.department,
            "designation": row.designation,
            "salary": row.salary,
            "incentives": row.incentives,
            "performance_score": row.performance_score,
        }
        for row in rows
    ]


@router.post("/records", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_HR}))])
async def create_record(payload: HRRecordCreate, _: CurrentUser, db: AsyncSession = Depends(get_db)):
    row = await HRService(HRRepository(db)).create_record(payload.model_dump())
    return {"id": str(row.id), "record_type": row.record_type}


@router.get("/records", dependencies=[Depends(require_permissions({PERMISSIONS.MANAGE_HR}))])
async def list_records(_: CurrentUser, db: AsyncSession = Depends(get_db), limit: int = Query(default=200, ge=1, le=500)):
    rows = await HRRepository(db).list_records(limit=limit)
    return [
        {
            "id": str(row.id),
            "employee_id": str(row.employee_id),
            "record_type": row.record_type,
            "record_date": row.record_date,
            "status": row.status,
            "details": row.details,
        }
        for row in rows
    ]
