from opsdesk_api.seed import PROJECTS, TASKS_PER_PROJECT, task_id_for


def test_demo_task_ids_are_stable_and_unique_across_projects() -> None:
    task_ids = [
        task_id_for(project_id, number)
        for project_id, *_ in PROJECTS
        for number in range(1, TASKS_PER_PROJECT + 1)
    ]

    assert len(task_ids) == 60
    assert len(set(task_ids)) == 60
    assert task_ids == [
        task_id_for(project_id, number)
        for project_id, *_ in PROJECTS
        for number in range(1, TASKS_PER_PROJECT + 1)
    ]
