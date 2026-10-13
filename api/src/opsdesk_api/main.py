"""FastAPI application factory and error/logging boundaries."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from jwt import PyJWKClient
from starlette.exceptions import HTTPException as StarletteHTTPException

from opsdesk_api.config import DEFAULT_WORKSPACE_ID, Settings
from opsdesk_api.database.session import Database
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
from opsdesk_api.repositories.postgres import PostgresRepository
from opsdesk_api.repositories.protocol import OpsRepository
from opsdesk_api.routers.documents import router as documents_router
from opsdesk_api.routers.health import router as health_router
from opsdesk_api.routers.projects import router as projects_router
from opsdesk_api.routers.tasks import router as tasks_router
from opsdesk_api.routers.workspaces import router as workspaces_router

logger = logging.getLogger("opsdesk.errors")


def create_app(
    settings: Settings | None = None, repository: OpsRepository | None = None
) -> FastAPI:
    config = settings or Settings.from_environment()
    configure_logging(config.log_level)
    database = None if repository is not None else Database(config.database_url)

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        try:
            if database is not None:
                # Fail visibly when PostgreSQL is unavailable; never mask it with memory.
                with database.engine.connect():
                    pass
            yield
        finally:
            if database is not None:
                database.engine.dispose()

    app = FastAPI(
        title=config.app_name,
        version="1.0.0",
        description="OpsDesk API. Project and task records are stored in PostgreSQL.",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(config.cors_origins),
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Workspace-ID"],
        expose_headers=["X-Request-ID"],
    )
    data_store = repository or PostgresRepository(database.sessions, DEFAULT_WORKSPACE_ID)
    app.state.settings = config
    app.state.database = database
    app.state.repository = data_store
    jwks_url = config.oidc_jwks_url or (
        f"{config.oidc_issuer.rstrip('/')}/.well-known/jwks.json" if config.oidc_issuer else ""
    )
    app.state.jwks_client = (
        PyJWKClient(jwks_url, cache_keys=True) if jwks_url and config.oidc_audience else None
    )
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
    app.include_router(documents_router)
    app.include_router(projects_router)
    app.include_router(tasks_router)
    app.include_router(workspaces_router)
    return app


app = create_app()
