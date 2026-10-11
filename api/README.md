# OpsDesk API

The backend is an independently run FastAPI application. Phase 02 establishes the versioned HTTP contract, Pydantic validation, error envelopes, request IDs, and tests. The repository implementation is in-memory only: projects and tasks reset when the API process restarts. PostgreSQL, migrations, authentication, authorization, uploads, and frontend integration remain later-phase work.

## Local setup

Requires Python 3.11 or newer.

```powershell
cd api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m uvicorn opsdesk_api.main:app --app-dir src --reload --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/docs` for Swagger UI, `http://127.0.0.1:8000/openapi.json` for the contract, and `http://127.0.0.1:8000/health` for process health.

Settings are read from `OPSDESK_APP_NAME`, `OPSDESK_ENVIRONMENT`, and `OPSDESK_LOG_LEVEL`; defaults are sufficient for local development. No secrets or `.env` file are required.

## Tests and checks

From `api/` with the virtual environment activated:

```powershell
python -m pytest
ruff check --no-cache src tests
ruff format --check --no-cache src tests
```

## API contract

All project and task resources are under `/api/v1`. Project and task list responses use `{ "items": [...], "page": { "limit": 50, "offset": 0, "total": 0 } }`. `limit` is bounded from 1 through 100. List endpoints support query filters, deterministic sort keys, and `asc`/`desc` ordering. Task `due` values use ISO 8601 dates (`YYYY-MM-DD`). The `X-Request-ID` response header and matching error-body `request_id` correlate requests and server logs.

Errors use `{ "error": { "code": "...", "message": "...", "details": [...] }, "request_id": "..." }`. Validation details omit raw submitted values. The OpenAPI schema distinguishes these cases:

- `400` — syntactically valid request rejected by an application rule.
- `401` — missing/invalid credentials (authentication is not implemented yet).
- `403` — authenticated caller lacks permission (authorization is not implemented yet).
- `404` — resource or route not found.
- `409` — state conflict (no uniqueness/conflict rule is active yet).
- `422` — body, path, or query validation failed.
- `429` — rate limit exceeded (rate limiting is not implemented yet).
- `500` — unexpected failure; response details are withheld and the request ID is logged.

The future-only cases are documented for a consistent contract and are not simulated by placeholder routes.

## Implemented routes

- `GET /health` — confirms the API process responds; it does not check a database.
- `GET|POST /api/v1/projects`, `GET|PATCH /api/v1/projects/{project_id}` — search/list, create, read, and update projects.
- `GET|POST /api/v1/projects/{project_id}/tasks` — list tasks in an existing project and create a project task.
- `GET /api/v1/tasks`, `GET|PATCH /api/v1/tasks/{task_id}` — filter/list, read, and update tasks.

The frontend still uses `web/src/features/projects/data.ts` and feature-local component state. A later integration task will add a typed HTTP client behind the frontend data boundary and switch workflows in the designated phase; this Phase 02 API does not change frontend behavior.
