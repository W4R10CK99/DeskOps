import { useState } from 'react';
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
            <strong>Workspace One</strong>
            <span>Free workspace</span>
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
            <div className="profile-avatar">MC</div>
            <div>
              <strong>Maya Chen</strong>
              <span>Workspace admin</span>
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
            <div className="top-avatar">MC</div>
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
