# Project progress

Last updated: 2026-10-12

## Current phase

Phase 03 — PostgreSQL and data modelling is complete. All p3-t00–p3-t07 acceptance criteria have evidence recorded below and in `docs/backlog.md`. The user confirmed restarting the PostgreSQL container and verifying its database contents remained persistent. Phase 04 is next but has not been started. Phase 01 task `p1-t07` (short frontend demo recording) remains open; it was waived to proceed with backend work and has not been marked complete.

## Verified completions

- Phase 00 product definition and setup artifacts are present; tasks p0-t00 through p0-t07 are checked in `docs/backlog.md`.
- Phase 01 frontend shell and quality checks are complete except for the real demo recording. The browser remains on feature-local sample data; no frontend files were changed in Phases 02–03.
- Phase 02 tasks p2-t00 through p2-t07 are complete, with 11 API contract tests and prior live HTTP verification documented in the backlog/history.
- Phase 03 p3-t01 and p3-t02: SQLAlchemy models and the initial Alembic migration describe Workspace, Membership, Project, Task, Document metadata, and AuditEvent, including key relationships, ownership references, checks, unique constraints, foreign keys, and indexes. Offline Alembic SQL generation succeeded; the user reports development revision `20261011_0001 (head)`.
- Phase 03 persistence code uses a pooled SQLAlchemy engine, checks PostgreSQL connectivity during app startup, and selects the PostgreSQL repository by default. The in-memory repository is only injected explicitly by the API contract tests; application startup never silently falls back to it.
- Project/task repositories perform filtered, sorted, paginated SQL queries, map ORM rows to the existing service records, and write mutation audit events in the same transaction. The API request/response schemas and routes remain unchanged.
- User-reported manual Swagger verification against the PostgreSQL-backed API: listed projects; created and updated projects; listed a project's tasks; created tasks; and listed the task list again. The user also reports that project/task records remained after restarting the API. These are manual API checks, not pytest cases.
- User-reported fresh-database proof: migrated disposable `opsdesk_migration_check` with `alembic upgrade head` and confirmed the expected tables were created.
- Added an idempotent seed command for three synthetic projects and 60 tasks, plus opt-in PostgreSQL integration tests for process restart durability, pagination, FK enforcement, and transaction rollback.
- Fixed the seed task-ID collision: the previous generator used only the first eight characters of each project UUID (which are shared across all three demo projects), producing 60 requested tasks with only 20 unique primary keys. With `autoflush=False`, `session.get()` could not see the first project's pending task rows before the second project's duplicate IDs were staged. The commit-time `UniqueViolation` rolled back the whole transaction, explaining why the database still had zero rows. Seed and API settings use the same `OPSDESK_DATABASE_URL`; the verified target was `localhost:5432/opsdesk`, so a wrong database URL was not the cause.
- Task IDs now use deterministic project-scoped UUIDv5 values. Seed upserts explicitly flush each project's writes inside one transaction; project descriptions are also refreshed. Added a unit regression for 60 unique stable IDs and PostgreSQL integration cases for repeated runs, unrelated-row preservation, and rollback after an injected mid-seed failure.
- Live development PostgreSQL verification: the documented seed command succeeded twice; subsequent read-only counts were exactly 3 projects and 60 tasks (20 per project). A failure injected during the final task flush left the prior seeded dataset unchanged. The PostgreSQL-backed API returned the second page of 10 tasks with `total=20`.
- Phase 03 p3-t00–p3-t07 are complete. The user reports the fresh migration, API restart persistence, passing integration suite, seed/pagination verification, query plan, and PostgreSQL container restart with database content retained. Compose defines the named volume and health check; API startup checks database connectivity.
- User-reported PostgreSQL integration test result: 20 passed, 0 skipped. This result was supplied by the user and was not rerun in this session.
- User confirmation closing p3-t00: the PostgreSQL container was restarted, the database was checked, and its content was verified persistent. The specific health-check status string was not supplied; PostgreSQL was accessible with its data after restart, and the Compose health check is configured.
- User-reported `EXPLAIN` result: project index scan using `ix_projects_workspace_customer` with workspace condition and project-ID filter; nested-loop join; sequential scan of `tasks` filtered by `project_id`; sort by `t.due, t.id`; estimated 20 rows and total cost approximately 11.59. The task scan is reasonable for this small dataset. These are estimates, not actual execution timings; no index was added to force index use. Recorded in `api/README.md`.
- Alembic's configuration omitted `path_separator` while specifying `prepend_sys_path`. Added `path_separator = os` to use the explicit platform path separator and avoid legacy path parsing. Afterward, Alembic history and offline migration SQL generation completed without the path-separator warning.
- Checks rerun in this Codex environment after the config change: pytest 14 passed/6 skipped (`OPSDESK_TEST_DATABASE_URL` unset), Ruff lint passed, Ruff format check passed, Alembic history passed, and offline `upgrade --sql head` generated the expected six-table DDL. The user separately reports 20 PostgreSQL tests passed with zero skipped; that result was not independently rerun here.

## Database model and boundaries

- Projects belong to the single configured local workspace; project and task rows may reference a workspace membership as owner. Membership email/role are structural identity references only; there are no login, authorization, or tenant-selection endpoints.
- Tasks reference projects with deletion restricted. Document metadata references a workspace and optionally a project; deleting a project would retain its metadata with the project reference detached. The API has no document CRUD or file-byte storage.
- The project/task API contract remains stable. The frontend still reads `web/src/features/projects/data.ts` and local feature state; a later integration phase will put a typed HTTP client behind the existing data boundary.
- Index rationale: `(workspace_id, name/customer)` supports the project list’s common workspace sort paths; `(project_id, due)` supports per-project due-date listing and project FK lookups; `(status, due)` supports filtered due-date listing; document indexes support workspace/project lookup; `(workspace_id, created_at)` supports ordered audit inspection. Live planner choice still needs measurement.

## Blockers and unverified work

- No Phase 03 acceptance items remain open. The user-reported integration suite result is 20 passed/0 skipped; it was not independently rerun in this session. The separate Codex-environment run after the Alembic config change had 14 passed/6 skipped because `OPSDESK_TEST_DATABASE_URL` was unset.
- Phase 01 p1-t07 remains open: no demo video artifact has been produced.

## Exact next task

Begin Phase 04 with p4-t00: choose and document a maintained OIDC/auth provider or a well-understood backend-session approach. The tracker prefers managed identity over implementing password, reset, and MFA logic from scratch. Phase 04 implementation has not started in this session.
