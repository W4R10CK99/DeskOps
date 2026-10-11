"""Consistent error envelope and HTTP exception translation."""

from collections.abc import Mapping
from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

STATUS_CODES = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    409: "conflict",
    422: "validation_error",
    429: "rate_limited",
    500: "internal_error",
}

ERROR_USE_CASES = {
    400: "The request is syntactically valid but violates an application-level rule.",
    401: "Authentication is missing or invalid; authentication is not implemented yet.",
    403: "The authenticated actor lacks permission; authorization is not implemented yet.",
    404: "The requested project, task, or route does not exist.",
    409: "The request conflicts with current state, such as a future uniqueness constraint.",
    422: "A request body, path parameter, or query parameter failed validation.",
    429: "A rate limit was exceeded; rate limiting is not implemented yet.",
    500: "An unexpected server error occurred; details are logged with the request ID.",
}


class ApiError(Exception):
    def __init__(self, status_code: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message


def error_body(request_id: str, code: str, message: str, details: Any = None) -> dict[str, Any]:
    return {
        "error": {"code": code, "message": message, "details": details},
        "request_id": request_id,
    }


def request_id_for(request: Request) -> str:
    return getattr(request.state, "request_id", "unavailable")


async def handle_api_error(request: Request, exc: ApiError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=error_body(request_id_for(request), exc.code, exc.message),
        headers={"X-Request-ID": request_id_for(request)},
    )


async def handle_http_error(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    detail = exc.detail
    message = "Request failed"
    code = STATUS_CODES.get(exc.status_code, "http_error")
    if isinstance(detail, str):
        message = detail
    elif isinstance(detail, Mapping):
        message = str(detail.get("message", message))
        code = str(detail.get("code", code))
    return JSONResponse(
        status_code=exc.status_code,
        content=error_body(request_id_for(request), code, message),
        headers={"X-Request-ID": request_id_for(request)},
    )


async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    details = [
        {
            "location": list(error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        }
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content=error_body(
            request_id_for(request), "validation_error", "Request validation failed", details
        ),
        headers={"X-Request-ID": request_id_for(request)},
    )
