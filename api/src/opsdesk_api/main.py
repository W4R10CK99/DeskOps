"""FastAPI application factory and error/logging boundaries."""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from opsdesk_api.config import Settings
from opsdesk_api.errors import (
    ApiError,
    error_body,
    handle_api_error,
    handle_http_error,
    handle_validation_error,
    request_id_for,
)
from opsdesk_api.logging_config import configure_logging
from opsdesk_api.middleware import request_context
from opsdesk_api.repositories.memory import InMemoryRepository
from opsdesk_api.repositories.protocol import OpsRepository
from opsdesk_api.routers.health import router as health_router
from opsdesk_api.routers.projects import router as projects_router
from opsdesk_api.routers.tasks import router as tasks_router
from opsdesk_api.services.projects import ProjectService
from opsdesk_api.services.tasks import TaskService

logger = logging.getLogger("opsdesk.errors")


def create_app(
    settings: Settings | None = None, repository: OpsRepository | None = None
) -> FastAPI:
    config = settings or Settings.from_environment()
    configure_logging(config.log_level)
    app = FastAPI(
        title=config.app_name,
        version="1.0.0",
        description=(
            "OpsDesk API foundation. Project and task data uses process-local memory and "
            "resets when the service restarts."
        ),
    )
    data_store = repository or InMemoryRepository()
    app.state.settings = config
    app.state.repository = data_store
    app.state.project_service = ProjectService(data_store)
    app.state.task_service = TaskService(data_store)
    app.middleware("http")(request_context)
    app.add_exception_handler(ApiError, handle_api_error)
    app.add_exception_handler(StarletteHTTPException, handle_http_error)
    app.add_exception_handler(RequestValidationError, handle_validation_error)

    @app.exception_handler(Exception)
    async def unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        request_id = request_id_for(request)
        logger.error(
            "unhandled request failure",
            extra={
                "event": "request_failed",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "error_type": type(exc).__name__,
            },
        )
        return JSONResponse(
            status_code=500,
            content=error_body(request_id, "internal_error", "An unexpected error occurred"),
            headers={"X-Request-ID": request_id},
        )

    app.include_router(health_router)
    app.include_router(projects_router)
    app.include_router(tasks_router)
    return app


app = create_app()
