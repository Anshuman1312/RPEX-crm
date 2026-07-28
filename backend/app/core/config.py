from __future__ import annotations

from functools import lru_cache
from typing import Any, Literal

from pydantic import computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ── Application ───────────────────────────────────────────────────────────
    APP_NAME: str = "RPEX CRM"
    APP_ENV: Literal["development", "staging", "production"] = "development"
    APP_VERSION: str = "1.0.0"
    APP_DEBUG: bool = False
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    SECRET_KEY: str = "dev-secret-key-please-change-in-production-min-32!!"
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # ── Database ──────────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/rpex_crm"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 40
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RECYCLE: int = 3600

    # ── Redis ─────────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_DB: int = 1
    REDIS_SESSION_DB: int = 2
    REDIS_CELERY_DB: int = 3
    REDIS_RATE_LIMIT_DB: int = 4
    REDIS_MAX_CONNECTIONS: int = 50

    # ── JWT ───────────────────────────────────────────────────────────────────
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    REFRESH_TOKEN_ROTATE: bool = True

    # ── Celery ────────────────────────────────────────────────────────────────
    CELERY_BROKER_URL: str = "redis://localhost:6379/3"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/3"
    CELERY_TASK_ALWAYS_EAGER: bool = False

    # ── Rate Limiting ─────────────────────────────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 100
    AUTH_RATE_LIMIT_PER_MINUTE: int = 10
    ENABLE_RATE_LIMITING: bool = True

    # ── Field Encryption (AES-256 for Aadhaar, etc.) ─────────────────────────
    FIELD_ENCRYPTION_KEY: str = "dev-field-encryption-key-change-in-production!!"

    # ── Logging ───────────────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_FILE_PATH: str = "logs/app.log"

    # ── Email (SMTP) ──────────────────────────────────────────────────────────
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_NAME: str = "RPEX CRM"
    SMTP_FROM_EMAIL: str = "noreply@rpex.com"
    SMTP_USE_TLS: bool = True

    # ── SMS ───────────────────────────────────────────────────────────────────
    SMS_PROVIDER: str = "twilio"
    SMS_API_KEY: str = ""
    SMS_API_SECRET: str = ""
    SMS_FROM_NUMBER: str = ""

    # ── Pagination ────────────────────────────────────────────────────────────
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # ── Feature Flags ─────────────────────────────────────────────────────────
    ENABLE_SMS_NOTIFICATIONS: bool = False
    ENABLE_EMAIL_NOTIFICATIONS: bool = False
    ENABLE_AUDIT_LOG: bool = True

    # ── Validators ────────────────────────────────────────────────────────────

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: Any) -> list[str]:
        if isinstance(v, str):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long.")
        return v

    @field_validator("FIELD_ENCRYPTION_KEY")
    @classmethod
    def validate_encryption_key(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("FIELD_ENCRYPTION_KEY must be at least 32 characters long.")
        return v

    # ── Computed Properties ───────────────────────────────────────────────────

    @computed_field
    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @computed_field
    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"

    @computed_field
    @property
    def jwt_secret_key(self) -> str:
        return self.SECRET_KEY

    @computed_field
    @property
    def jwt_algorithm(self) -> str:
        return self.JWT_ALGORITHM

    @computed_field
    @property
    def access_token_expire_minutes(self) -> int:
        return self.ACCESS_TOKEN_EXPIRE_MINUTES

    @computed_field
    @property
    def refresh_token_expire_days(self) -> int:
        return self.REFRESH_TOKEN_EXPIRE_DAYS

    @computed_field
    @property
    def redis_cache_url(self) -> str:
        base = self.REDIS_URL.rsplit("/", 1)[0]
        return f"{base}/{self.REDIS_CACHE_DB}"

    @computed_field
    @property
    def redis_session_url(self) -> str:
        base = self.REDIS_URL.rsplit("/", 1)[0]
        return f"{base}/{self.REDIS_SESSION_DB}"

    @computed_field
    @property
    def redis_rate_limit_url(self) -> str:
        base = self.REDIS_URL.rsplit("/", 1)[0]
        return f"{base}/{self.REDIS_RATE_LIMIT_DB}"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings: Settings = get_settings()
