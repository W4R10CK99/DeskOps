"""Versioned task endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from opsdesk_api.routers.dependencies import task_service
from opsdesk_api.schemas.responses import ERROR_RESPONSES
from opsdesk_api.schemas.tasks import (
    TaskPage,
    TaskRead,
    TaskSort,
    TaskSortOrder,
    TaskStatus,
    TaskUpdate,
)
from opsdesk_api.services.tasks import TaskService

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


@router.get("", response_model=TaskPage, responses=ERROR_RESPONSES, summary="List tasks")
def list_tasks(
    service: Annotated[TaskService, Depends(task_service)],
    project_id: UUID | None = None,
    status_filter: Annotated[TaskStatus | None, Query(alias="status")] = None,
    q: Annotated[str | None, Query(max_length=240)] = None,
    sort: TaskSort = "due",
    order: TaskSortOrder = "asc",
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> TaskPage:
    return service.list_tasks(
        project_id=project_id,
        status=status_filter,
        query=q,
        sort=sort,
        order=order,
        offset=offset,
        limit=limit,
    )


@router.get("/{task_id}", response_model=TaskRead, responses=ERROR_RESPONSES, summary="Get a task")
def get_task(
    task_id: UUID,
    service: Annotated[TaskService, Depends(task_service)],
) -> TaskRead:
    return service.get_task(task_id)


@router.patch(
    "/{task_id}",
    response_model=TaskRead,
    responses=ERROR_RESPONSES,
    summary="Update a task",
)
def update_task(
    task_id: UUID,
    payload: TaskUpdate,
    service: Annotated[TaskService, Depends(task_service)],
) -> TaskRead:
    return service.update_task(task_id, payload)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=ERROR_RESPONSES,
    summary="Delete a task",
)
def delete_task(
    task_id: UUID,
    service: Annotated[TaskService, Depends(task_service)],
) -> None:
    service.delete_task(task_id)
