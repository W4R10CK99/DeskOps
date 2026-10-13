import { Auth0Provider } from '@auth0/auth0-react';
import type { ReactNode } from 'react';

type IdentityRootProps = { children: ReactNode };

export function IdentityRoot({ children }: IdentityRootProps) {
  const domain = import.meta.env.VITE_AUTH0_DOMAIN;
  const clientId = import.meta.env.VITE_AUTH0_CLIENT_ID;
  const audience = import.meta.env.VITE_AUTH0_AUDIENCE;

  if (!domain || !clientId || !audience) {
    return (
      <main className="identity-screen">
        <section className="identity-card" aria-labelledby="identity-setup-title">
          <div className="brand-mark" aria-hidden="true">
            o
          </div>
          <p className="eyebrow">OpsDesk identity</p>
          <h1 id="identity-setup-title">Identity provider setup required</h1>
          <p>
            Set <code>VITE_AUTH0_DOMAIN</code>, <code>VITE_AUTH0_CLIENT_ID</code>, and{' '}
            <code>VITE_AUTH0_AUDIENCE</code> in the web environment to enable sign-in.
          </p>
          <p className="identity-muted">
            Protected workspace content stays hidden until identity is configured.
          </p>
        </section>
      </main>
    );
  }

  return (
    <Auth0Provider
      domain={domain}
      clientId={clientId}
      authorizationParams={{
        redirect_uri: window.location.origin,
        audience,
      }}
      cacheLocation="memory"
      useRefreshTokens={false}
    >
      {children}
    </Auth0Provider>
  );
}
