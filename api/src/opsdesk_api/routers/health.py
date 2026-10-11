"""Process health endpoint."""

from fastapi import APIRouter

from opsdesk_api.schemas.common import HealthResponse
from opsdesk_api.schemas.responses import ERROR_RESPONSES

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    responses=ERROR_RESPONSES,
    summary="Check API process health",
)
def health() -> HealthResponse:
    return HealthResponse(status="ok")
