"""Ensure email remains informational rather than an identity key.

Revision ID: 20261012_0003
Revises: 20261012_0002
"""

from alembic import op

revision = "20261012_0003"
down_revision = "20261012_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("uq_memberships_workspace_email", "memberships", type_="unique")


def downgrade() -> None:
    op.create_unique_constraint(
        "uq_memberships_workspace_email", "memberships", ["workspace_id", "email"]
    )
