# OpsDesk

OpsDesk is a customer-operations workspace portfolio project for managing projects, tasks, and internal documents. The roadmap and acceptance gates are defined in [FDE_End_to_End_Build_Tracker_Ram.html](./FDE_End_to_End_Build_Tracker_Ram.html).

## Current state

Phase 00 product/setup and the Phase 01 frontend shell are complete. The tracker-required Phase 01 demo recording remains open but was waived for proceeding by the user. Phase 02 now provides a separately runnable FastAPI API foundation; its project/task data is process-local and resets on restart. The frontend still uses local mock data. PostgreSQL, authentication, file storage, and deployment are not implemented.

## Repository layout

- `web/` — independently buildable React + TypeScript + Vite frontend.
- `api/` — FastAPI application, versioned project/task endpoints, schemas, services, in-memory repository, and tests.
- `infra/` — reserved for local infrastructure and deployment configuration.
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
