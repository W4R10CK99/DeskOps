import { useEffect, useState } from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import { NavLink, Navigate, Route, Routes, useLocation } from 'react-router-dom';
import { DocumentsPage } from './features/documents/pages';
import {
  DashboardPage,
  ProjectDetailPage,
  ProjectsPage,
  SettingsPage,
} from './features/projects/pages';
import { initialProjects, type Project, type Task } from './features/projects/data';
import { ErrorState, Loading } from './components/ui';

const navigation = [
  { to: '/', label: 'Overview', icon: '▦', end: true },
  { to: '/projects', label: 'Projects', icon: '◫' },
  { to: '/documents', label: 'Documents', icon: '▤' },
];

export default function App() {
  const {
    isLoading,
    isAuthenticated,
    error,
    loginWithRedirect,
    logout,
    user,
    getAccessTokenSilently,
  } = useAuth0();
  const [backendState, setBackendState] = useState<'checking' | 'ready' | 'no-workspace' | 'error'>(
    'checking',
  );
  const [backendRetry, setBackendRetry] = useState(0);
  const [workspaceName, setWorkspaceName] = useState('Workspace');

  useEffect(() => {
    if (!isAuthenticated) {
      setBackendState('checking');
      return;
    }
    let current = true;
    setBackendState('checking');
    void (async () => {
      try {
        const token = await getAccessTokenSilently();
        const apiBase = (
          import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1'
        ).replace(/\/$/, '');
        const response = await fetch(`${apiBase}/workspaces`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!response.ok) throw new Error('Backend identity verification failed');
        const workspaces: unknown = await response.json();
        if (!Array.isArray(workspaces)) throw new Error('Invalid workspace response');
        if (current) {
          const firstWorkspace = workspaces[0] as { name?: unknown } | undefined;
          setWorkspaceName(
            typeof firstWorkspace?.name === 'string' ? firstWorkspace.name : 'Workspace',
          );
          setBackendState(workspaces.length > 0 ? 'ready' : 'no-workspace');
        }
      } catch {
        if (current) setBackendState('error');
      }
    })();
    return () => {
      current = false;
    };
  }, [isAuthenticated, getAccessTokenSilently, backendRetry]);

  if (isLoading) {
    return (
      <main className="identity-screen" aria-live="polite">
        <div className="identity-card">
          <Loading label="Verifying your identity…" />
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="identity-screen">
        <section className="identity-card" role="alert">
          <h1>Sign-in could not be completed</h1>
          <p>Check your connection or identity provider settings, then try again.</p>
          <button className="primary-button" onClick={() => void loginWithRedirect()}>
            Try signing in again
          </button>
        </section>
      </main>
    );
  }

  if (!isAuthenticated) {
    return (
      <main className="identity-screen">
        <section className="identity-card" aria-labelledby="sign-in-title">
          <div className="brand-mark" aria-hidden="true">
            o
          </div>
          <p className="eyebrow">OpsDesk workspace</p>
          <h1 id="sign-in-title">Sign in to continue</h1>
          <p>Use your organization’s secure identity provider to access OpsDesk.</p>
          <button className="primary-button" onClick={() => void loginWithRedirect()}>
            Continue to sign in
          </button>
        </section>
      </main>
    );
  }

  if (backendState !== 'ready') {
    const message =
      backendState === 'checking'
        ? 'Confirming your identity and workspace access…'
        : backendState === 'no-workspace'
          ? 'Your identity is verified, but no OpsDesk workspace has been assigned to this account.'
          : 'OpsDesk could not verify your access with the API. Check your connection and try again.';
    return (
      <main className="identity-screen" aria-live="polite">
        <section className="identity-card" aria-labelledby="workspace-access-title">
          <h1 id="workspace-access-title">
            {backendState === 'no-workspace'
              ? 'Workspace access required'
              : 'Checking workspace access'}
          </h1>
          <p>{message}</p>
          {backendState === 'error' && (
            <div className="identity-actions">
              <button
                className="primary-button"
                onClick={() => setBackendRetry((attempt) => attempt + 1)}
              >
                Retry verification
              </button>
              <button className="state-preview" onClick={() => void loginWithRedirect()}>
                Sign in again
              </button>
            </div>
          )}
          {backendState === 'no-workspace' && (
            <button
              className="primary-button"
              onClick={() => setBackendRetry((attempt) => attempt + 1)}
            >
              Check workspace access again
            </button>
          )}
          {backendState !== 'checking' && (
            <button
              className="state-preview"
              onClick={() => logout({ logoutParams: { returnTo: window.location.origin } })}
            >
              Sign out
            </button>
          )}
        </section>
      </main>
    );
  }

  return (
    <WorkspaceApp
      userLabel={user?.name || user?.email || 'Signed-in user'}
      workspaceName={workspaceName}
      onSignOut={() => logout({ logoutParams: { returnTo: window.location.origin } })}
    />
  );
}

function WorkspaceApp({
  userLabel,
  workspaceName,
  onSignOut,
}: {
  userLabel: string;
  workspaceName: string;
  onSignOut: () => void;
}) {
  const [projects, setProjects] = useState(initialProjects);
  const [notice, setNotice] = useState('');
  const [loadState, setLoadState] = useState<'ready' | 'loading' | 'error'>('ready');
  const location = useLocation();

  function previewLoading() {
    setLoadState('loading');
    window.setTimeout(
      () => setLoadState((current) => (current === 'loading' ? 'ready' : current)),
      650,
    );
  }

  function addProject(project: Project) {
    setProjects((current) => [project, ...current]);
    setNotice('Project created successfully.');
  }
  function addTask(projectId: string, task: Task) {
    setProjects((current) =>
      current.map((project) =>
        project.id === projectId ? { ...project, tasks: [task, ...project.tasks] } : project,
      ),
    );
    setNotice('Task added to project.');
  }
  function updateProject(updated: Project) {
    setProjects((current) =>
      current.map((project) => (project.id === updated.id ? updated : project)),
    );
    setNotice('Project changes saved.');
  }
  function updateTask(projectId: string, task: Task) {
    setProjects((current) =>
      current.map((project) =>
        project.id === projectId
          ? { ...project, tasks: project.tasks.map((item) => (item.id === task.id ? task : item)) }
          : project,
      ),
    );
    setNotice('Task changes saved.');
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <NavLink to="/" className="brand">
          <span className="brand-mark">o</span>
          <span>
            opsdesk<span className="brand-dot">.</span>
          </span>
        </NavLink>
        <div className="workspace-switch">
          <div className="workspace-avatar">W</div>
          <div>
            <strong>{workspaceName}</strong>
            <span>Authorized workspace</span>
          </div>
          <span className="chevron">⌄</span>
        </div>
        <div className="nav-label">WORKSPACE</div>
        <nav className="main-nav" aria-label="Main navigation">
          {navigation.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
            >
              <span className="nav-icon" aria-hidden="true">
                {item.icon}
              </span>
              {item.label}
              {item.label === 'Projects' && <span className="nav-count">{projects.length}</span>}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-section">
          <div className="nav-label">YOUR PROJECTS</div>
          {projects.slice(0, 4).map((project) => (
            <NavLink
              key={project.id}
              className={({ isActive }) => `project-nav${isActive ? ' active' : ''}`}
              to={`/projects/${project.id}`}
            >
              <span className={`project-dot ${project.color}`} />
              {project.name}
            </NavLink>
          ))}
          <NavLink to="/projects" className="add-project-link">
            <span>＋</span> Add a project
          </NavLink>
        </div>
        <div className="sidebar-bottom">
          <NavLink
            className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
            to="/settings"
          >
            <span className="nav-icon" aria-hidden="true">
              ⚙
            </span>
            Settings
          </NavLink>
          <div className="profile">
            <div className="profile-avatar" aria-hidden="true">
              {userLabel.slice(0, 1).toUpperCase()}
            </div>
            <div>
              <strong>{userLabel}</strong>
              <span>Signed in</span>
            </div>
            <span className="more">···</span>
          </div>
        </div>
      </aside>
      <main className="main-area">
        <header className="topbar">
          <div className="breadcrumbs">
            <span>Workspace</span>
            <span className="crumb-sep">/</span>
            <strong>
              {location.pathname.includes('documents')
                ? 'Documents'
                : location.pathname.includes('settings')
                  ? 'Settings'
                  : location.pathname.includes('projects/')
                    ? 'Project detail'
                    : location.pathname.includes('projects')
                      ? 'Projects'
                      : 'Overview'}
            </strong>
          </div>
          <div className="top-actions">
            <span className="demo-pill">
              <span /> Demo data
            </span>
            <button className="state-preview" onClick={previewLoading}>
              Preview loading
            </button>
            <button className="state-preview" onClick={() => setLoadState('error')}>
              Preview error
            </button>
            <button className="icon-button" aria-label="Help">
              ?
            </button>
            <div className="top-avatar" aria-hidden="true">
              {userLabel.slice(0, 1).toUpperCase()}
            </div>
            <button className="state-preview" onClick={onSignOut}>
              Sign out
            </button>
          </div>
        </header>
        {notice && (
          <div className="toast" role="status">
            <span>✓</span>
            {notice}
            <button aria-label="Dismiss notification" onClick={() => setNotice('')}>
              ×
            </button>
          </div>
        )}
        <div className="page-content">
          {loadState === 'loading' ? (
            <Loading label="Loading workspace data…" />
          ) : loadState === 'error' ? (
            <ErrorState onRetry={() => setLoadState('ready')} />
          ) : (
            <Routes>
              <Route path="/" element={<DashboardPage projects={projects} />} />
              <Route
                path="/projects"
                element={<ProjectsPage projects={projects} onCreate={addProject} />}
              />
              <Route
                path="/projects/:projectId"
                element={
                  <ProjectDetailPage
                    projects={projects}
                    onAddTask={addTask}
                    onUpdateTask={updateTask}
                    onUpdateProject={updateProject}
                  />
                }
              />
              <Route path="/documents" element={<DocumentsPage />} />
              <Route
                path="/settings"
                element={<SettingsPage onSave={() => setNotice('Workspace preferences saved.')} />}
              />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          )}
        </div>
      </main>
    </div>
  );
}
