"""API contract, validation, and failure behavior tests."""

import json
from uuid import UUID

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from opsdesk_api.config import Settings
from opsdesk_api.database.session import Database
from opsdesk_api.errors import ERROR_USE_CASES, STATUS_CODES
from opsdesk_api.main import create_app
from opsdesk_api.repositories.memory import InMemoryRepository
from opsdesk_api.repositories.postgres import PostgresRepository
from opsdesk_api.routers.dependencies import project_service


def create_project(client: TestClient, name: str = "Northstar") -> dict:
    response = client.post(
        "/api/v1/projects",
        json={
            "name": name,
            "customer": "Northstar Health",
            "description": f"{name} project",
        },
    )
    assert response.status_code == 201
    return response.json()


def create_task(client: TestClient, project_id: str, title: str, due: str) -> dict:
    response = client.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": title, "owner": "Maya Chen", "due": due},
    )
    assert response.status_code == 201
    return response.json()


def test_health_has_request_id(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert UUID(response.headers["X-Request-ID"])


def test_cors_preflight_allows_only_configured_frontend_origin() -> None:
    app = create_app(
        settings=Settings(cors_origins=("http://localhost:5173",)),
        repository=InMemoryRepository(),
    )
    with TestClient(app) as test_client:
        allowed = test_client.options(
            "/api/v1/projects",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "authorization,x-workspace-id",
            },
        )
        denied = test_client.options(
            "/api/v1/projects",
            headers={
                "Origin": "https://untrusted.example",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "authorization,x-workspace-id",
            },
        )

    assert allowed.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert "access-control-allow-origin" not in denied.headers


def test_cors_configuration_rejects_wildcard_origins(monkeypatch) -> None:
    monkeypatch.setenv("OPSDESK_CORS_ORIGINS", "*")

    with pytest.raises(ValueError, match="explicit origin allowlist"):
        Settings.from_environment()


def test_production_app_uses_postgres_without_memory_fallback() -> None:
    app = create_app(settings=Settings(database_url="postgresql+psycopg://ops:ops@localhost/test"))
    try:
        assert isinstance(app.state.repository, PostgresRepository)
    finally:
        app.state.database.engine.dispose()


def test_database_configuration_rejects_non_postgres_driver() -> None:
    with pytest.raises(ValueError, match=r"postgresql\+psycopg"):
        Database("sqlite:///./opsdesk.db")


def test_project_and_task_create_read_update(client: TestClient) -> None:
    project = create_project(client)
    project_id = project["id"]
    assert project["task_count"] == 0
    assert client.get(f"/api/v1/projects/{project_id}").json()["name"] == "Northstar"

    task = create_task(client, project_id, "Confirm requirements", "2026-10-14")
    assert task["due"] == "2026-10-14"
    assert task["status"] == "To do"

    project_update = client.patch(
        f"/api/v1/projects/{project_id}", json={"name": "Northstar onboarding"}
    )
    task_update = client.patch(f"/api/v1/tasks/{task['id']}", json={"status": "In progress"})
    assert project_update.status_code == 200
    assert project_update.json()["name"] == "Northstar onboarding"
    assert task_update.status_code == 200
    assert task_update.json()["status"] == "In progress"
    assert client.get(f"/api/v1/projects/{project_id}").json()["task_count"] == 1


def test_delete_task_then_empty_project(client: TestClient) -> None:
    project = create_project(client)
    task = create_task(client, project["id"], "Remove after review", "2026-10-14")

    blocked = client.delete(f"/api/v1/projects/{project['id']}")
    assert blocked.status_code == 409
    assert blocked.json()["error"]["code"] == "conflict"

    deleted_task = client.delete(f"/api/v1/tasks/{task['id']}")
    assert deleted_task.status_code == 204
    assert deleted_task.content == b""
    assert client.get(f"/api/v1/tasks/{task['id']}").status_code == 404

    deleted_project = client.delete(f"/api/v1/projects/{project['id']}")
    assert deleted_project.status_code == 204
    assert client.get(f"/api/v1/projects/{project['id']}").status_code == 404

    missing = client.delete("/api/v1/tasks/10000000-0000-4000-8000-000000000000")
    assert missing.status_code == 404


def test_project_filter_sort_and_pagination(client: TestClient) -> None:
    create_project(client, "Zulu launch")
    create_project(client, "Alpha rollout")
    create_project(client, "Another launch")

    page = client.get("/api/v1/projects?q=launch&sort=name&order=asc&limit=1&offset=1")

    assert page.status_code == 200
    assert [item["name"] for item in page.json()["items"]] == ["Zulu launch"]
    assert page.json()["page"] == {"limit": 1, "offset": 1, "total": 2}


def test_task_filter_sort_and_pagination(client: TestClient) -> None:
    project = create_project(client)
    first = create_task(client, project["id"], "Zulu task", "2026-10-20")
    create_task(client, project["id"], "Alpha task", "2026-10-12")
    client.patch(f"/api/v1/tasks/{first['id']}", json={"status": "Review"})

    page = client.get(f"/api/v1/tasks?project_id={project['id']}&status=Review&sort=title&limit=1")

    assert page.status_code == 200
    assert [item["title"] for item in page.json()["items"]] == ["Zulu task"]
    assert page.json()["page"]["total"] == 1


def test_invalid_body_and_query_return_safe_error_envelope(client: TestClient) -> None:
    invalid = client.post("/api/v1/projects", json={"name": "   ", "customer": "Acme"})
    invalid_query = client.get("/api/v1/projects?limit=101")

    assert invalid.status_code == 422
    assert invalid.json()["error"]["code"] == "validation_error"
    assert invalid.json()["request_id"] == invalid.headers["X-Request-ID"]
    assert "input" not in json.dumps(invalid.json()).lower()
    assert invalid_query.status_code == 422


def test_patch_requires_at_least_one_non_null_field(client: TestClient) -> None:
    project = create_project(client)

    empty_patch = client.patch(f"/api/v1/projects/{project['id']}", json={})
    null_patch = client.patch(f"/api/v1/projects/{project['id']}", json={"name": None})

    assert empty_patch.status_code == null_patch.status_code == 422


def test_missing_resources_use_consistent_404(client: TestClient) -> None:
    missing_project = client.get("/api/v1/projects/10000000-0000-4000-8000-000000000000")
    missing_task = client.get("/api/v1/tasks/10000000-0000-4000-8000-000000000000")

    assert missing_project.status_code == missing_task.status_code == 404
    assert missing_project.json()["error"]["code"] == "not_found"
    assert UUID(missing_project.headers["X-Request-ID"])


def test_unknown_project_cannot_receive_tasks(client: TestClient) -> None:
    response = client.post(
        "/api/v1/projects/10000000-0000-4000-8000-000000000000/tasks",
        json={"title": "Task", "owner": "Maya Chen", "due": "2026-10-14"},
    )
    assert response.status_code == 404
    assert response.json()["error"]["message"] == "Project not found"


def test_unexpected_failure_is_sanitized_and_correlated(app: FastAPI) -> None:
    class BrokenProjectService:
        def list_projects(self, **_kwargs):
            raise RuntimeError("sensitive internal detail")

    app.dependency_overrides[project_service] = lambda: BrokenProjectService()
    response = TestClient(app, raise_server_exceptions=False).get("/api/v1/projects")

    assert response.status_code == 500
    assert response.json()["error"] == {
        "code": "internal_error",
        "message": "An unexpected error occurred",
        "details": None,
    }
    assert "sensitive internal detail" not in response.text
    assert response.json()["request_id"] == response.headers["X-Request-ID"]


def test_openapi_documents_versioned_contract_and_error_envelope(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()

    assert "/health" in schema["paths"]
    assert "/api/v1/projects" in schema["paths"]
    assert "/api/v1/projects/{project_id}/tasks" in schema["paths"]
    assert "/api/v1/tasks/{task_id}" in schema["paths"]
    responses = schema["paths"]["/api/v1/projects"]["post"]["responses"]
    assert responses["422"]["content"]
    for code, description in ERROR_USE_CASES.items():
        assert responses[str(code)]["description"] == description


def test_status_code_guidance_covers_tracker_http_classes() -> None:
    expected = {400, 401, 403, 404, 409, 422, 429, 500}

    assert expected <= set(STATUS_CODES) | {500}
    assert expected <= set(ERROR_USE_CASES)
