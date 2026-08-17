from __future__ import annotations

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db_session
from app.dependencies.auth import get_current_user, get_current_admin, require_permission
from app.models.user import User
from app.schemas.auth import UserCreate, UserUpdate, UserListResponse
from app.services.auth_service import UserService
from app.utils.response import ok, created, PaginatedResponse
from app.utils.pagination import PaginationParams, get_pagination_params
from loguru import logger

router = APIRouter()


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=dict,
)
async def create_user(
    request: UserCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """
    Create new user (SUPER_ADMIN only).
    """
    if not current_user.role or current_user.role.name.upper() != "SUPER_ADMIN":
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only SUPER_ADMIN can create CRM users."
        )

    # Auto-generate employee_code if not supplied
    employee_code = request.employee_code
    if not employee_code:
        import uuid as py_uuid
        employee_code = f"EMP-{py_uuid.uuid4().hex[:8].upper()}"

    user_service = UserService(session)

    new_user = await user_service.create_user(
        email=request.email,
        phone=request.phone,
        full_name=request.full_name,
        password=request.password,
        employee_code=employee_code,
        department_id=str(request.department_id) if request.department_id else None,
        designation_id=str(request.designation_id) if request.designation_id else None,
        role_id=str(request.role_id) if request.role_id else None,
        created_by=current_user.id,
    )

    await session.commit()

    logger.info(f"User created | user_id={new_user.id} | created_by={current_user.id}")

    # Load relations eagerly to avoid lazy loading MissingGreenlet issues
    db_user = await user_service.get_user_with_permissions(str(new_user.id))

    from app.schemas.auth import UserResponse

    return created(
        data=UserResponse.model_validate(db_user).__dict__,
        message="User created successfully.",
    )


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=PaginatedResponse,
)
async def list_users(
    search: str | None = Query(None),
    role_id: str | None = Query(None),
    department_id: str | None = Query(None),
    status: str | None = Query(None),
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("users.view")),
    pagination: PaginationParams = Depends(get_pagination_params),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """
    List all users (paginated, with search & filters).

    Requires users.view permission.
    """
    import uuid
    user_service = UserService(session)
    
    parsed_role_id = uuid.UUID(role_id) if role_id else None
    parsed_dept_id = uuid.UUID(department_id) if department_id else None
    
    users, total = await user_service.list_users(
        skip=pagination.offset,
        limit=pagination.limit,
        search=search,
        role_id=parsed_role_id,
        department_id=parsed_dept_id,
        status=status,
    )

    data = [UserListResponse.model_validate(u).__dict__ for u in users]

    return PaginatedResponse.build(
        data=data,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    ).__dict__


@router.get("/roles", status_code=status.HTTP_200_OK)
async def list_roles(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    from sqlalchemy import select
    from app.models.user import Role
    result = await session.execute(select(Role).where(Role.is_deleted == False))
    roles = result.scalars().all()
    return ok(data=[{"id": str(r.id), "name": r.name, "code": r.code} for r in roles])


@router.get("/departments", status_code=status.HTTP_200_OK)
async def list_departments(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    from sqlalchemy import select
    from app.models.user import Department
    result = await session.execute(select(Department).where(Department.is_deleted == False))
    depts = result.scalars().all()
    return ok(data=[{"id": str(d.id), "name": d.name, "code": d.code} for d in depts])


@router.get("/designations", status_code=status.HTTP_200_OK)
async def list_designations(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    from sqlalchemy import select
    from app.models.user import Designation
    result = await session.execute(select(Designation).where(Designation.is_deleted == False))
    desigs = result.scalars().all()
    return ok(data=[{"id": str(d.id), "name": d.name, "code": d.code} for d in desigs])


@router.get(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=dict,
)
async def get_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("users.view")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """
    Get user by ID.

    Requires users.view permission.
    """
    user_service = UserService(session)
    user = await user_service.get_user_with_permissions(user_id)

    if not user:
        from app.core.exceptions import NotFoundException

        raise NotFoundException("User", user_id)

    from app.schemas.auth import UserResponse

    return ok(data=UserResponse.model_validate(user).__dict__)


@router.patch(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=dict,
)
async def update_user(
    user_id: str,
    request: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """
    Update user (SUPER_ADMIN check for status & role changes).
    """
    from app.repositories.user_repository import UserRepository
    from fastapi import HTTPException

    user_repo = UserRepository(session)
    user = await user_repo.get_or_404(user_id, "User")

    # Update only provided fields
    update_data = {}
    if request.full_name:
        update_data["full_name"] = request.full_name
    if request.phone:
        update_data["phone"] = request.phone
    if request.department_id:
        update_data["department_id"] = request.department_id
    if request.designation_id:
        update_data["designation_id"] = request.designation_id
    if request.role_id:
        update_data["role_id"] = request.role_id
    if request.status:
        # Map frontend Active/Inactive to lowercase
        status_val = request.status.lower()
        if status_val == "active":
            update_data["status"] = "active"
        elif status_val in ("inactive", "suspended"):
            update_data["status"] = "inactive"

    if not update_data:
        from app.core.exceptions import ValidationException

        raise ValidationException("No fields to update.")

    # Enforce SUPER_ADMIN validation for status or role changes
    if "role_id" in update_data or "status" in update_data:
        if not current_user.role or current_user.role.name.upper() != "SUPER_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only SUPER_ADMIN can update user role or status."
            )

    user = await user_repo.update(user_id, **update_data)
    await session.commit()

    logger.info(f"User updated | user_id={user.id} | updated_by={current_user.id}")

    # Re-fetch with all relationships loaded (must be after commit to see latest state)
    user_service = UserService(session)
    db_user = await user_service.get_user_with_permissions(str(user.id))

    from app.schemas.auth import UserResponse

    return ok(data=UserResponse.model_validate(db_user).__dict__)


@router.post(
    "/{user_id}/verify",
    status_code=status.HTTP_200_OK,
    response_model=dict,
)
async def verify_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("users.verify")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """
    Verify a user account (admin only).

    Requires users.verify permission.
    """
    user_service = UserService(session)
    user = await user_service.verify_user(user_id)
    await session.flush()

    logger.info(f"User verified | user_id={user.id} | verified_by={current_user.id}")

    # Load relations eagerly to avoid lazy loading MissingGreenlet issues
    db_user = await user_service.get_user_with_permissions(str(user.id))

    from app.schemas.auth import UserResponse

    return ok(data=UserResponse.model_validate(db_user).__dict__)


@router.post(
    "/{user_id}/suspend",
    status_code=status.HTTP_200_OK,
    response_model=dict,
)
async def suspend_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("users.suspend")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """
    Suspend a user account (admin only).

    Requires users.suspend permission.
    """
    user_service = UserService(session)
    user = await user_service.suspend_user(user_id)
    await session.flush()

    logger.info(f"User suspended | user_id={user.id} | suspended_by={current_user.id}")

    # Load relations eagerly to avoid lazy loading MissingGreenlet issues
    db_user = await user_service.get_user_with_permissions(str(user.id))

    from app.schemas.auth import UserResponse

    return ok(data=UserResponse.model_validate(db_user).__dict__)
