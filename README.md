# OpsDesk

OpsDesk is a customer-operations workspace portfolio project for managing projects, tasks, and internal documents. The roadmap and acceptance gates are defined in [FDE_End_to_End_Build_Tracker_Ram.html](./FDE_End_to_End_Build_Tracker_Ram.html).

## Current state

Phase 03 PostgreSQL persistence and its exit gate are complete based on recorded user and test evidence. Phase 04 identity/access work is underway: Auth0 OIDC browser flow, backend JWT validation, membership-based workspace scoping, and identity migrations are implemented. The backend suite, including cross-workspace PostgreSQL authorization tests, passed against an isolated test database; live Auth0 browser configuration remains unverified. The frontend project/task workflows still use local mock data; full API integration remains a later phase. The Phase 01 demo recording remains open.

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

See [api/README.md](api/README.md) for Python environment setup, Auth0 configuration, API docs, endpoint details, and tests. See [web/README.md](web/README.md) for the browser sign-in setup and frontend mock-data boundary.
