"""PostgreSQL implementation of the application repository contract."""

from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, sessionmaker

from opsdesk_api.database.models import AuditEvent, Project, Task
from opsdesk_api.errors import ApiError
from opsdesk_api.schemas.projects import ProjectCreate, ProjectUpdate
from opsdesk_api.schemas.tasks import TaskCreate, TaskUpdate
from opsdesk_api.services.models import ProjectRecord, TaskRecord


def _contains_pattern(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


class PostgresRepository:
    def __init__(self, sessions: sessionmaker[Session], default_workspace_id: UUID) -> None:
        self._sessions = sessions
        self._default_workspace_id = default_workspace_id

    def list_projects(
        self, *, query, customer, sort, descending, offset, limit
    ) -> tuple[list[ProjectRecord], int]:
        filters = [Project.workspace_id == self._default_workspace_id]
        if query:
            pattern = _contains_pattern(query)
            filters.append(
                or_(
                    Project.name.ilike(pattern, escape="\\"),
                    Project.customer.ilike(pattern, escape="\\"),
                    Project.description.ilike(pattern, escape="\\"),
                )
            )
        if customer:
            filters.append(func.lower(Project.customer) == customer.casefold())
        order_column = {"name": Project.name, "customer": Project.customer}[sort]
        order = order_column.desc() if descending else order_column.asc()
        id_order = Project.id.desc() if descending else Project.id.asc()
        with self._sessions() as session:
            total = session.scalar(select(func.count()).select_from(Project).where(*filters)) or 0
            rows = session.scalars(
                select(Project)
                .where(*filters)
                .order_by(order, id_order)
                .offset(offset)
                .limit(limit)
            ).all()
            return [self._project_record(row) for row in rows], total

    def get_project(self, project_id: UUID) -> ProjectRecord | None:
        with self._sessions() as session:
            row = session.scalar(
                select(Project).where(
                    Project.id == project_id,
                    Project.workspace_id == self._default_workspace_id,
                )
            )
            return self._project_record(row) if row else None

    def create_project(self, project_id: UUID, data: ProjectCreate) -> ProjectRecord:
        with self._sessions.begin() as session:
            row = Project(
                id=project_id, workspace_id=self._default_workspace_id, **data.model_dump()
            )
            session.add(row)
            session.flush()
            session.add(
                AuditEvent(
                    workspace_id=self._default_workspace_id,
                    action="project.created",
                    entity_type="project",
                    entity_id=project_id,
                )
            )
            session.flush()
            return self._project_record(row)

    def update_project(self, project_id: UUID, changes: ProjectUpdate) -> ProjectRecord | None:
        with self._sessions.begin() as session:
            row = session.scalar(
                select(Project).where(
                    Project.id == project_id,
                    Project.workspace_id == self._default_workspace_id,
                )
            )
            if row is None:
                return None
            for key, value in changes.model_dump(exclude_unset=True).items():
                setattr(row, key, value)
            session.add(
                AuditEvent(
                    workspace_id=row.workspace_id,
                    action="project.updated",
                    entity_type="project",
                    entity_id=project_id,
                )
            )
            session.flush()
            return self._project_record(row)

    def list_tasks(
        self, *, project_id, status, query, sort, descending, offset, limit
    ) -> tuple[list[TaskRecord], int]:
        filters = [Project.workspace_id == self._default_workspace_id]
        if project_id is not None:
            filters.append(Task.project_id == project_id)
        if status is not None:
            filters.append(Task.status == status)
        if query:
            pattern = _contains_pattern(query)
            filters.append(
                or_(Task.title.ilike(pattern, escape="\\"), Task.owner.ilike(pattern, escape="\\"))
            )
        order_column = {
            "title": Task.title,
            "owner": Task.owner,
            "due": Task.due,
            "status": Task.status,
        }[sort]
        order = order_column.desc() if descending else order_column.asc()
        id_order = Task.id.desc() if descending else Task.id.asc()
        with self._sessions() as session:
            query_stmt = select(Task).join(Project).where(*filters)
            total = session.scalar(select(func.count()).select_from(query_stmt.subquery())) or 0
            rows = session.scalars(
                query_stmt.order_by(order, id_order).offset(offset).limit(limit)
            ).all()
            return [self._task_record(row) for row in rows], total

    def count_tasks_for_projects(self, project_ids: list[UUID]) -> dict[UUID, int]:
        if not project_ids:
            return {}
        with self._sessions() as session:
            rows = session.execute(
                select(Task.project_id, func.count(Task.id))
                .join(Project)
                .where(
                    Task.project_id.in_(project_ids),
                    Project.workspace_id == self._default_workspace_id,
                )
                .group_by(Task.project_id)
            )
            counts = dict.fromkeys(project_ids, 0)
            counts.update({project_id: count for project_id, count in rows})
            return counts

    def get_task(self, task_id: UUID) -> TaskRecord | None:
        with self._sessions() as session:
            row = session.scalar(
                select(Task)
                .join(Project)
                .where(
                    Task.id == task_id,
                    Project.workspace_id == self._default_workspace_id,
                )
            )
            return self._task_record(row) if row else None

    def create_task(self, task_id: UUID, project_id: UUID, data: TaskCreate) -> TaskRecord:
        with self._sessions.begin() as session:
            project = session.scalar(
                select(Project).where(
                    Project.id == project_id,
                    Project.workspace_id == self._default_workspace_id,
                )
            )
            if project is None:
                raise ApiError(404, "not_found", "Project not found")
            row = Task(id=task_id, project_id=project_id, **data.model_dump())
            session.add(row)
            session.flush()
            session.add(
                AuditEvent(
                    workspace_id=project.workspace_id,
                    action="task.created",
                    entity_type="task",
                    entity_id=task_id,
                )
            )
            session.flush()
            return self._task_record(row)

    def update_task(self, task_id: UUID, changes: TaskUpdate) -> TaskRecord | None:
        with self._sessions.begin() as session:
            row = session.scalar(
                select(Task)
                .join(Project)
                .where(
                    Task.id == task_id,
                    Project.workspace_id == self._default_workspace_id,
                )
            )
            if row is None:
                return None
            for key, value in changes.model_dump(exclude_unset=True).items():
                setattr(row, key, value)
            session.add(
                AuditEvent(
                    workspace_id=row.project.workspace_id,
                    action="task.updated",
                    entity_type="task",
                    entity_id=task_id,
                )
            )
            session.flush()
            return self._task_record(row)

    @staticmethod
    def _project_record(row: Project) -> ProjectRecord:
        return ProjectRecord(
            id=row.id, name=row.name, customer=row.customer, description=row.description
        )

    @staticmethod
    def _task_record(row: Task) -> TaskRecord:
        return TaskRecord(
            id=row.id,
            project_id=row.project_id,
            title=row.title,
            owner=row.owner,
            due=row.due,
            status=row.status,  # type: ignore[arg-type]
        )
