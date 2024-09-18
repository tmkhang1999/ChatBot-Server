examples = [
    {
        "input": "Check all tasks",
        "project_id": "X",
        "query": "SELECT id, title, deadline, description, CONCAT({workspace_link}, id) AS task_link FROM planz_tasks WHERE project_id = X AND deleted=0 ORDER BY created_date DESC;",
    },
    {
        "input": "Check to-do tasks",
        "project_id": "X",
        "query": "SELECT id, title, deadline, description, CONCAT({workspace_link}, id) AS task_link FROM planz_tasks WHERE status_id=1 AND project_id=X AND deleted=0 ORDER BY created_date DESC;",
    },
    {
        "input": "Check in-progress tasks",
        "project_id": "X",
        "query": "SELECT id, title, deadline, description, CONCAT({workspace_link}, id) AS task_link FROM planz_tasks WHERE status_id=2 AND project_id=X AND deleted=0 ORDER BY created_date DESC;",
    },
    {
        "input": "Check done | completed tasks",
        "project_id": "X",
        "query": "SELECT id, title, deadline, description, CONCAT({workspace_link}, id) AS task_link FROM planz_tasks WHERE status_id=3 AND project_id=X AND deleted=0 ORDER BY created_date DESC;",
    },
    {
        "input": "How many tasks have missed deadlines? | Check late tasks",
        "project_id": "X",
        "query": """
                SELECT id, title, deadline, description, CONCAT({workspace_link}, id) AS task_link
                FROM (
                    SELECT id, title, deadline, description, created_date FROM planz_tasks
                    WHERE deadline < NOW()
                    AND (status_id = 1 OR status_id = 2)
                    AND deleted = 0
                    AND project_id = X
                
                    UNION ALL
                
                    SELECT id, title, deadline, description, created_date FROM planz_tasks
                    WHERE status_changed_at > deadline
                    AND status_id = 3
                    AND deleted = 0
                    AND project_id = X
                ) AS miss_deadline_tasks
                ORDER BY created_date DESC;
        """,
    },
    {
        "input": "Check tasks not assigned to anyone",
        "project_id": "X",
        "query": "SELECT id, title, deadline, description, CONCAT({workspace_link}, id) AS task_link FROM planz_tasks WHERE assigned_to = 0 AND project_id = X AND deleted=0 ORDER BY created_date DESC;",
    },
    {
        "input": "List the tasks with no budget?",
        "project_id": "X",
        "query": "SELECT id, title, deadline, description, CONCAT({workspace_link}, id) AS task_link FROM planz_tasks WHERE budget_id = 0 AND project_id = X AND deleted=0 ORDER BY created_date DESC;",
    },
      {
        "input": "List the tasks with no deadline?",
        "project_id": "X",
        "query": "SELECT id, title, deadline, description, CONCAT({workspace_link}, id) FROM planz_tasks WHERE estimate_id = 0 AND project_id = X AND deleted=0 ORDER BY created_date DESC;",
    },
]
