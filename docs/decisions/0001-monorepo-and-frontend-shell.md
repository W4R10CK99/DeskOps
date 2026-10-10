# ADR 0001: One monorepo with an independently built frontend

- Status: Accepted for initial setup
- Date: 2026-10-10

## Context

The project tracker calls for a React + TypeScript frontend shell, then a separately owned FastAPI backend and later database, identity, and storage. There was no prior application or repository in the workspace.

## Decision

Use one Git repository with `web/`, `api/`, `infra/`, and `docs/` ownership boundaries. Build the first UI as a Vite SPA using mock data behind feature-local boundaries. Add no backend or infrastructure implementation in Phase 01.

## Consequences

The single history makes the portfolio lifecycle easy to review, while separate package/build boundaries preserve independent frontend/backend deployment. Mock data keeps UX work unblocked but provides no persistence, identity, or authorization evidence. Before Phase 02, define a versioned HTTP contract and keep backend logic out of the browser.

## Alternatives considered

- Separate repositories: unnecessary operational overhead before independent ownership is demonstrated.
- Full-stack framework: not needed for this client-only milestone and would obscure the intended frontend/API boundary.
