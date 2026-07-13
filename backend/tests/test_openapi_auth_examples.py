from fastapi import FastAPI

from app.api.v1.auth import router


def test_auth_openapi_contains_examples():
    app = FastAPI()
    app.include_router(router, prefix="/api/v1/auth")

    schema = app.openapi()
    login_examples = schema["paths"]["/api/v1/auth/login"]["post"]["requestBody"]["content"]["application/json"]["examples"]
    refresh_examples = schema["paths"]["/api/v1/auth/refresh"]["post"]["requestBody"]["content"]["application/json"]["examples"]

    assert "default" in login_examples
    assert login_examples["default"]["value"]["email"] == "admin@rpex.local"
    assert "default" in refresh_examples
