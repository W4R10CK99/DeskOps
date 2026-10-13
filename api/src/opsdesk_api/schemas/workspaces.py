"""Workspace and owner-managed membership transport schemas."""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class WorkspaceRead(BaseModel):
    id: UUID
    name: str
    role: Literal["owner", "member"]


class WorkspaceMemberCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    identity_subject: str = Field(min_length=1, max_length=255)
    role: Literal["owner", "member"] = "member"
    email: str | None = Field(default=None, max_length=254)

    @field_validator("identity_subject")
    @classmethod
    def subject_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("identity_subject must not be blank")
        return value

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None


class WorkspaceMemberRead(BaseModel):
    id: UUID
    identity_subject: str
    email: str | None
    role: Literal["owner", "member"]
