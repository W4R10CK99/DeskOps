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

    @classmethod
    def from_environment(cls) -> "Settings":
        defaults = cls()
        return cls(
            app_name=os.getenv("OPSDESK_APP_NAME", defaults.app_name),
            environment=os.getenv("OPSDESK_ENVIRONMENT", defaults.environment),
            log_level=os.getenv("OPSDESK_LOG_LEVEL", defaults.log_level).upper(),
            database_url=os.getenv("OPSDESK_DATABASE_URL", defaults.database_url),
        )
