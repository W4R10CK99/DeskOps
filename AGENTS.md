# OpsDesk engineering instructions

## Purpose and ownership
OpsDesk is a portfolio customer-operations workspace for teams managing projects, tasks, and internal documents. Build the core product before AI features. This is one Git monorepo with independently structured and deployable applications: `web/` owns the React UI; `api/` will own the FastAPI HTTP contract and backend; `infra/` owns local/deployment configuration; `docs/` owns product, architecture, progress, decisions, and runbooks.

## Approved stack and boundaries
- Frontend: React, TypeScript, Vite. Keep UI, API client/contracts, and business concerns separated. Mock data belongs behind a replaceable feature/data boundary.
- Backend (when its tracker phase begins): Python, FastAPI, Pydantic, SQLAlchemy, Alembic, PostgreSQL, pytest.
- Local services: Docker Compose under `infra/`; add storage, workers, or identity only when required by the current phase.
- GitHub Actions validates frontend and backend independently and integration workflows across them when ready.
- Do not couple frontend to backend implementation modules. Do not add microservices, Kubernetes, Redis, custom auth, or AI/RAG/agents before their tracker gates.

## Required continuity reading
At the start of a resumed session, read this file, `docs/progress.md`, `docs/backlog.md`, `docs/architecture.md`, relevant ADRs, the applicable sections of `FDE_End_to_End_Build_Tracker_Ram.html`, and inspect the actual repository state. The tracker is authoritative for task order, IDs, outcomes, and exit gates. Surface missing evidence or conflicts; do not silently change scope.

## Commands
- Frontend install: `cd web; npm ci`
- Frontend dev: `cd web; npm run dev`
- Frontend lint: `cd web; npm run lint`
- Frontend formatting check: `cd web; npm run format:check`
- Frontend type check: `cd web; npm run typecheck`
- Frontend build: `cd web; npm run build`
- Frontend automated tests are not configured in Phase 01; add and document the real test command when a tracker task calls for a test runner. Do not report tests as run when none exist.
- Backend commands will be documented in `api/pyproject.toml` and here when Phase 02 begins. Do not create backend functionality early.

## Engineering expectations
- Keep code typed, focused, readable, and explicit about failure states. Validate user input at boundaries and use consistent API error shapes when API work begins.
- Add abstractions only for a concrete need. Keep mock data in `web/src/features/*/data` until API integration begins.
- Provide labeled controls, keyboard access, responsive layouts, meaningful loading/empty/error/success states, and stable IDs.
- Add tests when specified by the current tracker task; never claim checks that were not run. Distinguish unit, integration, manual, and unverified behavior.
- Security: treat user input, files, external responses, and future model outputs as untrusted. Enforce authorization server-side for every protected operation. Never commit credentials, tokens, private data, or production secrets. Keep `.env` files ignored and maintain safe `.env.example` placeholders.
- Database changes must use versioned Alembic migrations once the database phase starts. Keep test data synthetic and isolated; never point tests at production.
- Do not overwrite existing work or rewrite Git history destructively. Check `git status` before changes; preserve user edits. Do not commit unless asked.

## Phase order and release gates
Follow the tracker sequentially: 00 product/setup; 01 frontend mock shell; 02 API; 03 database; 04 auth/tenant isolation; 05 storage/async work; 06 integration; 07 core deployment/testing/observability/security; then AI/RAG/agent and later phases. Do not start AI/RAG/agent implementation until the deployed core product passes Phase 07. Do not mark tracker tasks complete merely because code exists: verify the task acceptance criteria and demo the result where the tracker requires it.

## Definition of done and final report
A milestone is done only when its observable acceptance criteria are verified, relevant commands pass, docs reflect reality, and known gaps are recorded. At each meaningful session end, report changes and reasons, files, commands and actual outcomes, limitations/blockers, tracker task IDs completed with evidence, and the exact next task. Do not claim Phase 01 demo recording without an actual recording artifact.

## Harness instructions
This repository uses `AGENTS.md` as its canonical shared instruction file. Codex reads it as project guidance when the repository is open; this session loaded it explicitly from the kickoff brief and will use it as the source of truth. Other harnesses may not discover it automatically. `CLAUDE.md` directs Claude Code to read it. For any harness without automatic discovery, load this file explicitly at session start. Keep essential shared rules here rather than duplicating them.
