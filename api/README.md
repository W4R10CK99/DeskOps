# OpsDesk API

The API is a separate FastAPI application. The Phase 02 HTTP contract and Pydantic schemas remain in place; production app instances now use PostgreSQL through SQLAlchemy. There is no in-memory fallback. Run Alembic migrations before starting the API. Local project/task routes operate in the seeded `OpsDesk Local` workspace until authentication and workspace selection arrive in later phases.

## Local PostgreSQL

Requires Docker Compose and Python 3.11 or newer. From the repository root:

```powershell
Copy-Item .env.example .env
docker compose --env-file .env -f infra/compose.yaml up -d
docker compose --env-file .env -f infra/compose.yaml ps
```

The Compose service has a named volume and health check. To stop PostgreSQL while keeping its data, run `docker compose --env-file .env -f infra/compose.yaml down`. Do not use `down -v` unless intentionally deleting the local database.

## Install, migrate, and run

```powershell
cd api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
$env:OPSDESK_DATABASE_URL = "postgresql+psycopg://opsdesk:opsdesk@localhost:5432/opsdesk"
python -m alembic -c alembic.ini upgrade head
python -m alembic -c alembic.ini current
python -m uvicorn opsdesk_api.main:app --app-dir src --reload --host 127.0.0.1 --port 8000
```

The API checks the database connection on startup and fails visibly if PostgreSQL is unavailable. It does not create tables on startup. Swagger UI is at `http://127.0.0.1:8000/docs`; the OpenAPI document is at `/openapi.json`. `GET /health` reports process health, not database readiness.

## Demo data

After applying migrations, from `api/` with the same database URL configured, run:

```powershell
python -m opsdesk_api.seed
```

This repeatably inserts or updates three synthetic projects and 60 tasks with stable IDs. Task IDs are generated in a project-specific UUID namespace. All project/task changes share one transaction, so a failed seed rolls back the complete dataset. It does not seed memberships, documents, or audit history.

## Tests and checks

Contract tests use the in-memory repository as an isolated unit-test adapter. PostgreSQL integration tests require a separate database ending in `_test`; create that database explicitly, then set its URL before running tests. The suite applies migrations to that database and never drops tables or data.

```powershell
python -m pytest
ruff check --no-cache src tests migrations
ruff format --check --no-cache src tests migrations
```

For PostgreSQL integration coverage, create a separate database ending in `_test` (for example, from the repository root run `docker compose --env-file .env -f infra/compose.yaml exec postgres createdb -U opsdesk opsdesk_test`), set `$env:OPSDESK_TEST_DATABASE_URL` to a URL such as `postgresql+psycopg://opsdesk:opsdesk@localhost:5432/opsdesk_test`, and run `python -m pytest`. Tests cover process-restart persistence, seed-backed pagination, repeated seeding and preservation of unrelated records, seed transaction rollback, a database foreign-key constraint, and rollback after an injected failure during the audit flush. Without that environment variable, PostgreSQL integration tests are skipped and must not be reported as passed. A database-free regression test always verifies all 60 deterministic task IDs are unique.

## Data and boundaries

Alembic creates workspaces, memberships, projects, tasks, document metadata, and audit events. Membership email/role are structural records only; authentication, authorization, and tenant isolation are not implemented. Project/task create and update operations write their audit event in the same transaction. Foreign keys restrict deletion of workspaces/projects; removing a project leaves linked document metadata detached (`project_id` set null). File bytes are not stored. Document metadata, membership, and audit tables do not have public CRUD endpoints in this phase.

Project/task list filtering, sorting, and pagination execute through the repository. The frontend continues to use feature-local mock data in `web/src/features/projects/data.ts`; the later integration phase will introduce a typed client under `web/src/api/` and swap data adapters without coupling the UI to backend modules.

Configuration is read from `OPSDESK_APP_NAME`, `OPSDESK_ENVIRONMENT`, `OPSDESK_LOG_LEVEL`, and `OPSDESK_DATABASE_URL`. The initial migration and app use the same stable local workspace UUID. `.env.example` contains local placeholders only; use real secrets only in ignored local files or deployment secret storage.

## Query/index review

The task list with a project filter and due-date sort is backed by `(project_id, due)`; the status-filtered due-date list is backed by `(status, due)`. Project list ordering within the default workspace uses `(workspace_id, name)` or `(workspace_id, customer)`. Document indexes cover workspace/project foreign-key lookups, and audit history is ordered by `(workspace_id, created_at)`. After seeding a PostgreSQL database, inspect the common task query with:

```sql
EXPLAIN SELECT t.id, t.project_id, t.title, t.owner, t.due, t.status
FROM tasks AS t
JOIN projects AS p ON p.id = t.project_id
WHERE t.project_id = '10000000-0000-4000-8000-000000000001'
  AND p.workspace_id = '00000000-0000-4000-8000-000000000001'
ORDER BY t.due, t.id
LIMIT 50;
```

### Recorded development plan

The user reports running the query above against the seeded development database. PostgreSQL chose an index scan using `ix_projects_workspace_customer` on `projects`, applying the workspace condition and project-ID filter, followed by a nested-loop join. It sequentially scanned `tasks` with a `project_id` filter, then sorted by `t.due, t.id`. The estimates were 20 matching rows and total cost approximately 11.59.

The task-table sequential scan is reasonable for this small local dataset; do not add an index only to force index usage. `EXPLAIN` reports planner estimates and costs, not actual execution timings. Use `EXPLAIN ANALYZE` separately if measured execution time is needed, understanding that it executes the query. The observed plan and existing index rationale satisfy the p3-t07 review; revisit indexes only after representative data and measured query behavior justify a change.
