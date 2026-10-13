# ADR 0002: Managed OIDC identity and API bearer validation

- Status: accepted for Phase 04 implementation
- Date: 2026-10-12

## Context

OpsDesk needs sign-in and server-enforced workspace authorization. Building password storage, reset flows, MFA, and credential rotation would create unnecessary security ownership for this portfolio product. The React app and FastAPI service are independently deployed and the project/task data adapters remain mock-backed until the integration phase.

## Decision

Use Auth0 as the managed OpenID Connect identity provider. The browser uses the maintained Auth0 React SPA SDK, which performs authorization-code flow with PKCE and keeps tokens in memory. The API accepts only Auth0 access tokens intended for the configured API audience. FastAPI validates JWT signatures against the issuer JWKS and enforces issuer, audience, expiry, and required subject claims. The API never trusts frontend-supplied identity or role claims.

Application identity is the pair `(configured issuer, sub)`, stored on a workspace membership. Email is informational and is not used to authorize or merge accounts. Workspace selection is a request hint only; the API must resolve an active membership for the verified subject and selected workspace before serving data. Workspace and role checks are enforced in repository queries and server-side dependencies. Owners may manage membership; members may use ordinary project/task operations.

## Trust boundaries and responsibilities

- Auth0 authenticates the human and issues signed, audience-bound access tokens.
- The browser SDK handles redirect state, nonce, PKCE, token acquisition, and logout. Tokens are held in memory; no client secret or long-lived refresh token is shipped to the browser.
- FastAPI is the enforcement point. It verifies each presented access token, maps `sub` to application membership, authorizes the selected workspace, and scopes database operations. CORS is not authorization.
- PostgreSQL stores workspace memberships, roles, and business records. Membership provisioning and role changes require a trusted owner/server-side action; request bodies cannot grant membership to their caller.
- Deployment operators provide Auth0 issuer/audience values and allowed frontend origins through environment configuration. No credentials are stored in source control.

## Alternatives considered

- Custom username/password sessions: rejected because it would require OpsDesk to own password storage, resets, MFA, cookie/CSRF controls, and revocation.
- Self-hosted OIDC (for example Keycloak): viable for local development, but adds identity-service operations and does not match the managed-identity preference. It can be reconsidered if a local provider becomes a concrete requirement.
- Browser local-storage token persistence: rejected because long-lived credentials would be exposed to persistent script access after XSS.

## Consequences and limitations

Auth0 tenant/application/API configuration is required for real browser sign-in and live JWKS verification. Automated tests can prove token-validation rules and authorization with isolated test credentials, but they do not prove the external Auth0 tenant configuration. In-memory browser token caching means a page reload may require silent reauthentication or another interactive login; no refresh token is persisted. Server-side token revocation is not instantaneous for already-issued self-contained JWTs; short access-token lifetime and provider logout limit but do not eliminate this window. TLS, deployment secrets, rate limiting, and operational account lifecycle controls remain production-hardening responsibilities.
