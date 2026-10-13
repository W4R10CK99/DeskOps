# Ordered backlog

The tracker `FDE_End_to_End_Build_Tracker_Ram.html` is authoritative. Tasks remain open until acceptance criteria and phase gates are verified; implementation presence alone is not completion.

## Phase 00 — Define the product before writing code

- [x] p0-t00 Problem statement — recorded in product brief.
- [x] p0-t01 Primary user and workflows — recorded in product brief.
- [x] p0-t02 Observable acceptance criteria, including failure/empty states — recorded in product brief.
- [x] p0-t03 V1 non-goals — recorded in product brief.
- [x] p0-t04 Main pages and user flow sketch — recorded in architecture.
- [x] p0-t05 System diagram, boundaries, and data/secret placement — recorded in architecture.
- [x] p0-t06 Monorepo foundation, README, `.env.example`, `.gitignore` — root Git repository and requested ownership folders created; Phase 01 frontend tooling is validated.
- [x] p0-t07 Ordered dependency-aware backlog — this document.

## Phase 01 — Frontend: build the product shell

- [x] p1-t00 React + TypeScript + Vite dev/build workflow — installed with a generated lockfile.
- [x] p1-t01 Routes and shared navigation for Dashboard, Projects, Project Detail, Documents, Settings.
- [x] p1-t02 Reusable Button, Input, Modal, Table/List, StatusBadge, Loading components.
- [x] p1-t03 Project/task list/detail and create/edit with local mock data and stable IDs.
- [x] p1-t04 Meaningful loading, empty, validation, error, success states on primary screens — mock state preview controls exercise loading/error; route-level empty states, browser required-field validation, and success notifications are present.
- [x] p1-t05 Narrow layouts, keyboard navigation, labeled inputs, basic accessibility pass — checked mobile navigation and page/table widths; verified modal focus wrapping and required field labels in the browser.
- [x] p1-t06 Linting, formatting, TypeScript checks, reproducible build — all pass locally.
- [ ] p1-t07 Record a short frontend demo and list gaps before backend integration — integration gaps are documented; the video remains pending and the user waived it for proceeding to Phase 02. This item remains open, not complete.

## Phase 02 — Backend: design a real API

- [x] p2-t00 FastAPI service, environment configuration, and `/health` endpoint — app factory/settings boundary and live health response verified.
- [x] p2-t01 Versioned `/api/v1` project/task routes with explicit Pydantic request/response schemas — project/task create, read, update, and list contracts are present.
- [x] p2-t02 Boundary validation and a consistent error envelope with HTTP status guidance for 400/401/403/404/409/422/429/500 — request-body/query validation returns a sanitized 422 envelope; live missing-resource request returns 404; shared status guidance is in OpenAPI.
- [x] p2-t03 Separate routers, schemas, business services, and a persistence interface without adding database persistence early — services use an `OpsRepository` protocol with an explicitly ephemeral in-memory implementation.
- [x] p2-t04 Project/task filtering, deterministic sorting, and bounded list pagination — `limit` is constrained to 1–100 with offset, filters, and sort options; covered by tests.
- [x] p2-t05 Request IDs and structured logs that omit credentials and request payloads — response/error IDs match; live JSON logs include method/path/status/duration/environment only.
- [x] p2-t06 Review generated OpenAPI and exercise real HTTP endpoints, including error responses — OpenAPI paths checked; live Uvicorn health, OpenAPI, validation (422), and not-found (404) requests verified.
- [x] p2-t07 Automated API tests for valid and invalid input, missing resources, and unexpected failures — 11 pytest tests passed.

## Phase 03 — Persistence: PostgreSQL and data modelling

- [x] p3-t00 Run PostgreSQL locally and connect the backend using configuration and a connection pool — Compose defines the named `opsdesk-postgres-data` volume, `pg_isready` health check, and restart policy; the API checks PostgreSQL at startup. User confirms restarting the PostgreSQL container, reconnecting to the database, and verifying its content remained persistent.
- [x] p3-t01 Model Workspace, Membership, Project, Task, Document metadata, and AuditEvent tables — six ORM models include workspace relationships and optional membership ownership references; identity/authentication remains out of scope.
- [x] p3-t02 Add primary keys, foreign keys, not-null/unique/check constraints, and query-justified indexes — SQLAlchemy metadata and PostgreSQL DDL include the constraints and indexes; Alembic revision `20261011_0001 (head)` was reported on the development database and PostgreSQL-backed CRUD was manually exercised. Fresh-database migration evidence is recorded under p3-t03.
- [x] p3-t03 Add Alembic migrations and prove a fresh database can be created from zero — user reports successfully running `alembic upgrade head` against disposable `opsdesk_migration_check` and confirming the expected tables were created; development DB is at `20261011_0001 (head)`.
- [x] p3-t04 Replace mock/in-memory repositories with PostgreSQL persistence and verify records survive restart — user reports successful Swagger project/task CRUD/list operations and confirms records remained after restarting the API.
- [x] p3-t05 Use transactions for multi-step writes and demonstrate rollback — controlled failure during the final seed-task flush on development PostgreSQL left the pre-existing seed dataset unchanged; user also reports all 20 PostgreSQL integration tests passed with zero skipped.
- [x] p3-t06 Seed a repeatable demo dataset and test pagination against enough rows — two seed runs left exactly three projects and 60 tasks; the PostgreSQL-backed API returned 10 tasks from a page with 20 total. User reports the PostgreSQL integration suite passed; demo data remains behind the backend seed command, not hard-coded in frontend components.
- [x] p3-t07 Inspect one query with EXPLAIN and document why indexes exist — user reports an index scan on `ix_projects_workspace_customer`, nested-loop join, task-table sequential scan filtered by `project_id`, then sort by `t.due, t.id`; estimates were 20 rows and cost approximately 11.59. This plan is recorded in `api/README.md`; the small-table sequential scan is reasonable, and no index was added just to force index use. `EXPLAIN` values are estimates, not measured execution times.

PostgreSQL test status: the user reports the PostgreSQL integration run completed with 20 passed and 0 skipped. This result was supplied by the user and was not independently rerun in this session. The rerun in this Codex environment reported 14 passed and 6 skipped because its `OPSDESK_TEST_DATABASE_URL` was unset; that separate result is not the user's latest test run. Manual Swagger checks and direct development-database checks remain separately identified.

Phase 03 exit gate: satisfied based on the evidence above. Phase 04 is now underway; Phase 03 work is unchanged apart from the additive identity migration.

## Dependencies and sequence

1. Complete the shell/tooling and shared route/components (p1-t00–02).
2. Add mock workflows and screen states (p1-t03–04).
3. Complete responsive/accessibility and quality checks (p1-t05–06).
4. Record the demo, document integration gaps, and pass the Phase 01 exit gate (p1-t07). The user has waived the recording for the current Phase 02 work; keep p1-t07 open until a real recording is made.
5. Complete and verify Phase 02 API tasks (p2-t00–07), then complete Phase 03 p3-t00 through p3-t07 before beginning Phase 04. Phase 03 is now complete; its evidence and the first Phase 04 task are recorded above.

## Later phases

Phase 04–12 remain planned in the HTML tracker. In particular, Phase 07 deployed-core exit gate blocks AI/RAG/agent work.

## Phase 04 — Authentication, authorization, and workspace isolation

- [x] p4-t00 Choose and document a maintained OIDC/auth provider or a well-understood session approach — Auth0 managed OIDC was selected in ADR 0002. React uses the maintained SPA SDK with authorization code + PKCE and memory-only tokens; FastAPI validates audience-bound access tokens. The user reports configuring a local Auth0 tenant for manual verification; no provider secrets were added to the repository.
- [ ] p4-t01 Implement sign-up/sign-in, sign-out, session expiry, and unauthenticated route flow — user-confirmed Auth0 browser checks verified sign-in to the workspace dashboard, sign-out, denial of workspace access for a second user without membership, and owner success/unprovisioned-user denial on the workspace API. Expired/revoked credential handling is still not manually verified, so this task remains open.
- [x] p4-t02 Make the backend validate identity tokens using maintained libraries and expected issuer/audience/expiry — PyJWT RS256/JWKS verification checks issuer, audience, `exp`, `iat`, and `sub`; RSA-backed unit tests pass for valid and rejected tokens. The user-confirmed successful workspace API request with a real Auth0 owner token is manual evidence that a live tenant token was accepted; key rotation/network-failure cases remain outside the verified flow.
- [x] p4-t03 Protect API routes and derive current identity from verified credentials — project/task routes require bearer identity and membership; `/health` is public; workspace and metadata routes are protected. Anonymous/malformed credentials and PostgreSQL-scoped requests were exercised by the passing tests.
- [x] p4-t04 Implement workspace membership and owner/member checks — migrations `20261012_0002`–`0003` map identity by `(issuer, subject)` and keep email informational; workspace-scoped repositories, owner-only member provisioning, and a first-owner CLI are implemented. The PostgreSQL suite passed, and a separate database upgraded from `20261011_0001` to head while preserving pre-existing membership, project, and task rows.
- [ ] p4-t05 Prove cross-user and cross-workspace read/update/delete/document isolation — existing PostgreSQL tests cover scoped project/task reads and updates, document-metadata access, and non-leaking 404s. Added workspace-scoped DELETE routes and authorization cases: task deletion is allowed to a member of that workspace; project deletion is allowed only with no tasks (otherwise 409); project-linked metadata remains available and is detached by the FK. These new PostgreSQL cases were not exercised in the current run because `OPSDESK_TEST_DATABASE_URL` was unset; the in-memory API deletion contract test passed. Keep open until the PostgreSQL authorization suite passes. Project/task records are shared within a workspace, not user-private. Document bytes/download remain Phase 05 and are deliberately out of scope here.
- [x] p4-t06 Choose/configure browser credential handling — Auth0 SPA SDK uses PKCE, in-memory token caching, no browser client secret, no refresh-token persistence, and bearer requests (no auth cookies/CSRF surface). CORS uses explicit origins with credentials disabled. User-confirmed live sign-in and sign-out exercised the configured browser flow; automated frontend checks passed. Expired/revoked-credential behavior remains tracked under p4-t01.
- [x] p4-t07 Security review — reviewed CORS, boundary validation, identity/membership checks, error handling, and sensitive-data logging. Automated API tests passed CORS allow/deny and wildcard rejection. `pip-audit --local` initially found 24 advisory entries across local `pip 23.1.2`, `setuptools 65.5.0`, and dev `pytest 8.4.2`; upgraded the isolated API venv to pip 26.2.1, setuptools 84.0.0, pytest 9.1.1, and changed the dev constraint to `pytest>=9.0.3,<10`. The rerun reported no known vulnerabilities in installed dependencies; the local `opsdesk-api` package itself is not in PyPI and was skipped. No API rate limiter is implemented; Auth0 protects interactive login, but edge/API throttling is needed before public exposure. Self-contained JWTs are not immediately revocable on logout; short expiry limits the window. `.env` is ignored and examples use placeholders; no frontend client secret is used. Limitations are recorded in the threat model and API README.
- [x] p4-t08 Write a threat model — `docs/threat-model-phase-04.md` records the required threats, assets, attack paths, mitigations, user-confirmed live Auth0 evidence, automated-test evidence, and remaining risks.

Phase 04 exit gate: open. Current API run: 24 passed, 7 skipped because `OPSDESK_TEST_DATABASE_URL` was unset; PostgreSQL authorization/deletion cases therefore remain unverified in this run. User-confirmed Auth0 manual evidence covers sign-in/dashboard, sign-out, owner workspace API success, and denial for a second unprovisioned user. Expiry/revocation behavior remains open under p4-t01; p4-t05 remains open until the PostgreSQL delete-isolation cases pass. p4-t06 and p4-t07 are complete based on implementation/review and recorded evidence. Do not begin Phase 05 until all p4-t00–p4-t08 criteria and the Phase 04 exit gate are verified.
