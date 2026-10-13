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
        rows, total = self.repository.list_projects(
            query=query,
            customer=customer,
            sort=sort,
            descending=descending,
            offset=offset,
            limit=limit,
        )
        task_counts = self.repository.count_tasks_for_projects([project.id for project in rows])
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
        task_count = self.repository.count_tasks_for_projects([project_id]).get(project_id, 0)
        return ProjectRead(**asdict(project), task_count=task_count)

    def create_project(self, data: ProjectCreate) -> ProjectRead:
        project = self.repository.create_project(uuid4(), data)
        return ProjectRead(**asdict(project), task_count=0)

    def update_project(self, project_id: UUID, changes: ProjectUpdate) -> ProjectRead:
        project = self.repository.update_project(project_id, changes)
        if project is None:
            raise ApiError(404, "not_found", "Project not found")
        task_count = self.repository.count_tasks_for_projects([project_id]).get(project_id, 0)
        return ProjectRead(**asdict(project), task_count=task_count)

    def delete_project(self, project_id: UUID) -> None:
        if not self.repository.delete_project(project_id):
            raise ApiError(404, "not_found", "Project not found")
