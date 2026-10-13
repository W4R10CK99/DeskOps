# OpsDesk web

The React + TypeScript + Vite app remains independently runnable. It uses Auth0 for sign-in when configured and verifies the access token with the API before displaying the workspace UI.

## Local sign-in setup

1. Create an Auth0 tenant, a Single Page Application, and an API. Use the API identifier as the audience.
2. Add `http://localhost:5173` to the SPA's Allowed Callback URLs, Allowed Logout URLs, and Allowed Web Origins.
3. Copy `.env.example` to `.env.local` and fill in the tenant domain, SPA client ID, and API audience. Set the API base URL if it is not `http://localhost:8000/api/v1`.
4. Configure the API's matching issuer, audience, database URL, and CORS origin; migrate the database and provision an initial owner as described in [the API README](../api/README.md).
5. Run `npm ci` and `npm run dev`.

The Auth0 SDK uses authorization code with PKCE and in-memory token caching. No client secret or persistent refresh token is included in the browser bundle. On sign-in, the browser calls `GET /api/v1/workspaces` with the API access token. A missing/invalid token or absent membership blocks the app shell; retry and sign-out actions remain available.

When Auth0 variables are absent, the app shows setup instructions and keeps the workspace shell hidden. Real provider redirects and logout require a configured tenant and have not been verified in this repository environment.

## Data boundary

Project and task screens still use the feature-local demo adapter in `src/features/projects/data.ts`. The backend identity check is the narrow Phase 04 flow; it does not replace project/task mock operations with a full API client. That adapter-to-client transition is reserved for the tracker integration phase. Documents remain demo metadata in the UI; the API currently exposes only workspace-scoped database metadata, not file storage or download.
