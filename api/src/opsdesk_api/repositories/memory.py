"""Ephemeral repository for API development; data resets on process restart."""

from dataclasses import replace
from datetime import date
from uuid import UUID

from opsdesk_api.errors import ApiError
from opsdesk_api.schemas.projects import ProjectCreate, ProjectUpdate
from opsdesk_api.schemas.tasks import TaskCreate, TaskUpdate
from opsdesk_api.services.models import ProjectRecord, TaskRecord


class InMemoryRepository:
    def __init__(self) -> None:
        self._projects: dict[UUID, ProjectRecord] = {}
        self._tasks: dict[UUID, TaskRecord] = {}

    def list_projects(
        self, *, query, customer, sort, descending, offset, limit
    ) -> tuple[list[ProjectRecord], int]:
        records = list(self._projects.values())
        if query:
            term = query.casefold()
            records = [
                project
                for project in records
                if term in f"{project.name} {project.customer} {project.description}".casefold()
            ]
        if customer:
            records = [p for p in records if p.customer.casefold() == customer.casefold()]
        records.sort(key=lambda p: (getattr(p, sort).casefold(), str(p.id)), reverse=descending)
        total = len(records)
        return records[offset : offset + limit], total

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

    def delete_project(self, project_id: UUID) -> bool:
        if project_id not in self._projects:
            return False
        if any(task.project_id == project_id for task in self._tasks.values()):
            raise ApiError(409, "conflict", "Project still has tasks")
        del self._projects[project_id]
        return True

    def list_tasks(
        self, *, project_id, status, query, sort, descending, offset, limit
    ) -> tuple[list[TaskRecord], int]:
        records = list(self._tasks.values())
        if project_id is not None:
            records = [task for task in records if task.project_id == project_id]
        if status is not None:
            records = [task for task in records if task.status == status]
        if query:
            term = query.casefold()
            records = [task for task in records if term in f"{task.title} {task.owner}".casefold()]

        def key(task):
            value = getattr(task, sort)
            return (value if isinstance(value, date) else value.casefold(), str(task.id))

        records.sort(key=key, reverse=descending)
        total = len(records)
        return records[offset : offset + limit], total

    def count_tasks_for_projects(self, project_ids: list[UUID]) -> dict[UUID, int]:
        counts = dict.fromkeys(project_ids, 0)
        for task in self._tasks.values():
            if task.project_id in counts:
                counts[task.project_id] += 1
        return counts

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

    def delete_task(self, task_id: UUID) -> bool:
        return self._tasks.pop(task_id, None) is not None
