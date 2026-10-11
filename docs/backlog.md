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

## Dependencies and sequence

1. Complete the shell/tooling and shared route/components (p1-t00–02).
2. Add mock workflows and screen states (p1-t03–04).
3. Complete responsive/accessibility and quality checks (p1-t05–06).
4. Record the demo, document integration gaps, and pass the Phase 01 exit gate (p1-t07). The user has waived the recording for the current Phase 02 work; keep p1-t07 open until a real recording is made.
5. Complete and verify Phase 02 API tasks (p2-t00–07) before beginning database work. Continue in tracker order through Phase 07 before any AI/RAG/agent work.

## Later phases

Phase 03–12 are retained in the HTML tracker and intentionally not implemented ahead of their dependencies. In particular, Phase 07 deployed-core exit gate blocks AI/RAG/agent work.
