"""PostgreSQL cross-user and cross-workspace authorization tests.

Run only with OPSDESK_TEST_DATABASE_URL pointing at a dedicated *_test database.
"""

import os
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
import pytest
from fastapi.testclient import TestClient

from opsdesk_api.config import Settings
from opsdesk_api.database.models import DocumentMetadata, Membership, Project, Task, Workspace
from opsdesk_api.database.session import Database
from opsdesk_api.main import create_app

DATABASE_URL = os.getenv("OPSDESK_TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(not DATABASE_URL, reason="OPSDESK_TEST_DATABASE_URL is not set")
ISSUER = "https://opsdesk-test.example/"
AUDIENCE = "https://opsdesk-test.example/api"


def _database() -> Database:
    assert DATABASE_URL is not None
    database_name = DATABASE_URL.rsplit("/", maxsplit=1)[-1].split("?", maxsplit=1)[0]
    if not database_name.endswith("_test"):
        pytest.fail("OPSDESK_TEST_DATABASE_URL must target a database whose name ends in _test")
    if not DATABASE_URL.startswith("postgresql+psycopg://"):
        pytest.fail("Authorization integration tests require PostgreSQL")
    return Database(DATABASE_URL)


@pytest.fixture(scope="module", autouse=True)
def migrate_database() -> None:
    from alembic import command
    from alembic.config import Config

    database = _database()
    try:
        with database.engine.connect() as connection:
            if connection.dialect.name != "postgresql":
                pytest.fail("Authorization integration tests require PostgreSQL")
    finally:
        database.engine.dispose()
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", DATABASE_URL.replace("%", "%%"))
    config.attributes["database_url"] = DATABASE_URL
    command.upgrade(config, "head")


def _insert_fixture_records(database: Database) -> dict[str, str]:
    workspace_a, workspace_b = uuid4(), uuid4()
    owner_a, member_a, owner_b = uuid4(), uuid4(), uuid4()
    project_a, project_b = uuid4(), uuid4()
    task_a, doc_a, doc_b = uuid4(), uuid4(), uuid4()
    user_a, user_b, user_c = f"user-a-{owner_a}", f"user-b-{member_a}", f"user-c-{owner_b}"
    with database.sessions.begin() as session:
        session.add_all(
            [
                Workspace(id=workspace_a, name=f"Isolation A {workspace_a}"),
                Workspace(id=workspace_b, name=f"Isolation B {workspace_b}"),
            ]
        )
        session.flush()
        session.add_all(
            [
                Membership(
                    id=owner_a,
                    workspace_id=workspace_a,
                    identity_issuer=ISSUER,
                    identity_subject=user_a,
                    email=None,
                    role="owner",
                ),
                Membership(
                    id=member_a,
                    workspace_id=workspace_a,
                    identity_issuer=ISSUER,
                    identity_subject=user_b,
                    email=None,
                    role="member",
                ),
                Membership(
                    id=owner_b,
                    workspace_id=workspace_b,
                    identity_issuer=ISSUER,
                    identity_subject=user_c,
                    email=None,
                    role="owner",
                ),
            ]
        )
        session.flush()
        session.add_all(
            [
                Project(
                    id=project_a,
                    workspace_id=workspace_a,
                    name="Private project A",
                    customer="Customer A",
                    description="Workspace A",
                ),
                Project(
                    id=project_b,
                    workspace_id=workspace_b,
                    name="Private project B",
                    customer="Customer B",
                    description="Workspace B",
                ),
            ]
        )
        session.flush()
        session.add(
            Task(
                id=task_a,
                project_id=project_a,
                title="Task A",
                owner="User A",
                due=datetime(2026, 12, 1).date(),
                status="To do",
            )
        )
        session.flush()
        session.add_all(
            [
                DocumentMetadata(
                    id=doc_a,
                    workspace_id=workspace_a,
                    project_id=project_a,
                    name="Workspace A brief",
                    content_type="text/plain",
                ),
                DocumentMetadata(
                    id=doc_b,
                    workspace_id=workspace_b,
                    project_id=project_b,
                    name="Workspace B brief",
                    content_type="text/plain",
                ),
            ]
        )
    return {
        "workspace_a": str(workspace_a),
        "workspace_b": str(workspace_b),
        "project_a": str(project_a),
        "project_b": str(project_b),
        "task_a": str(task_a),
        "doc_a": str(doc_a),
        "doc_b": str(doc_b),
        "user_a": user_a,
        "user_b": user_b,
        "user_c": user_c,
    }


def test_workspace_membership_enforces_roles_and_resource_isolation(monkeypatch) -> None:
    from cryptography.hazmat.primitives.asymmetric import rsa

    database = _database()
    ids = _insert_fixture_records(database)
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    class TestJwks:
        def get_signing_key_from_jwt(self, _token):
            from types import SimpleNamespace

            return SimpleNamespace(key=key.public_key())

    settings = Settings(
        database_url=DATABASE_URL,
        oidc_issuer=ISSUER,
        oidc_audience=AUDIENCE,
    )
    app = create_app(settings=settings)
    app.state.jwks_client = TestJwks()

    def bearer(subject: str, *, audience: str = AUDIENCE, expires: int = 300) -> dict[str, str]:
        now = datetime.now(UTC)
        token = jwt.encode(
            {
                "iss": ISSUER,
                "aud": audience,
                "sub": subject,
                "iat": now,
                "exp": now + timedelta(seconds=expires),
            },
            key,
            algorithm="RS256",
            headers={"kid": "phase-04-test"},
        )
        return {"Authorization": f"Bearer {token}"}

    try:
        with TestClient(app) as client:
            owner_headers = {**bearer(ids["user_a"]), "X-Workspace-ID": ids["workspace_a"]}
            member_headers = {**bearer(ids["user_b"]), "X-Workspace-ID": ids["workspace_a"]}
            other_headers = {**bearer(ids["user_c"]), "X-Workspace-ID": ids["workspace_b"]}

            owner_projects = client.get("/api/v1/projects", headers=owner_headers)
            assert owner_projects.status_code == 200
            assert [row["id"] for row in owner_projects.json()["items"]] == [ids["project_a"]]
            owner_workspaces = client.get("/api/v1/workspaces", headers=bearer(ids["user_a"]))
            assert owner_workspaces.status_code == 200
            assert [row["id"] for row in owner_workspaces.json()] == [ids["workspace_a"]]

            # Workspace members can collaborate on that workspace's records.
            assert (
                client.get(
                    f"/api/v1/projects/{ids['project_a']}", headers=member_headers
                ).status_code
                == 200
            )

            # Changing either the resource ID or workspace selector cannot cross tenant scope.
            assert (
                client.get(
                    f"/api/v1/projects/{ids['project_a']}", headers=other_headers
                ).status_code
                == 404
            )
            assert (
                client.patch(
                    f"/api/v1/projects/{ids['project_a']}",
                    headers=other_headers,
                    json={"name": "attempted takeover"},
                ).status_code
                == 404
            )
            assert (
                client.delete(
                    f"/api/v1/projects/{ids['project_a']}", headers=other_headers
                ).status_code
                == 404
            )
            assert (
                client.delete(f"/api/v1/tasks/{ids['task_a']}", headers=other_headers).status_code
                == 404
            )
            assert (
                client.get(f"/api/v1/tasks/{ids['task_a']}", headers=other_headers).status_code
                == 404
            )
            assert (
                client.patch(
                    f"/api/v1/tasks/{ids['task_a']}",
                    headers=other_headers,
                    json={"title": "attempted task takeover"},
                ).status_code
                == 404
            )
            changed_workspace = client.get(
                f"/api/v1/projects/{ids['project_a']}",
                headers={**bearer(ids["user_c"]), "X-Workspace-ID": ids["workspace_a"]},
            )
            assert changed_workspace.status_code == 404
            missing_project = client.get(
                "/api/v1/projects/10000000-0000-4000-8000-000000000000",
                headers=other_headers,
            )
            foreign_project = client.get(
                f"/api/v1/projects/{ids['project_a']}", headers=other_headers
            )
            assert missing_project.json()["error"] == foreign_project.json()["error"]
            assert (
                client.get(f"/api/v1/documents/{ids['doc_a']}", headers=other_headers).status_code
                == 404
            )
            assert (
                client.get(f"/api/v1/documents/{ids['doc_b']}", headers=other_headers).status_code
                == 200
            )

            # A project with tasks is preserved; workspace members may then remove
            # the task and its now-empty project. Metadata remains in-workspace and
            # is detached from the deleted project by the database FK.
            blocked_delete = client.delete(
                f"/api/v1/projects/{ids['project_a']}", headers=member_headers
            )
            assert blocked_delete.status_code == 409
            assert (
                client.get(
                    f"/api/v1/projects/{ids['project_a']}", headers=owner_headers
                ).status_code
                == 200
            )

            assert (
                client.delete(f"/api/v1/tasks/{ids['task_a']}", headers=member_headers).status_code
                == 204
            )
            assert (
                client.get(f"/api/v1/tasks/{ids['task_a']}", headers=owner_headers).status_code
                == 404
            )
            assert (
                client.delete(
                    f"/api/v1/projects/{ids['project_a']}", headers=member_headers
                ).status_code
                == 204
            )
            assert (
                client.get(
                    f"/api/v1/projects/{ids['project_a']}", headers=owner_headers
                ).status_code
                == 404
            )
            document = client.get(f"/api/v1/documents/{ids['doc_a']}", headers=owner_headers)
            assert document.status_code == 200
            assert document.json()["project_id"] is None

            forged_workspace = client.post(
                "/api/v1/projects",
                headers=owner_headers,
                json={
                    "name": "Forged",
                    "customer": "Test",
                    "workspace_id": ids["workspace_b"],
                    "role": "owner",
                },
            )
            assert forged_workspace.status_code == 422

            member_add = client.post(
                f"/api/v1/workspaces/{ids['workspace_a']}/members",
                headers=member_headers,
                json={"identity_subject": "new-user", "role": "owner"},
            )
            assert member_add.status_code == 403
            unassigned_add = client.post(
                f"/api/v1/workspaces/{ids['workspace_a']}/members",
                headers={
                    **bearer("user-not-in-workspace"),
                    "X-Workspace-ID": ids["workspace_a"],
                },
                json={"identity_subject": "user-not-in-workspace", "role": "owner"},
            )
            assert unassigned_add.status_code == 404

            owner_add = client.post(
                f"/api/v1/workspaces/{ids['workspace_a']}/members",
                headers=owner_headers,
                json={"identity_subject": "new-user", "role": "member"},
            )
            assert owner_add.status_code == 201
            assert owner_add.json()["role"] == "member"

            unassigned = client.get(
                "/api/v1/projects",
                headers={**bearer("user-not-in-workspace"), "X-Workspace-ID": ids["workspace_a"]},
            )
            assert unassigned.status_code == 404
            assert unassigned.json()["error"]["code"] == "workspace_not_found"

            wrong_audience = client.get(
                "/api/v1/projects",
                headers={
                    **bearer(ids["user_a"], audience="https://other.example/api"),
                    "X-Workspace-ID": ids["workspace_a"],
                },
            )
            assert wrong_audience.status_code == 401
    finally:
        database.engine.dispose()
