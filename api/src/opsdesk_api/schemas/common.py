"""Shared API response schemas."""

from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ApiModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class PageMeta(ApiModel):
    limit: int
    offset: int
    total: int


class ErrorDetail(ApiModel):
    location: list[str | int] | None = None
    message: str
    type: str | None = None


class ErrorInfo(ApiModel):
    code: str
    message: str
    details: list[ErrorDetail] | dict[str, Any] | None = None


class ErrorResponse(ApiModel):
    error: ErrorInfo
    request_id: str


class HealthResponse(ApiModel):
    status: str


class IdResponse(ApiModel):
    id: UUID
