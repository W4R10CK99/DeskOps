"""Relational schema for the core OpsDesk entities."""

from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from opsdesk_api.database.base import Base


class Workspace(Base):
    __tablename__ = "workspaces"
    __table_args__ = (CheckConstraint("length(trim(name)) > 0", name="ck_workspaces_name"),)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    memberships: Mapped[list["Membership"]] = relationship(back_populates="workspace")
    projects: Mapped[list["Project"]] = relationship(back_populates="workspace")


class Membership(Base):
    """Workspace membership identity record; authentication is a later phase."""

    __tablename__ = "memberships"
    __table_args__ = (
        UniqueConstraint(
            "workspace_id",
            "identity_issuer",
            "identity_subject",
            name="uq_memberships_workspace_identity",
        ),
        CheckConstraint("length(trim(email)) > 0", name="ck_memberships_email"),
        CheckConstraint("role IN ('owner', 'member')", name="ck_memberships_role"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    workspace_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("workspaces.id", ondelete="RESTRICT"), nullable=False
    )
    email: Mapped[str | None] = mapped_column(String(254), nullable=True)
    identity_issuer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    identity_subject: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(16), nullable=False, default="member")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    workspace: Mapped[Workspace] = relationship(back_populates="memberships")


class Project(Base):
    __tablename__ = "projects"
    __table_args__ = (
        CheckConstraint("length(trim(name)) > 0", name="ck_projects_name"),
        CheckConstraint("length(trim(customer)) > 0", name="ck_projects_customer"),
        Index("ix_projects_workspace_name", "workspace_id", "name"),
        Index("ix_projects_workspace_customer", "workspace_id", "customer"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    workspace_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("workspaces.id", ondelete="RESTRICT"), nullable=False
    )
    owner_membership_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("memberships.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    customer: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    workspace: Mapped[Workspace] = relationship(back_populates="projects")
    owner: Mapped[Membership | None] = relationship(foreign_keys=[owner_membership_id])
    tasks: Mapped[list["Task"]] = relationship(back_populates="project")


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (
        CheckConstraint("length(trim(title)) > 0", name="ck_tasks_title"),
        CheckConstraint("length(trim(owner)) > 0", name="ck_tasks_owner"),
        CheckConstraint(
            "status IN ('In progress', 'To do', 'Review', 'Done')", name="ck_tasks_status"
        ),
        Index("ix_tasks_project_due", "project_id", "due"),
        Index("ix_tasks_status_due", "status", "due"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("projects.id", ondelete="RESTRICT"), nullable=False
    )
    owner_membership_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("memberships.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    owner: Mapped[str] = mapped_column(String(120), nullable=False)
    due: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="To do")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    project: Mapped[Project] = relationship(back_populates="tasks")
    owner_membership: Mapped[Membership | None] = relationship(foreign_keys=[owner_membership_id])


class DocumentMetadata(Base):
    __tablename__ = "document_metadata"
    __table_args__ = (
        CheckConstraint("length(trim(name)) > 0", name="ck_document_metadata_name"),
        Index("ix_document_metadata_workspace", "workspace_id"),
        Index("ix_document_metadata_project", "project_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    workspace_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("workspaces.id", ondelete="RESTRICT"), nullable=False
    )
    project_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str | None] = mapped_column(String(120))
    storage_key: Mapped[str | None] = mapped_column(String(512))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class AuditEvent(Base):
    __tablename__ = "audit_events"
    __table_args__ = (
        CheckConstraint("length(trim(action)) > 0", name="ck_audit_events_action"),
        Index("ix_audit_events_workspace_created", "workspace_id", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    workspace_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("workspaces.id", ondelete="RESTRICT"), nullable=False
    )
    membership_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("memberships.id", ondelete="SET NULL"), nullable=True
    )
    action: Mapped[str] = mapped_column(String(80), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(40), nullable=False)
    entity_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
