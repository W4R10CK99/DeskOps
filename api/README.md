# OpsDesk API

The API is a separate FastAPI application. It uses PostgreSQL through SQLAlchemy and validates Auth0 OIDC access tokens before granting workspace access. There is no in-memory production fallback. Run Alembic migrations before starting the API. Project/task data stays mock-backed in the web app until the later frontend integration phase.

## Identity and authorization

Configure an Auth0 tenant, a Single Page Application, and an API. Set the issuer to the exact tenant issuer including its trailing slash, and use the API identifier as the audience in both applications. In the Auth0 SPA settings allow `http://localhost:5173` for callback, logout, and web origins. Keep the SPA client ID public; never put a client secret in Vite variables. The browser uses Auth0 authorization code + PKCE and keeps credentials in memory. It calls `GET /api/v1/workspaces` with a short-lived access token before displaying the workspace shell. This proves backend token validation, but project/task screens still use demo records.

Set these API variables in the backend process before starting it:

```powershell
$env:OPSDESK_OIDC_ISSUER = "https://your-tenant.example.auth0.com/"
$env:OPSDESK_OIDC_AUDIENCE = "https://opsdesk.example/api"
$env:OPSDESK_CORS_ORIGINS = "http://localhost:5173"
```

`OPSDESK_OIDC_JWKS_URL` is optional; by default the API uses `{issuer}/.well-known/jwks.json`. FastAPI verifies the RS256 signature against issuer keys and enforces issuer, audience, expiration, issued-at, and subject claims. Identity is `(issuer, sub)`; email is optional and never grants access. The API does not trust user, role, or workspace values from resource request bodies.

Protected project/task operations require `Authorization: Bearer <access-token>` and `X-Workspace-ID: <workspace-uuid>`. The selected workspace header is only a hint: a matching membership for the verified identity is required, and repository queries are scoped to that workspace. All workspace members can use the current project/task operations. Only owners can add a member or assign a role. Members may delete tasks; a project may be deleted only after its tasks are removed (otherwise `409 conflict`). Deletes are audited in the same transaction. Deleting an empty project detaches its document metadata (`project_id` becomes null) without deleting the metadata or any file bytes. `GET /api/v1/workspaces` lists only the caller's memberships; `GET /api/v1/documents/{id}` exposes metadata only after a workspace check. `/health` remains public and reports process health only.

For first-owner bootstrap, create/sign in the user in Auth0, copy its stable `sub` from the Auth0 user profile, run migrations, and use the privileged one-time command below. It refuses to add another bootstrap owner once the workspace already has one:

```powershell
python -m opsdesk_api.provision_owner --workspace-id 00000000-0000-4000-8000-000000000001 --subject "auth0|provider-user-id" --email "operator@example.com"
```

The command uses the configured `OPSDESK_DATABASE_URL` and `OPSDESK_OIDC_ISSUER`; database access is the trusted administrative boundary. Subsequent member additions must use the owner-only API operation. Real Auth0 sign-in/JWKS configuration requires the developer's tenant and was not simulated by automated tests.

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

For PostgreSQL integration coverage, create a separate database ending in `_test` (for example, from the repository root run `docker compose --env-file .env -f infra/compose.yaml exec postgres createdb -U opsdesk opsdesk_test`), set `$env:OPSDESK_TEST_DATABASE_URL` to its URL, and run `python -m pytest -vv`. Tests cover persistence, seed/pagination, rollback, and workspace authorization. The authorization suite creates two workspaces and three test identities and verifies scoped project/task/document-metadata access, owner/member checks, workspace-ID tampering, forged fields, cross-workspace DELETE denial, project deletion conflict while tasks exist, metadata detachment after permitted deletion, and non-leaking errors. Provider-independent tests verify signed JWT claims and failure paths. Without the test URL, PostgreSQL tests are skipped. A database-free regression test always verifies all 60 deterministic task IDs are unique.

## Data and boundaries

Alembic creates workspaces, memberships, projects, tasks, document metadata, and audit events. Project/task create, update, and delete operations write their audit event in the same transaction. Workspace membership listing and owner-only member creation are available; membership removal and owner transfer are not. Foreign keys restrict deletion of workspaces/projects; a project with tasks returns 409, and removing an empty project leaves linked document metadata detached (`project_id` set null). File bytes are not stored. The only document endpoint returns metadata after a workspace membership check. Private file upload/download is not implemented.

Project/task list filtering, sorting, pagination, and workspace-scoped deletion execute through the repository. The frontend continues to use feature-local mock data in `web/src/features/projects/data.ts`; the later integration phase will introduce a typed client under `web/src/api/` and swap data adapters without coupling the UI to backend modules.

Configuration is read from `OPSDESK_APP_NAME`, `OPSDESK_ENVIRONMENT`, `OPSDESK_LOG_LEVEL`, `OPSDESK_DATABASE_URL`, `OPSDESK_OIDC_ISSUER`, `OPSDESK_OIDC_AUDIENCE`, optional `OPSDESK_OIDC_JWKS_URL`, and `OPSDESK_CORS_ORIGINS`. The initial migration and app use the same stable local workspace UUID. `.env.example` contains local placeholders only; use real secrets only in ignored local files or deployment secret storage. No application-level API rate limiter is configured; Auth0 protects interactive sign-in, but API callers can still make repeated requests, so apply edge/API throttling before public deployment. Access tokens are stateless JWTs: logout clears the browser session but a copied token remains usable until expiry unless the issuer or a revocation mechanism rejects it. Keep access-token lifetime short and never log bearer headers or request bodies.

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
