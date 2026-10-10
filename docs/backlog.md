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
- [ ] p1-t07 Record a short frontend demo and list gaps before backend integration — integration gaps are documented in progress; a video recording is still pending.

## Dependencies and sequence

1. Complete the shell/tooling and shared route/components (p1-t00–02).
2. Add mock workflows and screen states (p1-t03–04).
3. Complete responsive/accessibility and quality checks (p1-t05–06).
4. Record the demo, document integration gaps, and pass the Phase 01 exit gate (p1-t07).
5. Only then begin Phase 02 backend API work. Continue in tracker order through Phase 07 before any AI/RAG/agent work.

## Later phases

Phase 02–12 are retained in the HTML tracker and intentionally not expanded or implemented ahead of their dependencies. In particular, Phase 07 deployed-core exit gate blocks AI/RAG/agent work.
