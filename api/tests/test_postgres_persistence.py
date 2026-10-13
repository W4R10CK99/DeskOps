"""Real PostgreSQL integration checks; opt in with a dedicated *_test database URL."""

import os
from datetime import date
from uuid import UUID, uuid4

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import event, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from opsdesk_api.auth import CurrentMembership, current_membership
from opsdesk_api.config import DEFAULT_WORKSPACE_ID, Settings
from opsdesk_api.database.models import AuditEvent, Project, Task
from opsdesk_api.database.session import Database
from opsdesk_api.main import create_app
from opsdesk_api.repositories.postgres import PostgresRepository
from opsdesk_api.schemas.projects import ProjectCreate
from opsdesk_api.seed import PROJECTS, seed, task_id_for

DATABASE_URL = os.getenv("OPSDESK_TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(not DATABASE_URL, reason="OPSDESK_TEST_DATABASE_URL is not set")


def _test_settings() -> Settings:
    assert DATABASE_URL is not None
    database_name = DATABASE_URL.rsplit("/", maxsplit=1)[-1].split("?", maxsplit=1)[0]
    if not database_name.endswith("_test"):
        pytest.fail("OPSDESK_TEST_DATABASE_URL must target a database whose name ends in _test")
    if not DATABASE_URL.startswith("postgresql+psycopg://"):
        pytest.fail("PostgreSQL integration tests require the psycopg SQLAlchemy URL")
    return Settings(database_url=DATABASE_URL)


def _persistence_test_app(settings: Settings):
    app = create_app(settings=settings)
    # Phase 03 tests exercise persistence; authentication has dedicated Phase 04 tests.
    app.dependency_overrides[current_membership] = lambda: CurrentMembership(
        DEFAULT_WORKSPACE_ID,
        None,
        "https://phase03-test.example/",
        "persistence-test-actor",
        "owner",
        "OpsDesk Local",
    )
    return app


@pytest.fixture(scope="module", autouse=True)
def migrate_test_database() -> None:
    settings = _test_settings()
    database = Database(settings.database_url)
    try:
        with database.engine.connect() as connection:
            if connection.dialect.name != "postgresql":
                pytest.fail("Integration tests require PostgreSQL")
    finally:
        database.engine.dispose()
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", settings.database_url.replace("%", "%%"))
    config.attributes["database_url"] = settings.database_url
    command.upgrade(config, "head")


def test_api_records_survive_application_restart() -> None:
    settings = _test_settings()
    app = _persistence_test_app(settings)
    with TestClient(app) as first_process:
        created = first_process.post(
            "/api/v1/projects",
            json={"name": "Restart proof", "customer": "Synthetic"},
        )
        assert created.status_code == 201
        project_id = created.json()["id"]
        task = first_process.post(
            f"/api/v1/projects/{project_id}/tasks",
            json={"title": "Restart task", "owner": "Synthetic", "due": "2026-11-15"},
        )
        assert task.status_code == 201
        task_id = task.json()["id"]

    restarted_app = _persistence_test_app(settings)
    with TestClient(restarted_app) as restarted_process:
        response = restarted_process.get(f"/api/v1/projects/{project_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Restart proof"
    task_response = restarted_process.get(f"/api/v1/tasks/{task_id}")
    assert task_response.status_code == 200
    assert task_response.json()["title"] == "Restart task"


def test_project_and_task_api_pagination_over_seeded_dataset() -> None:
    settings = _test_settings()
    seed(settings.database_url)
    project_id = "10000000-0000-4000-8000-000000000001"
    with TestClient(_persistence_test_app(settings)) as client:
        response = client.get(f"/api/v1/tasks?project_id={project_id}&limit=10&offset=10")
    assert response.status_code == 200
    assert response.json()["page"] == {"limit": 10, "offset": 10, "total": 20}
    assert len(response.json()["items"]) == 10


def test_seed_is_repeatable_and_preserves_unrelated_records() -> None:
    settings = _test_settings()
    database = Database(settings.database_url)
    unrelated_project_id = uuid4()
    unrelated_task_id = uuid4()
    try:
        with database.sessions.begin() as session:
            session.add(
                Project(
                    id=unrelated_project_id,
                    workspace_id=DEFAULT_WORKSPACE_ID,
                    name="Unrelated project",
                    customer="Synthetic",
                    description="Must remain unchanged",
                )
            )
            session.add(
                Task(
                    id=unrelated_task_id,
                    project_id=unrelated_project_id,
                    title="Unrelated task",
                    owner="Synthetic",
                    due=date(2026, 12, 1),
                    status="To do",
                )
            )

        seed(settings.database_url)
        first_snapshot = _seed_snapshot(database)
        seed(settings.database_url)
        second_snapshot = _seed_snapshot(database)

        assert first_snapshot == second_snapshot
        assert len(first_snapshot[0]) == 3
        assert len(first_snapshot[1]) == 60
        with database.sessions() as session:
            project = session.get(Project, unrelated_project_id)
            task = session.get(Task, unrelated_task_id)
            assert project is not None
            assert (project.name, project.customer, project.description) == (
                "Unrelated project",
                "Synthetic",
                "Must remain unchanged",
            )
            assert task is not None
            assert (task.project_id, task.title, task.owner, task.due, task.status) == (
                unrelated_project_id,
                "Unrelated task",
                "Synthetic",
                date(2026, 12, 1),
                "To do",
            )
    finally:
        database.engine.dispose()


def test_seed_failure_rolls_back_all_seed_writes() -> None:
    settings = _test_settings()
    database = Database(settings.database_url)
    target_task_id = task_id_for(PROJECTS[-1][0], 20)
    # Make the target observably dirty even if a prior test already seeded the
    # database; the listener can then fail on the final project's task flush.
    with database.sessions.begin() as session:
        target_task = session.get(Task, target_task_id)
        if target_task is not None:
            target_task.title = "Synthetic pre-failure value"
    before = _seed_snapshot(database)

    def fail_last_seed_task(session, _flush_context, _instances) -> None:
        pending_records = list(session.new) + list(session.dirty)
        if any(
            isinstance(record, Task) and record.id == target_task_id for record in pending_records
        ):
            raise RuntimeError("synthetic seed failure")

    event.listen(Session, "before_flush", fail_last_seed_task)
    try:
        with pytest.raises(RuntimeError, match="synthetic seed failure"):
            seed(settings.database_url)
        assert _seed_snapshot(database) == before
    finally:
        event.remove(Session, "before_flush", fail_last_seed_task)
        database.engine.dispose()


def _seed_snapshot(database: Database) -> tuple[tuple[tuple, ...], tuple[tuple, ...]]:
    project_ids = [project_id for project_id, *_ in PROJECTS]
    task_ids = [
        task_id_for(project_id, number) for project_id in project_ids for number in range(1, 21)
    ]
    with database.sessions() as session:
        projects = session.scalars(select(Project).where(Project.id.in_(project_ids))).all()
        tasks = session.scalars(select(Task).where(Task.id.in_(task_ids))).all()
    project_snapshot = tuple(
        sorted(
            (row.id, row.workspace_id, row.name, row.customer, row.description) for row in projects
        )
    )
    task_snapshot = tuple(
        sorted((row.id, row.project_id, row.title, row.owner, row.due, row.status) for row in tasks)
    )
    return project_snapshot, task_snapshot


def test_failed_audit_insert_rolls_back_project_write() -> None:
    settings = _test_settings()
    database = Database(settings.database_url)
    repository = PostgresRepository(database.sessions, DEFAULT_WORKSPACE_ID)
    project_id = uuid4()

    def fail_audit_flush(session, _flush_context, _instances) -> None:
        if any(isinstance(record, AuditEvent) for record in session.new):
            raise RuntimeError("synthetic audit insert failure")

    event.listen(Session, "before_flush", fail_audit_flush)
    try:
        with pytest.raises(RuntimeError, match="synthetic audit insert failure"):
            repository.create_project(
                project_id, ProjectCreate(name="Rollback check", customer="Synthetic")
            )
        with database.sessions() as session:
            assert session.get(Project, project_id) is None
            audit_count = session.scalar(
                select(func.count())
                .select_from(AuditEvent)
                .where(AuditEvent.entity_id == project_id)
            )
            assert audit_count == 0
    finally:
        event.remove(Session, "before_flush", fail_audit_flush)
        database.engine.dispose()


def test_database_rejects_task_with_unknown_project() -> None:
    settings = _test_settings()
    database = Database(settings.database_url)
    try:
        with pytest.raises(IntegrityError), database.sessions.begin() as session:
            session.add(
                Task(
                    project_id=UUID("30000000-0000-4000-8000-000000000001"),
                    title="Orphan task",
                    owner="Synthetic",
                    due=date(2026, 11, 15),
                    status="To do",
                )
            )
    finally:
        database.engine.dispose()
