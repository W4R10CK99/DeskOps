"""Router dependencies for application services."""

from typing import Annotated

from fastapi import Depends, Request

from opsdesk_api.auth import CurrentMembership, current_membership
from opsdesk_api.repositories.postgres import PostgresRepository
from opsdesk_api.services.projects import ProjectService
from opsdesk_api.services.tasks import TaskService


def _scoped_repository(request: Request, membership: CurrentMembership):
    database = request.app.state.database
    if database is None:
        # Explicit in-memory repositories are used only by isolated contract tests.
        return request.app.state.repository
    return PostgresRepository(database.sessions, membership.workspace_id, membership.membership_id)


def project_service(
    request: Request, membership: Annotated[CurrentMembership, Depends(current_membership)]
) -> ProjectService:
    return ProjectService(_scoped_repository(request, membership))


def task_service(
    request: Request, membership: Annotated[CurrentMembership, Depends(current_membership)]
) -> TaskService:
    return TaskService(_scoped_repository(request, membership))
