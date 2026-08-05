from __future__ import annotations

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db_session
from app.dependencies.auth import get_current_user, get_current_admin, require_permission
from app.models.user import User, Role
from app.schemas.auth import UserCreate, UserUpdate, UserListResponse
from app.services.auth_service import UserService
from app.utils.response import ok, created, PaginatedResponse
from app.utils.pagination import PaginationParams, get_pagination_params
from loguru import logger

router = APIRouter()


@router.get(
    "/lookup",
    status_code=status.HTTP_200_OK,
    response_model=dict,
)
async def lookup_users(
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("users.view")),
    role_based: str = Query(..., description="Role code/name to filter users, e.g. SALES"),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """
    List users by role and return only user_id and user_name.

    Requires users.view permission.
    """
    role_filter = role_based.strip().upper()
    query = (
        select(User.id, User.full_name)
        .outerjoin(Role, User.role_id == Role.id)
        .where(User.is_deleted == False)
        .where(
            or_(
                Role.code == role_filter,
                Role.name == role_filter,
            )
        )
        .order_by(User.full_name.asc())
    )

    rows = (await session.execute(query)).all()
    data = [{"user_id": str(row.id), "user_name": row.full_name} for row in rows]
    return ok(data=data)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=dict,
)
async def create_user(
    request: UserCreate,
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("users.create")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """
    Create new user (admin only).

    Requires users.create permission.
    """
    user_service = UserService(session)

    new_user = await user_service.create_user(
        email=request.email,
        phone=request.phone,
        full_name=request.full_name,
        password=request.password,
        employee_code=request.employee_code,
        department_id=request.department_id,
        designation_id=request.designation_id,
        role_id=request.role_id,
    )

    await session.commit()

    logger.info(f"User created | user_id={new_user.id} | created_by={current_user.id}")

    from app.schemas.auth import UserResponse

    return created(
        data=UserResponse.model_validate(new_user).__dict__,
        message="User created successfully.",
    )


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=PaginatedResponse,
)
async def list_users(
    current_user: User = Depends(get_current_user),
    _=Depends(require_permission("users.view")),
    pagination: PaginationParams = Depends(get_pagination_params),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """
    List all users (paginated).

    Requires users.view permission.
    """
    user_service = UserService(session)
    users, total = await user_service.list_users(
        skip=pagination.offset,
        limit=pagination.limit,
    )

    data = [UserListResponse.model_validate(u).__dict__ for u in users]

    return PaginatedResponse.build(
        data=data,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    ).__dict__


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
    user = await user_service.get_user(user_id)

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
    _=Depends(require_permission("users.edit")),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """
    Update user.

    Requires users.edit permission.
    """
    from app.repositories.user_repository import UserRepository

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

    if not update_data:
        from app.core.exceptions import ValidationException

        raise ValidationException("No fields to update.")

    user = await user_repo.update(user_id, **update_data)
    await session.flush()

    logger.info(f"User updated | user_id={user.id} | updated_by={current_user.id}")

    from app.schemas.auth import UserResponse

    return ok(data=UserResponse.model_validate(user).__dict__)


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

    from app.schemas.auth import UserResponse

    return ok(data=UserResponse.model_validate(user).__dict__)


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

    from app.schemas.auth import UserResponse

    return ok(data=UserResponse.model_validate(user).__dict__)
