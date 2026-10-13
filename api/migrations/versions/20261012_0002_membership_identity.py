"""Map workspace memberships to stable OIDC identities.

Revision ID: 20261012_0002
Revises: 20261011_0001
"""

import sqlalchemy as sa
from alembic import op

revision = "20261012_0002"
down_revision = "20261011_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("memberships", sa.Column("identity_issuer", sa.String(255), nullable=True))
    op.add_column("memberships", sa.Column("identity_subject", sa.String(255), nullable=True))
    op.alter_column("memberships", "email", existing_type=sa.String(length=254), nullable=True)
    op.create_unique_constraint(
        "uq_memberships_workspace_identity",
        "memberships",
        ["workspace_id", "identity_issuer", "identity_subject"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_memberships_workspace_identity", "memberships", type_="unique")
    op.alter_column("memberships", "email", existing_type=sa.String(length=254), nullable=False)
    op.drop_column("memberships", "identity_subject")
    op.drop_column("memberships", "identity_issuer")
