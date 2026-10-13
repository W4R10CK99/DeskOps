"""Workspace-scoped access to document metadata stored in PostgreSQL."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select

from opsdesk_api.auth import CurrentMembership, current_membership
from opsdesk_api.database.models import DocumentMetadata
from opsdesk_api.schemas.documents import DocumentMetadataRead

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


@router.get("/{document_id}", response_model=DocumentMetadataRead, summary="Get document metadata")
def get_document_metadata(
    document_id: UUID,
    request: Request,
    membership: Annotated[CurrentMembership, Depends(current_membership)],
) -> DocumentMetadataRead:
    database = request.app.state.database
    with database.sessions() as session:
        document = session.scalar(
            select(DocumentMetadata).where(
                DocumentMetadata.id == document_id,
                DocumentMetadata.workspace_id == membership.workspace_id,
            )
        )
    if document is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "document_not_found", "message": "Document not found"},
        )
    return DocumentMetadataRead.model_validate(document)
