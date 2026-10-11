"""Application settings loaded from the process environment."""

import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Settings:
    app_name: str = "OpsDesk API"
    environment: str = "development"
    log_level: str = "INFO"

    @classmethod
    def from_environment(cls) -> "Settings":
        defaults = cls()
        return cls(
            app_name=os.getenv("OPSDESK_APP_NAME", defaults.app_name),
            environment=os.getenv("OPSDESK_ENVIRONMENT", defaults.environment),
            log_level=os.getenv("OPSDESK_LOG_LEVEL", defaults.log_level).upper(),
        )
