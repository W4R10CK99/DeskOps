"""Private document metadata response schema; file bytes are added in Phase 05."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DocumentMetadataRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID | None
    name: str
    content_type: str | None
    created_at: datetime
