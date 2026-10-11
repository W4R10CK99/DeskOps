"""Task API schemas."""

from datetime import date
from typing import Literal
from uuid import UUID

from pydantic import Field, model_validator

from .common import ApiModel, PageMeta

TaskStatus = Literal["In progress", "To do", "Review", "Done"]


class TaskCreate(ApiModel):
    title: str = Field(min_length=1, max_length=240)
    owner: str = Field(min_length=1, max_length=120)
    due: date
    status: TaskStatus = "To do"


class TaskUpdate(ApiModel):
    title: str | None = Field(default=None, min_length=1, max_length=240)
    owner: str | None = Field(default=None, min_length=1, max_length=120)
    due: date | None = None
    status: TaskStatus | None = None

    @model_validator(mode="after")
    def require_nonempty_patch(self) -> "TaskUpdate":
        if not self.model_fields_set or any(
            getattr(self, field) is None for field in self.model_fields_set
        ):
            raise ValueError("Provide at least one non-null task field to update")
        return self


class TaskRead(ApiModel):
    id: UUID
    project_id: UUID
    title: str
    owner: str
    due: date
    status: TaskStatus


class TaskPage(ApiModel):
    items: list[TaskRead]
    page: PageMeta


TaskSort = Literal["title", "owner", "due", "status"]
TaskSortOrder = Literal["asc", "desc"]
