"""Project API schemas."""

from typing import Literal
from uuid import UUID

from pydantic import Field, model_validator

from .common import ApiModel, PageMeta


class ProjectCreate(ApiModel):
    name: str = Field(min_length=1, max_length=120)
    customer: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=2000)


class ProjectUpdate(ApiModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    customer: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2000)

    @model_validator(mode="after")
    def require_nonempty_patch(self) -> "ProjectUpdate":
        if not self.model_fields_set or any(
            getattr(self, field) is None for field in self.model_fields_set
        ):
            raise ValueError("Provide at least one non-null project field to update")
        return self


class ProjectRead(ApiModel):
    id: UUID
    name: str
    customer: str
    description: str
    task_count: int


class ProjectPage(ApiModel):
    items: list[ProjectRead]
    page: PageMeta


ProjectSort = Literal["name", "customer"]
