"""Request context, correlation IDs, and safe structured access logs."""

import logging
from time import perf_counter
from uuid import uuid4

from starlette.middleware.base import RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("opsdesk.http")


async def request_context(request: Request, call_next: RequestResponseEndpoint) -> Response:
    request_id = str(uuid4())
    request.state.request_id = request_id
    request.state.environment = request.app.state.settings.environment
    started = perf_counter()
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "request completed",
        extra={
            "event": "request_completed",
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round((perf_counter() - started) * 1000, 2),
            "environment": request.state.environment,
        },
    )
    return response
