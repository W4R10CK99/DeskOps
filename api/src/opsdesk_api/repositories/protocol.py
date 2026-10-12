"""Persistence boundary used by application services."""

from typing import Protocol
from uuid import UUID

from opsdesk_api.schemas.projects import ProjectCreate, ProjectUpdate
from opsdesk_api.schemas.tasks import TaskCreate, TaskUpdate
from opsdesk_api.services.models import ProjectRecord, TaskRecord


class OpsRepository(Protocol):
    def list_projects(
        self,
        *,
        query: str | None,
        customer: str | None,
        sort: str,
        descending: bool,
        offset: int,
        limit: int,
    ) -> tuple[list[ProjectRecord], int]: ...

    def get_project(self, project_id: UUID) -> ProjectRecord | None: ...

    def create_project(self, project_id: UUID, data: ProjectCreate) -> ProjectRecord: ...

    def update_project(self, project_id: UUID, changes: ProjectUpdate) -> ProjectRecord | None: ...

    def list_tasks(
        self,
        *,
        project_id: UUID | None,
        status: str | None,
        query: str | None,
        sort: str,
        descending: bool,
        offset: int,
        limit: int,
    ) -> tuple[list[TaskRecord], int]: ...

    def count_tasks_for_projects(self, project_ids: list[UUID]) -> dict[UUID, int]: ...

    def get_task(self, task_id: UUID) -> TaskRecord | None: ...

    def create_task(self, task_id: UUID, project_id: UUID, data: TaskCreate) -> TaskRecord: ...

    def update_task(self, task_id: UUID, changes: TaskUpdate) -> TaskRecord | None: ...
