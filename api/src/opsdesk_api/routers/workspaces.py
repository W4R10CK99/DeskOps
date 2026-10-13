"""Authenticated workspace listing and owner-controlled membership provisioning."""

from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from opsdesk_api.auth import (
    CurrentMembership,
    VerifiedIdentity,
    current_identity,
    current_membership,
)
from opsdesk_api.database.models import AuditEvent, Membership, Workspace
from opsdesk_api.schemas.workspaces import (
    WorkspaceMemberCreate,
    WorkspaceMemberRead,
    WorkspaceRead,
)

router = APIRouter(prefix="/api/v1/workspaces", tags=["workspaces"])


@router.get("", response_model=list[WorkspaceRead], summary="List caller workspaces")
def list_workspaces(
    request: Request,
    identity: Annotated[VerifiedIdentity, Depends(current_identity)],
) -> list[WorkspaceRead]:
    database = request.app.state.database
    if database is None:
        raise HTTPException(status_code=503, detail="Workspace storage is unavailable")
    with database.sessions() as session:
        rows = session.execute(
            select(Workspace.id, Workspace.name, Membership.role)
            .join(Membership, Membership.workspace_id == Workspace.id)
            .where(
                Membership.identity_issuer == identity.issuer,
                Membership.identity_subject == identity.subject,
            )
            .order_by(Workspace.name, Workspace.id)
        )
        return [WorkspaceRead(id=row.id, name=row.name, role=row.role) for row in rows]


@router.post(
    "/{workspace_id}/members",
    response_model=WorkspaceMemberRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add a workspace member (owner only)",
)
def add_member(
    workspace_id: UUID,
    payload: WorkspaceMemberCreate,
    request: Request,
    membership: Annotated[CurrentMembership, Depends(current_membership)],
) -> WorkspaceMemberRead:
    if membership.workspace_id != workspace_id:
        raise HTTPException(
            status_code=404,
            detail={"code": "workspace_not_found", "message": "Workspace not found"},
        )
    if membership.role != "owner":
        raise HTTPException(
            status_code=403, detail={"code": "forbidden", "message": "Owner role required"}
        )
    if payload.identity_subject == membership.subject:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "membership_conflict",
                "message": "Cannot add the current identity again",
            },
        )

    database = request.app.state.database
    try:
        with database.sessions.begin() as session:
            existing = session.scalar(
                select(Membership.id).where(
                    Membership.workspace_id == workspace_id,
                    Membership.identity_issuer == membership.issuer,
                    Membership.identity_subject == payload.identity_subject,
                )
            )
            if existing is not None:
                raise HTTPException(
                    status_code=409,
                    detail={"code": "membership_conflict", "message": "Membership already exists"},
                )
            member = Membership(
                id=uuid4(),
                workspace_id=workspace_id,
                identity_issuer=membership.issuer,
                identity_subject=payload.identity_subject,
                email=payload.email,
                role=payload.role,
            )
            session.add(member)
            session.flush()
            session.add(
                AuditEvent(
                    workspace_id=workspace_id,
                    membership_id=membership.membership_id,
                    action="membership.created",
                    entity_type="membership",
                    entity_id=member.id,
                )
            )
            session.flush()
            result = WorkspaceMemberRead(
                id=member.id,
                identity_subject=member.identity_subject,
                email=member.email,
                role=member.role,
            )
    except IntegrityError as exc:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "membership_conflict",
                "message": "Membership conflicts with existing workspace data",
            },
        ) from exc
    return result
