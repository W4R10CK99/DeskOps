"""Create core persistence tables and the local development workspace."""

from uuid import UUID

import sqlalchemy as sa
from alembic import op

revision = "20261011_0001"
down_revision = None
branch_labels = None
depends_on = None
DEFAULT_WORKSPACE_ID = UUID("00000000-0000-4000-8000-000000000001")


def upgrade() -> None:
    op.create_table(
        "workspaces",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("length(trim(name)) > 0", name="ck_workspaces_name"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "memberships",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(254), nullable=False),
        sa.Column("role", sa.String(16), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("length(trim(email)) > 0", name="ck_memberships_email"),
        sa.CheckConstraint("role IN ('owner', 'member')", name="ck_memberships_role"),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("workspace_id", "email", name="uq_memberships_workspace_email"),
    )
    op.create_table(
        "projects",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("owner_membership_id", sa.Uuid(), nullable=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("customer", sa.String(120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("length(trim(name)) > 0", name="ck_projects_name"),
        sa.CheckConstraint("length(trim(customer)) > 0", name="ck_projects_customer"),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["owner_membership_id"], ["memberships.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_projects_workspace_name", "projects", ["workspace_id", "name"])
    op.create_index("ix_projects_workspace_customer", "projects", ["workspace_id", "customer"])
    op.create_table(
        "tasks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("owner_membership_id", sa.Uuid(), nullable=True),
        sa.Column("title", sa.String(240), nullable=False),
        sa.Column("owner", sa.String(120), nullable=False),
        sa.Column("due", sa.Date(), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("length(trim(title)) > 0", name="ck_tasks_title"),
        sa.CheckConstraint("length(trim(owner)) > 0", name="ck_tasks_owner"),
        sa.CheckConstraint(
            "status IN ('In progress', 'To do', 'Review', 'Done')", name="ck_tasks_status"
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["owner_membership_id"], ["memberships.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tasks_project_due", "tasks", ["project_id", "due"])
    op.create_index("ix_tasks_status_due", "tasks", ["status", "due"])
    op.create_table(
        "document_metadata",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("content_type", sa.String(120), nullable=True),
        sa.Column("storage_key", sa.String(512), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("length(trim(name)) > 0", name="ck_document_metadata_name"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_document_metadata_workspace", "document_metadata", ["workspace_id"])
    op.create_index("ix_document_metadata_project", "document_metadata", ["project_id"])
    op.create_table(
        "audit_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workspace_id", sa.Uuid(), nullable=False),
        sa.Column("membership_id", sa.Uuid(), nullable=True),
        sa.Column("action", sa.String(80), nullable=False),
        sa.Column("entity_type", sa.String(40), nullable=False),
        sa.Column("entity_id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("length(trim(action)) > 0", name="ck_audit_events_action"),
        sa.ForeignKeyConstraint(["membership_id"], ["memberships.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_audit_events_workspace_created", "audit_events", ["workspace_id", "created_at"]
    )
    op.bulk_insert(
        sa.table("workspaces", sa.column("id", sa.Uuid()), sa.column("name", sa.String())),
        [{"id": DEFAULT_WORKSPACE_ID, "name": "OpsDesk Local"}],
    )


def downgrade() -> None:
    op.drop_index("ix_audit_events_workspace_created", table_name="audit_events")
    op.drop_table("audit_events")
    op.drop_index("ix_document_metadata_project", table_name="document_metadata")
    op.drop_index("ix_document_metadata_workspace", table_name="document_metadata")
    op.drop_table("document_metadata")
    op.drop_index("ix_tasks_status_due", table_name="tasks")
    op.drop_index("ix_tasks_project_due", table_name="tasks")
    op.drop_table("tasks")
    op.drop_index("ix_projects_workspace_customer", table_name="projects")
    op.drop_index("ix_projects_workspace_name", table_name="projects")
    op.drop_table("projects")
    op.drop_table("memberships")
    op.drop_table("workspaces")
