"""Insert/update a small deterministic dataset for local API demonstrations."""

from datetime import date, timedelta
from uuid import UUID, uuid5

from opsdesk_api.config import DEFAULT_WORKSPACE_ID, Settings
from opsdesk_api.database.models import Project, Task
from opsdesk_api.database.session import Database

PROJECTS = (
    (UUID("10000000-0000-4000-8000-000000000001"), "Northstar", "Northstar Health"),
    (UUID("10000000-0000-4000-8000-000000000002"), "Atlas rollout", "Atlas Co"),
    (UUID("10000000-0000-4000-8000-000000000003"), "Meridian renewal", "Meridian Group"),
)

TASKS_PER_PROJECT = 20


def task_id_for(project_id: UUID, number: int) -> UUID:
    """Return the stable task ID in a project-specific UUID namespace."""
    if not 1 <= number <= TASKS_PER_PROJECT:
        raise ValueError(f"task number must be between 1 and {TASKS_PER_PROJECT}")
    return uuid5(project_id, f"opsdesk-demo-task-{number:02d}")


def seed(database_url: str | None = None) -> None:
    settings = Settings.from_environment()
    database = Database(database_url or settings.database_url)
    try:
        with database.sessions.begin() as session:
            for project_id, name, customer in PROJECTS:
                project = session.get(Project, project_id)
                if project is None:
                    project = Project(
                        id=project_id,
                        workspace_id=DEFAULT_WORKSPACE_ID,
                        name=name,
                        customer=customer,
                        description=f"Demo dataset project for {customer}.",
                    )
                    session.add(project)
                else:
                    project.name = name
                    project.customer = customer
                    project.description = f"Demo dataset project for {customer}."
                # Keep the explicit flushes inside this one transaction. Queries
                # must see writes staged for the current project even though the
                # shared session factory intentionally disables autoflush.
                session.flush()
                for number in range(1, TASKS_PER_PROJECT + 1):
                    task_id = task_id_for(project_id, number)
                    task = session.get(Task, task_id)
                    values = {
                        "title": f"{name} demo task {number:02d}",
                        "owner": "Demo User",
                        "due": date(2026, 11, 1) + timedelta(days=number),
                        "status": ("To do", "In progress", "Review", "Done")[number % 4],
                    }
                    if task is None:
                        session.add(Task(id=task_id, project_id=project_id, **values))
                    else:
                        for key, value in values.items():
                            setattr(task, key, value)
                session.flush()
        print("Seeded 3 demo projects and 60 tasks (safe to run again).")
    finally:
        database.engine.dispose()


if __name__ == "__main__":
    seed()
