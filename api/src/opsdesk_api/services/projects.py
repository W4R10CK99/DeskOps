"""Project business logic."""

from dataclasses import asdict
from uuid import UUID, uuid4

from opsdesk_api.errors import ApiError
from opsdesk_api.repositories.protocol import OpsRepository
from opsdesk_api.schemas.common import PageMeta
from opsdesk_api.schemas.projects import (
    ProjectCreate,
    ProjectPage,
    ProjectRead,
    ProjectSort,
    ProjectUpdate,
)
from opsdesk_api.services.pagination import page_items


class ProjectService:
    def __init__(self, repository: OpsRepository) -> None:
        self.repository = repository

    def list_projects(
        self,
        *,
        query: str | None,
        customer: str | None,
        sort: ProjectSort,
        descending: bool,
        offset: int,
        limit: int,
    ) -> ProjectPage:
        records = self.repository.list_projects()
        if query:
            term = query.casefold()
            records = [
                project
                for project in records
                if term in f"{project.name} {project.customer} {project.description}".casefold()
            ]
        if customer:
            records = [
                project for project in records if project.customer.casefold() == customer.casefold()
            ]
        rows, total = page_items(
            records,
            key=lambda project: (getattr(project, sort).casefold(), str(project.id)),
            descending=descending,
            offset=offset,
            limit=limit,
        )
        task_counts: dict[UUID, int] = {}
        for task in self.repository.list_tasks():
            task_counts[task.project_id] = task_counts.get(task.project_id, 0) + 1
        return ProjectPage(
            items=[
                ProjectRead(
                    id=project.id,
                    name=project.name,
                    customer=project.customer,
                    description=project.description,
                    task_count=task_counts.get(project.id, 0),
                )
                for project in rows
            ],
            page=PageMeta(limit=limit, offset=offset, total=total),
        )

    def get_project(self, project_id: UUID) -> ProjectRead:
        project = self.repository.get_project(project_id)
        if project is None:
            raise ApiError(404, "not_found", "Project not found")
        task_count = sum(task.project_id == project_id for task in self.repository.list_tasks())
        return ProjectRead(**asdict(project), task_count=task_count)

    def create_project(self, data: ProjectCreate) -> ProjectRead:
        project = self.repository.create_project(uuid4(), data)
        return ProjectRead(**asdict(project), task_count=0)

    def update_project(self, project_id: UUID, changes: ProjectUpdate) -> ProjectRead:
        project = self.repository.update_project(project_id, changes)
        if project is None:
            raise ApiError(404, "not_found", "Project not found")
        task_count = sum(task.project_id == project_id for task in self.repository.list_tasks())
        return ProjectRead(**asdict(project), task_count=task_count)
