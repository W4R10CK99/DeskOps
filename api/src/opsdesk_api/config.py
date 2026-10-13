"""Application settings loaded from the process environment."""

import os
from dataclasses import dataclass
from uuid import UUID

DEFAULT_WORKSPACE_ID = UUID("00000000-0000-4000-8000-000000000001")


@dataclass(frozen=True, slots=True)
class Settings:
    app_name: str = "OpsDesk API"
    environment: str = "development"
    log_level: str = "INFO"
    database_url: str = "postgresql+psycopg://opsdesk:opsdesk@localhost:5432/opsdesk"
    oidc_issuer: str = ""
    oidc_audience: str = ""
    oidc_jwks_url: str = ""
    cors_origins: tuple[str, ...] = ("http://localhost:5173",)

    @classmethod
    def from_environment(cls) -> "Settings":
        defaults = cls()
        cors_origins = tuple(
            origin.strip()
            for origin in os.getenv("OPSDESK_CORS_ORIGINS", "http://localhost:5173").split(",")
            if origin.strip()
        )
        if "*" in cors_origins:
            raise ValueError("OPSDESK_CORS_ORIGINS must be an explicit origin allowlist")
        return cls(
            app_name=os.getenv("OPSDESK_APP_NAME", defaults.app_name),
            environment=os.getenv("OPSDESK_ENVIRONMENT", defaults.environment),
            log_level=os.getenv("OPSDESK_LOG_LEVEL", defaults.log_level).upper(),
            database_url=os.getenv("OPSDESK_DATABASE_URL", defaults.database_url),
            oidc_issuer=os.getenv("OPSDESK_OIDC_ISSUER", ""),
            oidc_audience=os.getenv("OPSDESK_OIDC_AUDIENCE", ""),
            oidc_jwks_url=os.getenv("OPSDESK_OIDC_JWKS_URL", ""),
            cors_origins=cors_origins,
        )
