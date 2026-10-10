# OpsDesk product brief

## Problem

Small customer-operations teams coordinate projects, follow-up work, and internal reference documents across separate tools and informal messages. Team members lose time finding current status, ownership, and the document relevant to a task. OpsDesk will provide one focused workspace for that coordination. The first increment is a navigable frontend shell with realistic sample data; it does not claim to solve persistence or collaboration yet.

## Primary user and workflows

Primary user: an operations coordinator in a small customer-facing team who needs a quick view of active work and its supporting documents.

1. Create and track a project, then inspect its tasks and progress.
2. Add or update a task, owner, due date, and status within a project.
3. Find and organize internal documents associated with the team's work.

## V1 scope

- Workspace dashboard, project list, project detail/task view, documents, and settings screens.
- Frontend-only prototype using clearly isolated, realistic mock data.
- Responsive navigation, reusable controls, form validation, and visible empty, loading, error, and success states.
- Later core scope: sign-in, workspace memberships, server-enforced permissions, persistent projects/tasks, private documents, and independently deployed frontend/backend.

## Acceptance criteria

### Project workflow
- The user can navigate to a project list and open a project detail route.
- Project list has a useful empty state; selecting a project with no tasks shows a task empty state.
- Invalid required fields are identified beside labeled controls; valid create/edit submissions produce a visible success state and update mock UI state.
- A simulated load failure offers an actionable retry; the prototype clearly identifies data as local/demo data.

### Task workflow
- Project detail displays tasks with status, owner, and due date.
- The user can create a task with a title and project, and edit its title/status/owner/due date.
- Required-field validation prevents invalid submission; empty, loading, error, and success feedback are visible.

### Document workflow
- The user can browse/search/filter the sample document list and sees a useful empty result state.
- The shell communicates that upload/download are not connected yet; it must not imply files are actually stored.

### Cross-screen and accessibility
- Dashboard, Projects, Project Detail, Documents, and Settings are directly addressable routes with shared navigation.
- Core navigation and dialogs work by keyboard, controls have labels, focus is visible, and layouts remain usable on narrow screens.

## Non-goals for the initial product

- AI copilot, RAG, autonomous agents, or model integration.
- Microservices, Kubernetes, Redis, custom authentication infrastructure, or premature abstraction.
- Production persistence, real identity, uploads, notifications, external integrations, or deployment in the frontend shell phase.

## Risks and assumptions

- The initial workflow assumptions need validation with plausible users before claiming customer impact.
- Mock interactions demonstrate UX only; they do not establish multi-user consistency, authorization, or durability.
- File visibility and workspace isolation must be enforced by the backend in later phases, never by client-side filtering alone.
