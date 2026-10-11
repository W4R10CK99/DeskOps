"""Task business logic."""

from dataclasses import asdict
from datetime import date
from uuid import UUID, uuid4

from opsdesk_api.errors import ApiError
from opsdesk_api.repositories.protocol import OpsRepository
from opsdesk_api.schemas.common import PageMeta
from opsdesk_api.schemas.tasks import (
    TaskCreate,
    TaskPage,
    TaskRead,
    TaskSort,
    TaskSortOrder,
    TaskStatus,
    TaskUpdate,
)
from opsdesk_api.services.pagination import page_items


class TaskService:
    def __init__(self, repository: OpsRepository) -> None:
        self.repository = repository

    def list_tasks(
        self,
        *,
        project_id: UUID | None,
        status: TaskStatus | None,
        query: str | None,
        sort: TaskSort,
        order: TaskSortOrder,
        offset: int,
        limit: int,
    ) -> TaskPage:
        records = self.repository.list_tasks()
        if project_id is not None:
            records = [task for task in records if task.project_id == project_id]
        if status is not None:
            records = [task for task in records if task.status == status]
        if query:
            term = query.casefold()
            records = [task for task in records if term in f"{task.title} {task.owner}".casefold()]

        def sort_key(task):
            value = getattr(task, sort)
            if isinstance(value, date):
                return value, str(task.id)
            return value.casefold(), str(task.id)

        rows, total = page_items(
            records,
            key=sort_key,
            descending=order == "desc",
            offset=offset,
            limit=limit,
        )
        return TaskPage(
            items=[TaskRead(**asdict(task)) for task in rows],
            page=PageMeta(limit=limit, offset=offset, total=total),
        )

    def get_task(self, task_id: UUID) -> TaskRead:
        task = self.repository.get_task(task_id)
        if task is None:
            raise ApiError(404, "not_found", "Task not found")
        return TaskRead(**asdict(task))

    def create_task(self, project_id: UUID, data: TaskCreate) -> TaskRead:
        self.require_project(project_id)
        task = self.repository.create_task(uuid4(), project_id, data)
        return TaskRead(**asdict(task))

    def update_task(self, task_id: UUID, changes: TaskUpdate) -> TaskRead:
        task = self.repository.update_task(task_id, changes)
        if task is None:
            raise ApiError(404, "not_found", "Task not found")
        return TaskRead(**asdict(task))

    def require_project(self, project_id: UUID) -> None:
        if self.repository.get_project(project_id) is None:
            raise ApiError(404, "not_found", "Project not found")
