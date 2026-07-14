import pytest
from fastapi import HTTPException

from app.services.auth_service import AuthService


class _StubRole:
    def __init__(self, role_id: str, name: str):
        self.id = role_id
        self.name = name


class _StubUser:
    def __init__(self, email: str):
        self.id = "u-1"
        self.email = email


class _Repo:
    def __init__(self, existing=False, valid_role=True):
        self.existing = existing
        self.valid_role = valid_role

    async def get_user_by_email(self, email: str):
        return _StubUser(email) if self.existing else None

    async def get_role_by_name(self, name: str):
        if not self.valid_role:
            return None
        return _StubRole("r-1", name)

    async def create_user(self, user):
        user.id = "u-1"
        return user


@pytest.mark.asyncio
async def test_register_user_rejects_duplicate_email():
    service = AuthService(_Repo(existing=True))
    with pytest.raises(HTTPException) as exc:
        await service.register_user("Rahul", "rahul@example.com", "StrongPass@123", "SALES")
    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_register_user_allows_admin_role():
    service = AuthService(_Repo(existing=False))
    user = await service.register_user("Rahul", "rahul@example.com", "StrongPass@123", "ADMIN")
    assert user.email == "rahul@example.com"


@pytest.mark.asyncio
async def test_register_user_success():
    service = AuthService(_Repo(existing=False, valid_role=True))
    user = await service.register_user("Rahul", "rahul@example.com", "StrongPass@123", "SALES")
    assert user.email == "rahul@example.com"


@pytest.mark.asyncio
async def test_register_user_rejects_invalid_role():
    service = AuthService(_Repo(existing=False, valid_role=False))
    with pytest.raises(HTTPException) as exc:
        await service.register_user("Rahul", "rahul@example.com", "StrongPass@123", "NOT_A_ROLE")
    assert exc.value.status_code == 400
