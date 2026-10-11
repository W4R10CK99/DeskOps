"""Common documented error responses."""

from opsdesk_api.errors import ERROR_USE_CASES
from opsdesk_api.schemas.common import ErrorResponse

ERROR_RESPONSES = {
    code: {"model": ErrorResponse, "description": description}
    for code, description in ERROR_USE_CASES.items()
}
