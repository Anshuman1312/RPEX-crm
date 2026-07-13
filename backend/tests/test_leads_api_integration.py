from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1 import leads as leads_module
from app.api.v1.leads import router
from app.core.deps import get_current_permissions, get_current_user
from app.database.postgres import get_db


class DummyLead:
    def __init__(self, idx: str):
        self.id = idx
        self.name = "Rahul"
        self.email = "rahul@example.com"
        self.phone = "9999999999"
        self.status = "NEW"
        self.source = "google"
        self.medium = "cpc"
        self.campaign_id = None
        self.assigned_to = None
        self.extra_data = {"city": "Delhi"}
        self.created_at = "2026-07-13T00:00:00Z"


def _build_test_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router, prefix="/api/v1/leads")

    async def override_db():
        yield SimpleNamespace()

    async def override_user():
        return SimpleNamespace(id="00000000-0000-0000-0000-000000000001")

    async def override_permissions():
        return {"view_leads", "edit_leads"}

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = override_user
    app.dependency_overrides[get_current_permissions] = override_permissions
    return app


def test_list_leads_with_filters(monkeypatch):
    async def fake_search(self, filters):
        assert filters["extra_field_filters"]["city"] == "Delhi"
        assert filters["sort_by"] == "created_at"
        return [DummyLead("lead-1")], 1

    monkeypatch.setattr(leads_module.LeadRepository, "search_leads", fake_search)

    app = _build_test_app()
    client = TestClient(app)
    response = client.get(
        "/api/v1/leads",
        params={
            "q": "rahul",
            "statuses": "NEW,CONTACTED",
            "extra_filters": '{"city":"Delhi"}',
            "page": 1,
            "page_size": 25,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert len(body["items"]) == 1


def test_list_leads_invalid_extra_filter_json():
    app = _build_test_app()
    client = TestClient(app)
    response = client.get("/api/v1/leads", params={"extra_filters": "{invalid-json}"})
    assert response.status_code == 400


def test_saved_views_crud(monkeypatch):
    async def fake_create(self, payload):
        return SimpleNamespace(id="view-1", name=payload["name"], is_public=payload["is_public"])

    async def fake_list(self, user_id):
        return [
            SimpleNamespace(
                id="view-1",
                user_id=user_id,
                name="My View",
                filters={"statuses": ["NEW"]},
                is_public=False,
                updated_at="2026-07-13T00:00:00Z",
            )
        ]

    async def fake_delete(self, view_id, user_id):
        return view_id == "view-1"

    monkeypatch.setattr(leads_module.LeadSavedViewRepository, "create", fake_create)
    monkeypatch.setattr(leads_module.LeadSavedViewRepository, "list_for_user", fake_list)
    monkeypatch.setattr(leads_module.LeadSavedViewRepository, "delete_for_user", fake_delete)

    app = _build_test_app()
    client = TestClient(app)

    create_res = client.post("/api/v1/leads/views", json={"name": "My View", "filters": {"statuses": ["NEW"]}, "is_public": False})
    assert create_res.status_code == 200

    list_res = client.get("/api/v1/leads/views")
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1

    delete_res = client.delete("/api/v1/leads/views/view-1")
    assert delete_res.status_code == 200
    assert delete_res.json()["deleted"] is True
