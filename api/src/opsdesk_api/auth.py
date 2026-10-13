"""OIDC access-token verification and database-backed workspace identity."""

from dataclasses import dataclass
from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient, PyJWTError
from sqlalchemy import select

from opsdesk_api.database.models import Membership, Workspace

bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True, slots=True)
class VerifiedIdentity:
    issuer: str
    subject: str
    email: str | None = None


@dataclass(frozen=True, slots=True)
class CurrentMembership:
    workspace_id: UUID
    membership_id: UUID | None
    issuer: str
    subject: str
    role: str
    workspace_name: str


def verify_access_token(token: str, request: Request) -> VerifiedIdentity:
    settings = request.app.state.settings
    issuer = settings.oidc_issuer
    audience = settings.oidc_audience
    jwks_url = settings.oidc_jwks_url or f"{issuer.rstrip('/')}/.well-known/jwks.json"
    if not issuer or not audience:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "identity_not_configured",
                "message": "Identity provider is not configured",
            },
        )
    try:
        jwks_client = getattr(request.app.state, "jwks_client", None)
        if jwks_client is None:
            jwks_client = PyJWKClient(jwks_url, cache_keys=True)
        key = jwks_client.get_signing_key_from_jwt(token).key
        claims = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=audience,
            issuer=issuer,
            options={"require": ["iss", "aud", "exp", "iat", "sub"]},
        )
    except PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "invalid_token", "message": "Access token is invalid or expired"},
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    subject = claims.get("sub")
    if not isinstance(subject, str) or not subject or len(subject) > 255:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "invalid_token", "message": "Access token is invalid or expired"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    email = claims.get("email")
    return VerifiedIdentity(
        issuer=issuer, subject=subject, email=email if isinstance(email, str) else None
    )


def current_identity(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> VerifiedIdentity:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "authentication_required", "message": "Authentication is required"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    return verify_access_token(credentials.credentials, request)


def current_membership(
    request: Request,
    identity: Annotated[VerifiedIdentity, Depends(current_identity)],
    selected_workspace_id: Annotated[UUID, Header(alias="X-Workspace-ID")],
) -> CurrentMembership:
    database = request.app.state.database
    if database is None:
        raise HTTPException(status_code=500, detail="Workspace membership storage is unavailable")
    with database.sessions() as session:
        row = session.execute(
            select(Membership, Workspace.name)
            .join(Workspace, Workspace.id == Membership.workspace_id)
            .where(
                Membership.workspace_id == selected_workspace_id,
                Membership.identity_issuer == identity.issuer,
                Membership.identity_subject == identity.subject,
            )
        ).first()
    if row is None:
        # Same response for a missing workspace and a non-member to avoid resource enumeration.
        raise HTTPException(
            status_code=404,
            detail={"code": "workspace_not_found", "message": "Workspace not found"},
        )
    membership, workspace_name = row
    return CurrentMembership(
        workspace_id=membership.workspace_id,
        membership_id=membership.id,
        issuer=identity.issuer,
        subject=identity.subject,
        role=membership.role,
        workspace_name=workspace_name,
    )
