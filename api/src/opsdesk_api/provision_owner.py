"""Privileged one-time bootstrap for the first owner of an existing workspace."""

import argparse
from uuid import UUID

from sqlalchemy import func, select

from opsdesk_api.config import Settings
from opsdesk_api.database.models import Membership, Workspace
from opsdesk_api.database.session import Database


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace-id", required=True, type=UUID)
    parser.add_argument(
        "--subject", required=True, help="Exact OIDC subject from the provider's user profile"
    )
    parser.add_argument(
        "--email", default=None, help="Optional display/contact email; never used for authorization"
    )
    args = parser.parse_args()
    settings = Settings.from_environment()
    if not settings.oidc_issuer:
        parser.error("Set OPSDESK_OIDC_ISSUER before provisioning an identity")
    database = Database(settings.database_url)
    try:
        with database.sessions.begin() as session:
            workspace = session.get(Workspace, args.workspace_id)
            if workspace is None:
                parser.error("The selected workspace does not exist")
            owner_count = session.scalar(
                select(func.count())
                .select_from(Membership)
                .where(Membership.workspace_id == workspace.id, Membership.role == "owner")
            )
            if owner_count:
                parser.error("Workspace already has an owner; use owner-managed membership.")
            existing_identity = session.scalar(
                select(Membership.id).where(
                    Membership.workspace_id == workspace.id,
                    Membership.identity_issuer == settings.oidc_issuer,
                    Membership.identity_subject == args.subject,
                )
            )
            if existing_identity is not None:
                parser.error("Identity already has a membership in this workspace.")
            session.add(
                Membership(
                    workspace_id=workspace.id,
                    identity_issuer=settings.oidc_issuer,
                    identity_subject=args.subject,
                    email=args.email,
                    role="owner",
                )
            )
        print(f"Provisioned the first owner for workspace {args.workspace_id}.")
    finally:
        database.engine.dispose()


if __name__ == "__main__":
    main()
