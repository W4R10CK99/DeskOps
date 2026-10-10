import { useState, type FormEvent } from 'react';
import { Link, useParams } from 'react-router-dom';
import {
  Button,
  EmptyState,
  Form,
  Input,
  Modal,
  SearchInput,
  StatusBadge,
} from '../../components/ui';
import { teamMembers, type Project, type Task, type TaskStatus } from './data';

const formatDate = new Intl.DateTimeFormat('en', { month: 'short', day: 'numeric' });

function Heading({
  eyebrow,
  title,
  description,
  action,
}: {
  eyebrow: string;
  title: string;
  description: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="page-heading">
      <div>
        <div className="eyebrow">{eyebrow}</div>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      {action}
    </div>
  );
}

export function DashboardPage({ projects }: { projects: Project[] }) {
  const allTasks = projects.flatMap((project) =>
    project.tasks.map((task) => ({ ...task, project })),
  );
  const activeTasks = allTasks.filter((task) => task.status !== 'Done');
  const completed = allTasks.filter((task) => task.status === 'Done').length;
  const upcoming = activeTasks.slice(0, 4);
  return (
    <>
      <Heading
        eyebrow="Saturday, October 10, 2026"
        title="Good morning, Maya ✨"
        description="Here’s what’s happening across your workspace today."
        action={
          <Button variant="secondary" onClick={() => window.print()}>
            ↗ Export overview
          </Button>
        }
      />
      <div className="welcome-banner">
        <div>
          <div className="banner-tag">YOUR WORKSPACE AT A GLANCE</div>
          <h2>
            Make space for the work
            <br />
            that <em>moves things forward.</em>
          </h2>
          <p>Keep projects, tasks, and the details that connect them in one calm place.</p>
          <Link to="/projects" className="banner-link">
            Explore your projects <span>→</span>
          </Link>
        </div>
        <div className="banner-art" aria-hidden="true">
          <div className="art-orbit orbit-one" />
          <div className="art-orbit orbit-two" />
          <div className="art-card card-back">
            PROJECT
            <br />
            <b>NORTHSTAR</b>
            <span>03 tasks</span>
          </div>
          <div className="art-card card-front">
            <span className="art-check">✓</span>
            <div>
              <b>Launch checklist</b>
              <small>Updated just now</small>
            </div>
            <span className="art-spark">✳</span>
          </div>
          <div className="art-sparkle">✳</div>
        </div>
      </div>
      <div className="stats-grid">
        <article className="stat-card">
          <div className="stat-icon purple">◫</div>
          <div className="stat-value">{projects.length}</div>
          <div className="stat-label">
            Active projects <span>↗</span>
          </div>
          <div className="stat-foot">Across your workspace</div>
        </article>
        <article className="stat-card">
          <div className="stat-icon orange">◷</div>
          <div className="stat-value">{activeTasks.length}</div>
          <div className="stat-label">
            Open tasks <span>↗</span>
          </div>
          <div className="stat-foot">Needs a little attention</div>
        </article>
        <article className="stat-card">
          <div className="stat-icon green">✓</div>
          <div className="stat-value">{completed}</div>
          <div className="stat-label">
            Tasks completed <span>↗</span>
          </div>
          <div className="stat-foot">A good week of progress</div>
        </article>
        <article className="stat-card">
          <div className="stat-icon blue">↗</div>
          <div className="stat-value">
            {projects.filter((project) => project.tasks.length > 0).length}
          </div>
          <div className="stat-label">
            Projects moving <span>↗</span>
          </div>
          <div className="stat-foot">With work in progress</div>
        </article>
      </div>
      <section className="panel task-panel">
        <div className="panel-heading">
          <div>
            <div className="eyebrow">STAY IN THE LOOP</div>
            <h2>
              Upcoming tasks <span className="count-chip">{activeTasks.length}</span>
            </h2>
          </div>
          <Link className="text-link" to="/projects">
            View all tasks <span>→</span>
          </Link>
        </div>
        {upcoming.length ? (
          <div className="task-list">
            {upcoming.map((task) => (
              <div className="task-row" key={task.id}>
                <div className={`task-check ${task.status === 'Review' ? 'review' : ''}`}>
                  {task.status === 'Review' ? '◉' : ''}
                </div>
                <div className="task-main">
                  <strong>{task.title}</strong>
                  <span>
                    <Link to={`/projects/${task.project.id}`}>{task.project.name}</Link>{' '}
                    <span className="row-dot">·</span> {task.owner}
                  </span>
                </div>
                <div className="task-due">
                  <span>Due</span>
                  {task.due}
                </div>
                <StatusBadge status={task.status} />
              </div>
            ))}
          </div>
        ) : (
          <EmptyState
            title="You’re all caught up"
            action={
              <Link className="button button-secondary" to="/projects">
                Browse projects
              </Link>
            }
          >
            New tasks will show up here when they need your attention.
          </EmptyState>
        )}
      </section>
      <div className="dashboard-bottom">
        <section className="panel project-panel">
          <div className="panel-heading">
            <div>
              <div className="eyebrow">KEEP THE MOMENTUM</div>
              <h2>Recent projects</h2>
            </div>
            <Link className="text-link" to="/projects">
              All projects <span>→</span>
            </Link>
          </div>
          <div className="recent-projects">
            {projects.slice(0, 3).map((project) => (
              <Link className="recent-project" key={project.id} to={`/projects/${project.id}`}>
                <span className={`project-avatar ${project.color}`}>{project.name.charAt(0)}</span>
                <span>
                  <strong>{project.name}</strong>
                  <small>{project.customer}</small>
                </span>
                <span className="recent-arrow">↗</span>
              </Link>
            ))}
          </div>
        </section>
        <section className="panel tip-panel">
          <div className="tip-icon">✳</div>
          <div className="eyebrow">A SMALL REMINDER</div>
          <h2>Good work is a team sport.</h2>
          <p>Clear owners and next steps help everyone move with confidence.</p>
          <Link to="/projects" className="text-link">
            Check your projects <span>→</span>
          </Link>
        </section>
      </div>
      <div className="prototype-note">
        This is a frontend prototype. Changes use in-memory sample data and reset when the page
        reloads.
      </div>
    </>
  );
}

export function ProjectsPage({
  projects,
  onCreate,
}: {
  projects: Project[];
  onCreate: (project: Project) => void;
}) {
  const [query, setQuery] = useState('');
  const [open, setOpen] = useState(false);
  const filtered = projects.filter((project) =>
    `${project.name} ${project.customer}`.toLowerCase().includes(query.toLowerCase()),
  );

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const name = String(form.get('name') ?? '').trim();
    const customer = String(form.get('customer') ?? '').trim();
    if (!name || !customer) return;
    onCreate({
      id: crypto.randomUUID(),
      name,
      customer,
      description: String(form.get('description') ?? ''),
      color: ['violet', 'blue', 'green'][projects.length % 3]!,
      tasks: [],
    });
    setOpen(false);
  }

  return (
    <>
      <Heading
        eyebrow="YOUR WORKSPACE"
        title="Projects"
        description="A little context goes a long way. Keep every customer engagement moving."
        action={<Button onClick={() => setOpen(true)}>＋ New project</Button>}
      />
      <div className="toolbar">
        <SearchInput value={query} onChange={setQuery} placeholder="Search projects…" />
        <span className="toolbar-caption">
          {filtered.length} {filtered.length === 1 ? 'project' : 'projects'}
        </span>
      </div>
      {filtered.length ? (
        <div className="project-grid">
          {filtered.map((project, index) => (
            <ProjectCard key={project.id} project={project} index={index} />
          ))}
        </div>
      ) : (
        <section className="panel">
          <EmptyState
            title={query ? 'No projects found' : 'A clean slate'}
            action={
              !query ? (
                <Button onClick={() => setOpen(true)}>Create your first project</Button>
              ) : undefined
            }
          >
            {query
              ? 'Try another search term, or clear the search to see all projects.'
              : 'Start with a project to give your team’s work a home.'}
          </EmptyState>
        </section>
      )}
      {open && (
        <Modal title="Create a project" onClose={() => setOpen(false)}>
          <p className="modal-intro">Give this work a name and a customer to get started.</p>
          <Form className="stack-form" onSubmit={submit}>
            <Input
              label="Project name"
              name="name"
              placeholder="e.g. Westside onboarding"
              autoFocus
              required
            />
            <Input label="Customer" name="customer" placeholder="e.g. Westside Health" required />
            <div className="field">
              <label htmlFor="project-description">
                Description <span className="optional">Optional</span>
              </label>
              <textarea
                id="project-description"
                name="description"
                placeholder="What does success look like?"
                rows={3}
              />
            </div>
            <div className="modal-actions">
              <Button type="button" variant="secondary" onClick={() => setOpen(false)}>
                Cancel
              </Button>
              <Button type="submit">Create project</Button>
            </div>
          </Form>
        </Modal>
      )}
    </>
  );
}

function ProjectCard({ project, index }: { project: Project; index: number }) {
  const done = project.tasks.filter((task) => task.status === 'Done').length;
  const progress = project.tasks.length ? Math.round((done / project.tasks.length) * 100) : 0;
  return (
    <Link to={`/projects/${project.id}`} className="project-card">
      <div className="project-card-top">
        <span className={`project-avatar ${project.color}`}>{project.name.charAt(0)}</span>
        <button
          className="icon-button"
          aria-label={`More options for ${project.name}`}
          onClick={(event) => event.preventDefault()}
        >
          ···
        </button>
      </div>
      <span className="customer-label">{project.customer}</span>
      <h2>{project.name}</h2>
      <p>
        {project.description || 'A shared place to plan, coordinate, and move this work forward.'}
      </p>
      <div className="project-card-progress">
        <div className="progress-label">
          <span>Progress</span>
          <span>{progress}%</span>
        </div>
        <div className="progress-track">
          <span style={{ width: `${progress}%` }} />
        </div>
      </div>
      <div className="project-card-footer">
        <span>{project.tasks.length} tasks</span>
        <span className="avatar-stack">
          <span className={`tiny-avatar tone-${index % 3}`}>M</span>
          <span className={`tiny-avatar tone-${(index + 1) % 3}`}>J</span>
          <span className="avatar-more">+2</span>
        </span>
      </div>
    </Link>
  );
}

export function ProjectDetailPage({
  projects,
  onAddTask,
  onUpdateTask,
  onUpdateProject,
}: {
  projects: Project[];
  onAddTask: (projectId: string, task: Task) => void;
  onUpdateTask: (projectId: string, task: Task) => void;
  onUpdateProject: (project: Project) => void;
}) {
  const { projectId } = useParams();
  const project = projects.find((item) => item.id === projectId);
  const [open, setOpen] = useState(false);
  const [editOpen, setEditOpen] = useState(false);
  const [filter, setFilter] = useState('All tasks');
  if (!project)
    return (
      <section className="panel">
        <EmptyState
          title="We couldn’t find that project"
          action={
            <Link className="button button-secondary" to="/projects">
              Back to projects
            </Link>
          }
        >
          It may have been removed, or the link may be out of date.
        </EmptyState>
      </section>
    );

  const selectedProjectId = project.id;
  const selectedProject = project;
  const tasks = project.tasks.filter((task) => filter === 'All tasks' || task.status === filter);
  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const title = String(form.get('title') ?? '').trim();
    if (!title) return;
    onAddTask(selectedProjectId, {
      id: crypto.randomUUID(),
      title,
      owner: String(form.get('owner')),
      due: formatDate.format(new Date(`${String(form.get('due'))}T12:00:00`)),
      status: 'To do',
    });
    setOpen(false);
  }
  function submitProjectEdit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const name = String(form.get('name') ?? '').trim();
    const customer = String(form.get('customer') ?? '').trim();
    if (!name || !customer) return;
    onUpdateProject({
      ...selectedProject,
      name,
      customer,
      description: String(form.get('description') ?? '').trim(),
    });
    setEditOpen(false);
  }

  return (
    <>
      <div className="breadcrumb-link">
        <Link to="/projects">Projects</Link>
        <span>/</span>
        {project.name}
      </div>
      <div className="detail-heading">
        <div>
          <div className="project-title-row">
            <span className={`project-avatar ${project.color}`}>{project.name.charAt(0)}</span>
            <div>
              <div className="eyebrow">{project.customer}</div>
              <h1>{project.name}</h1>
            </div>
          </div>
          <p>{project.description}</p>
        </div>
        <div className="detail-actions">
          <Button variant="secondary" onClick={() => setEditOpen(true)}>
            Edit project
          </Button>
          <Button onClick={() => setOpen(true)}>＋ Add task</Button>
        </div>
      </div>
      <div className="detail-stats">
        <div>
          <span>Tasks</span>
          <strong>{project.tasks.length}</strong>
        </div>
        <div>
          <span>Completed</span>
          <strong>{project.tasks.filter((task) => task.status === 'Done').length}</strong>
        </div>
        <div>
          <span>Team members</span>
          <strong>4</strong>
        </div>
        <div className="detail-progress">
          <span>Overall progress</span>
          <div className="progress-track">
            <span
              style={{
                width: `${project.tasks.length ? Math.round((project.tasks.filter((task) => task.status === 'Done').length / project.tasks.length) * 100) : 0}%`,
              }}
            />
          </div>
        </div>
      </div>
      <section className="panel detail-task-panel">
        <div className="panel-heading">
          <div>
            <div className="eyebrow">PROJECT WORK</div>
            <h2>
              Tasks <span className="count-chip">{project.tasks.length}</span>
            </h2>
          </div>
          <select
            aria-label="Filter tasks"
            className="filter-select"
            value={filter}
            onChange={(event) => setFilter(event.target.value)}
          >
            {['All tasks', 'To do', 'In progress', 'Review', 'Done'].map((option) => (
              <option key={option}>{option}</option>
            ))}
          </select>
        </div>
        {project.tasks.length === 0 ? (
          <EmptyState
            title="No tasks just yet"
            action={<Button onClick={() => setOpen(true)}>Add the first task</Button>}
          >
            Break the project into a few clear next steps so everyone knows where to begin.
          </EmptyState>
        ) : tasks.length ? (
          <div className="table-wrap">
            <table className="task-table">
              <thead>
                <tr>
                  <th>Task</th>
                  <th>Assignee</th>
                  <th>Due date</th>
                  <th>Status</th>
                  <th>
                    <span className="sr-only">Edit task</span>
                  </th>
                </tr>
              </thead>
              <tbody>
                {tasks.map((task) => (
                  <TaskRow
                    key={task.id}
                    task={task}
                    onSave={(updated) => onUpdateTask(project.id, updated)}
                  />
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <EmptyState title="No tasks in this view">
            Choose another status filter to see more of the project.
          </EmptyState>
        )}
      </section>
      <div className="prototype-note">
        Task changes are held in browser memory only. Reloading this page restores the sample data.
      </div>
      {open && (
        <Modal title="Add a task" onClose={() => setOpen(false)}>
          <p className="modal-intro">What’s the next step for {project.name}?</p>
          <Form className="stack-form" onSubmit={submit}>
            <Input
              label="Task name"
              name="title"
              placeholder="e.g. Send kickoff notes"
              autoFocus
              required
            />
            <div className="field">
              <label htmlFor="task-owner">Assignee</label>
              <select id="task-owner" name="owner">
                {teamMembers.map((member) => (
                  <option key={member}>{member}</option>
                ))}
              </select>
            </div>
            <Input label="Due date" name="due" type="date" required />
            <div className="modal-actions">
              <Button type="button" variant="secondary" onClick={() => setOpen(false)}>
                Cancel
              </Button>
              <Button type="submit">Add task</Button>
            </div>
          </Form>
        </Modal>
      )}
      {editOpen && (
        <Modal title="Edit project" onClose={() => setEditOpen(false)}>
          <p className="modal-intro">Update the details your team sees for this project.</p>
          <Form className="stack-form" onSubmit={submitProjectEdit}>
            <Input
              label="Project name"
              name="name"
              defaultValue={project.name}
              autoFocus
              required
            />
            <Input label="Customer" name="customer" defaultValue={project.customer} required />
            <div className="field">
              <label htmlFor="edit-project-description">Description</label>
              <textarea
                id="edit-project-description"
                name="description"
                defaultValue={project.description}
                rows={3}
              />
            </div>
            <div className="modal-actions">
              <Button type="button" variant="secondary" onClick={() => setEditOpen(false)}>
                Cancel
              </Button>
              <Button type="submit">Save project</Button>
            </div>
          </Form>
        </Modal>
      )}
    </>
  );
}

function TaskRow({ task, onSave }: { task: Task; onSave: (task: Task) => void }) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(task);
  function save() {
    if (draft.title.trim()) {
      onSave({ ...draft, title: draft.title.trim() });
      setEditing(false);
    }
  }
  return (
    <tr>
      <td>
        {editing ? (
          <input
            className="inline-edit"
            aria-label="Task title"
            value={draft.title}
            onChange={(event) => setDraft({ ...draft, title: event.target.value })}
          />
        ) : (
          <strong>{task.title}</strong>
        )}
      </td>
      <td>
        {editing ? (
          <select
            className="inline-edit"
            aria-label="Assignee"
            value={draft.owner}
            onChange={(event) => setDraft({ ...draft, owner: event.target.value })}
          >
            {teamMembers.map((member) => (
              <option key={member}>{member}</option>
            ))}
          </select>
        ) : (
          <span className="assignee">
            <span className="tiny-avatar tone-1">{task.owner.charAt(0)}</span>
            {task.owner}
          </span>
        )}
      </td>
      <td>
        {editing ? (
          <input
            className="inline-edit"
            aria-label="Due date"
            type="text"
            value={draft.due}
            onChange={(event) => setDraft({ ...draft, due: event.target.value })}
          />
        ) : (
          task.due
        )}
      </td>
      <td>
        {editing ? (
          <select
            className="inline-edit"
            aria-label="Status"
            value={draft.status}
            onChange={(event) => setDraft({ ...draft, status: event.target.value as TaskStatus })}
          >
            {(['To do', 'In progress', 'Review', 'Done'] as TaskStatus[]).map((status) => (
              <option key={status}>{status}</option>
            ))}
          </select>
        ) : (
          <StatusBadge status={task.status} />
        )}
      </td>
      <td>
        {editing ? (
          <div className="row-edit-actions">
            <button className="save-inline" onClick={save}>
              Save
            </button>
            <button
              className="cancel-inline"
              onClick={() => {
                setDraft(task);
                setEditing(false);
              }}
            >
              Cancel
            </button>
          </div>
        ) : (
          <button
            className="icon-button"
            aria-label={`Edit ${task.title}`}
            onClick={() => setEditing(true)}
          >
            ···
          </button>
        )}
      </td>
    </tr>
  );
}

export function SettingsPage({ onSave }: { onSave: () => void }) {
  const [saved, setSaved] = useState(false);
  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaved(true);
    onSave();
    window.setTimeout(() => setSaved(false), 3000);
  }
  return (
    <>
      <Heading
        eyebrow="MAKE IT YOURS"
        title="Settings"
        description="A few workspace preferences to make OpsDesk feel like home."
      />
      <div className="settings-layout">
        <nav className="settings-nav" aria-label="Settings sections">
          <a className="selected" href="#workspace">
            General
          </a>
          <a href="#notifications">Notifications</a>
          <a href="#team">Team</a>
        </nav>
        <section className="panel settings-panel" id="workspace">
          <div className="panel-heading">
            <div>
              <div className="eyebrow">WORKSPACE PREFERENCES</div>
              <h2>General</h2>
            </div>
          </div>
          <form className="settings-form" onSubmit={submit}>
            <Input label="Workspace name" name="workspace" defaultValue="Workspace One" />
            <div className="field">
              <label htmlFor="timezone">Timezone</label>
              <select id="timezone" defaultValue="Asia/Kolkata">
                <option value="Asia/Kolkata">India Standard Time (UTC+5:30)</option>
                <option value="UTC">Coordinated Universal Time (UTC)</option>
                <option value="America/New_York">Eastern Time (UTC−5)</option>
              </select>
            </div>
            <div className="settings-divider" />
            <div className="setting-row">
              <div>
                <strong>Weekly project summary</strong>
                <p>Get a quick overview of what moved this week.</p>
              </div>
              <label className="switch">
                <input type="checkbox" defaultChecked aria-label="Weekly project summary" />
                <span />
              </label>
            </div>
            <div className="settings-divider" />
            <div className="settings-footer">
              <span className={saved ? 'saved-message visible' : 'saved-message'}>
                {saved ? '✓ Preferences saved' : ''}
              </span>
              <Button type="submit">Save changes</Button>
            </div>
          </form>
          <div className="settings-demo-note">
            Workspace settings are placeholders in this demo. No account or notification preferences
            are being saved.
          </div>
        </section>
      </div>
    </>
  );
}
