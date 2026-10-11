"""Versioned project endpoints."""

from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from opsdesk_api.routers.dependencies import project_service, task_service
from opsdesk_api.schemas.projects import (
    ProjectCreate,
    ProjectPage,
    ProjectRead,
    ProjectSort,
    ProjectUpdate,
)
from opsdesk_api.schemas.responses import ERROR_RESPONSES
from opsdesk_api.schemas.tasks import (
    TaskCreate,
    TaskPage,
    TaskRead,
    TaskSort,
    TaskSortOrder,
    TaskStatus,
)
from opsdesk_api.services.projects import ProjectService
from opsdesk_api.services.tasks import TaskService

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])
ProjectOrder = Literal["asc", "desc"]


@router.get("", response_model=ProjectPage, responses=ERROR_RESPONSES, summary="List projects")
def list_projects(
    service: Annotated[ProjectService, Depends(project_service)],
    q: Annotated[str | None, Query(max_length=120)] = None,
    customer: Annotated[str | None, Query(max_length=120)] = None,
    sort: ProjectSort = "name",
    order: ProjectOrder = "asc",
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> ProjectPage:
    return service.list_projects(
        query=q,
        customer=customer,
        sort=sort,
        descending=order == "desc",
        offset=offset,
        limit=limit,
    )


@router.post(
    "",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
    responses=ERROR_RESPONSES,
    summary="Create a project",
)
def create_project(
    payload: ProjectCreate,
    service: Annotated[ProjectService, Depends(project_service)],
) -> ProjectRead:
    return service.create_project(payload)


@router.get(
    "/{project_id}", response_model=ProjectRead, responses=ERROR_RESPONSES, summary="Get a project"
)
def get_project(
    project_id: UUID,
    service: Annotated[ProjectService, Depends(project_service)],
) -> ProjectRead:
    return service.get_project(project_id)


@router.patch(
    "/{project_id}",
    response_model=ProjectRead,
    responses=ERROR_RESPONSES,
    summary="Update a project",
)
def update_project(
    project_id: UUID,
    payload: ProjectUpdate,
    service: Annotated[ProjectService, Depends(project_service)],
) -> ProjectRead:
    return service.update_project(project_id, payload)


@router.get(
    "/{project_id}/tasks",
    response_model=TaskPage,
    responses=ERROR_RESPONSES,
    summary="List a project's tasks",
)
def list_project_tasks(
    project_id: UUID,
    service: Annotated[TaskService, Depends(task_service)],
    status_filter: Annotated[TaskStatus | None, Query(alias="status")] = None,
    q: Annotated[str | None, Query(max_length=240)] = None,
    sort: TaskSort = "due",
    order: TaskSortOrder = "asc",
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> TaskPage:
    # Validate parent existence as well as returning an empty page for an existing project.
    service.require_project(project_id)
    return service.list_tasks(
        project_id=project_id,
        status=status_filter,
        query=q,
        sort=sort,
        order=order,
        offset=offset,
        limit=limit,
    )


@router.post(
    "/{project_id}/tasks",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    responses=ERROR_RESPONSES,
    summary="Create a task in a project",
)
def create_task(
    project_id: UUID,
    payload: TaskCreate,
    service: Annotated[TaskService, Depends(task_service)],
) -> TaskRead:
    return service.create_task(project_id, payload)
