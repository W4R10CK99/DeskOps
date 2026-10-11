"""Router dependencies for application services."""

from fastapi import Request

from opsdesk_api.services.projects import ProjectService
from opsdesk_api.services.tasks import TaskService


def project_service(request: Request) -> ProjectService:
    return request.app.state.project_service


def task_service(request: Request) -> TaskService:
    return request.app.state.task_service
