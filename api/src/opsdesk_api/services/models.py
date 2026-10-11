"""Internal records kept independent from transport schemas."""

from dataclasses import dataclass
from datetime import date
from uuid import UUID

from opsdesk_api.schemas.tasks import TaskStatus


@dataclass(frozen=True, slots=True)
class ProjectRecord:
    id: UUID
    name: str
    customer: str
    description: str


@dataclass(frozen=True, slots=True)
class TaskRecord:
    id: UUID
    project_id: UUID
    title: str
    owner: str
    due: date
    status: TaskStatus
