import types

import pytest
from fastapi import HTTPException

from app.core.deps import require_permissions


@pytest.mark.asyncio
async def test_require_permissions_allows_when_subset_present():
    guard = require_permissions({"view_leads", "edit_leads"})
    current_user = types.SimpleNamespace(id="u1")

    result = await guard(current_user=current_user, permissions={"view_leads", "edit_leads", "export_reports"})
    assert result.id == "u1"


@pytest.mark.asyncio
async def test_require_permissions_denies_when_missing():
    guard = require_permissions({"manage_users"})
    current_user = types.SimpleNamespace(id="u1")

    with pytest.raises(HTTPException) as exc:
        await guard(current_user=current_user, permissions={"view_leads"})

    assert exc.value.status_code == 403
    assert exc.value.detail == "Insufficient permissions"
