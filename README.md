# OpsDesk

OpsDesk is a customer-operations workspace portfolio project for managing projects, tasks, and internal documents. The roadmap and acceptance gates are defined in [FDE_End_to_End_Build_Tracker_Ram.html](./FDE_End_to_End_Build_Tracker_Ram.html).

## Current state

Phase 00 product/setup and the Phase 02 FastAPI API foundation are complete. The Phase 01 frontend shell remains unchanged and uses local mock data; its tracker-required demo recording remains open but was waived for proceeding. Phase 03 is in progress: PostgreSQL models, migrations, repository, local Compose setup, and database integration tests are authored, but live database gates remain unverified because Docker/PostgreSQL are unavailable in the current environment. Authentication, authorization, file storage, frontend/API integration, and deployment are later phases.

## Repository layout

- `web/` — independently buildable React + TypeScript + Vite frontend.
- `api/` — FastAPI application, versioned project/task endpoints, schemas, services, PostgreSQL and test repositories, Alembic migrations, and tests.
- `infra/` — local PostgreSQL Compose configuration and infrastructure documentation.
- `docs/` — product definition, architecture, ordered backlog, progress, decisions, and future runbooks.

The frontend and backend remain independently testable and deployable. The frontend will move from its feature-local mock data to a typed HTTP client in the later integration phase.

## Frontend development

Requires Node.js 20.19+ or 22.12+; Node.js 24 is used for this workspace.

```powershell
cd web
npm ci
npm run dev
npm run lint
npm run format:check
npm run typecheck
npm run build
```

## Product and engineering docs

See [the product brief](docs/product-brief.md), [architecture](docs/architecture.md), [backlog](docs/backlog.md), [progress](docs/progress.md), and [ADRs](docs/decisions/).

## Backend development

See [api/README.md](api/README.md) for Python environment setup, API docs, endpoint details, and tests.
