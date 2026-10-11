"""Ephemeral repository for API development; data resets on process restart."""

from dataclasses import replace
from uuid import UUID

from opsdesk_api.schemas.projects import ProjectCreate, ProjectUpdate
from opsdesk_api.schemas.tasks import TaskCreate, TaskUpdate
from opsdesk_api.services.models import ProjectRecord, TaskRecord


class InMemoryRepository:
    def __init__(self) -> None:
        self._projects: dict[UUID, ProjectRecord] = {}
        self._tasks: dict[UUID, TaskRecord] = {}

    def list_projects(self) -> list[ProjectRecord]:
        return list(self._projects.values())

    def get_project(self, project_id: UUID) -> ProjectRecord | None:
        return self._projects.get(project_id)

    def create_project(self, project_id: UUID, data: ProjectCreate) -> ProjectRecord:
        record = ProjectRecord(id=project_id, **data.model_dump())
        self._projects[project_id] = record
        return record

    def update_project(self, project_id: UUID, changes: ProjectUpdate) -> ProjectRecord | None:
        current = self.get_project(project_id)
        if current is None:
            return None
        record = replace(current, **changes.model_dump(exclude_unset=True))
        self._projects[project_id] = record
        return record

    def list_tasks(self) -> list[TaskRecord]:
        return list(self._tasks.values())

    def get_task(self, task_id: UUID) -> TaskRecord | None:
        return self._tasks.get(task_id)

    def create_task(self, task_id: UUID, project_id: UUID, data: TaskCreate) -> TaskRecord:
        record = TaskRecord(id=task_id, project_id=project_id, **data.model_dump())
        self._tasks[task_id] = record
        return record

    def update_task(self, task_id: UUID, changes: TaskUpdate) -> TaskRecord | None:
        current = self.get_task(task_id)
        if current is None:
            return None
        record = replace(current, **changes.model_dump(exclude_unset=True))
        self._tasks[task_id] = record
        return record
