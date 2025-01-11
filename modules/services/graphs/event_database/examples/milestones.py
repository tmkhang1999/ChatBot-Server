examples = [
    {
        "input": "List milestones?",
        "project_id": "X",
        "query": "SELECT * FROM planz_milestones WHERE project_id = X;",
    },
    {
        "input": "How much have milestones been completed? | Check the progress of each milestone",
        "project_id": "X",
        "query": """
        SELECT
            milestones.id AS milestone_id,
            IFNULL(total_tasks_table.total_tasks, 0) AS total_tasks,
            IFNULL(completed_tasks_table.completed_tasks, 0) AS completed_tasks,
            IFNULL((completed_tasks_table.completed_tasks / total_tasks_table.total_tasks) * 100, 0) AS percentage_tasks_completed
        FROM
            (SELECT * FROM planz_milestones WHERE project_id = X AND deleted = 0) AS milestones
        LEFT JOIN
            (SELECT
                milestone_id,
                COUNT(id) AS total_tasks
            FROM
                planz_tasks
            WHERE
                deleted = 0
                AND project_id = X
            GROUP BY
                milestone_id) AS total_tasks_table
        ON
            total_tasks_table.milestone_id = milestones.id
        LEFT JOIN
            (SELECT
                milestone_id,
                COUNT(id) AS completed_tasks
            FROM
                planz_tasks
            WHERE
                deleted = 0
                AND project_id = X
                AND status_id = 3
            GROUP BY
                milestone_id) AS completed_tasks_table
        ON
            completed_tasks_table.milestone_id = milestones.id;
        """,
    },
    {
        "input": "Check milestone Y?",
        "project_id": "X",
        "query": "SELECT * FROM planz_milestones WHERE project_id = X LIMIT 1 OFFSET (Y - 1)"
    },
    {
        "input": "Check tasks in milestone Y?",
        "project_id": "X",
        "query": "SELECT * FROM planz_tasks WHERE milestone_id = Y AND project_id = X",
    }
]
