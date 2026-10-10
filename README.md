# OpsDesk

OpsDesk is a customer-operations workspace portfolio project for managing projects, tasks, and internal documents. The roadmap and acceptance gates are defined in [FDE_End_to_End_Build_Tracker_Ram.html](./FDE_End_to_End_Build_Tracker_Ram.html).

## Current state

Phase 00 product/setup is complete. The Phase 01 frontend shell is implemented and its build and main workflows are verified; the tracker-required demo recording is still pending. The frontend currently uses local mock data; no backend, database, authentication, file storage, or deployment is implemented.

## Repository layout

- `web/` — independently buildable React + TypeScript + Vite frontend.
- `api/` — reserved for the FastAPI application when Phase 02 begins.
- `infra/` — reserved for local infrastructure and deployment configuration.
- `docs/` — product definition, architecture, ordered backlog, progress, decisions, and future runbooks.

The frontend communicates with the backend only through an HTTP API contract, to be defined before Phase 02 implementation. The two apps will remain independently testable and deployable.

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
