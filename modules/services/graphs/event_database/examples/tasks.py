examples = [
    {
        "input": "Check all tasks for everyone in this event",
        "project_id": "X",
        "query": "SELECT id, title, deadline, description, CONCAT({workspace_link}, id) AS task_link FROM planz_tasks WHERE project_id = X AND deleted=0 ORDER BY created_date DESC;",
    },
    {
        "input": "Check to-do tasks for everyone in this event",
        "project_id": "X",
        "query": "SELECT id, title, deadline, description, CONCAT({workspace_link}, id) AS task_link FROM planz_tasks WHERE status_id=1 AND project_id=X AND deleted=0 ORDER BY created_date DESC;",
    },
    {
        "input": "Check in-progress tasks for everyone in this event",
        "project_id": "X",
        "query": "SELECT id, title, deadline, description, CONCAT({workspace_link}, id) AS task_link FROM planz_tasks WHERE status_id=2 AND project_id=X AND deleted=0 ORDER BY created_date DESC;",
    },
    {
        "input": "Check done/completed tasks for everyone in this event",
        "project_id": "X",
        "query": "SELECT id, title, deadline, description, CONCAT({workspace_link}, id) AS task_link FROM planz_tasks WHERE status_id=3 AND project_id=X AND deleted=0 ORDER BY created_date DESC;",
    },
    {
        "input": "How many tasks have missed deadlines? | Check late tasks for everyone in this event | Are there any tasks that are behind schedule?",
        "project_id": "X",
        "query": """
                SELECT id, title, deadline, description, CONCAT({workspace_link}, id) AS task_link
                FROM (
                    SELECT id, title, deadline, description, created_date FROM planz_tasks
                    WHERE deadline < NOW()
                    AND (status_id = 1 OR status_id = 2)
                    AND deleted = 0
                    AND project_id = {project_id}
                
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
        "input": "Check all tasks assigned to me | List all my tasks for this event.",
        "project_id": "X",
        "query": """
                SELECT id, title, created_date, deadline, description, CONCAT('{workspace_link}', id) AS task_link
                FROM planz_tasks
                WHERE project_id = X AND (
                    assigned_to = {user_id}
                    OR FIND_IN_SET({user_id}, collaborators)
                ) AND deleted=0 ORDER BY created_date DESC;;
                """
    },
    {
        "input": "Check my to-do tasks in this event",
        "project_id": "X",
        "query": """
                SELECT id, title, created_date, deadline, description, CONCAT('{workspace_link}', id) AS task_link
                FROM planz_tasks
                WHERE status_id = 1 AND project_id = X AND (
                    assigned_to = {user_id}
                    OR FIND_IN_SET({user_id}, collaborators)
                ) AND deleted=0 ORDER BY created_date DESC;
                """,
    },
    {
        "input": "Check my in-progress tasks in this event | What tasks am I currently doing?",
        "project_id": "X",
        "query": """
                SELECT id, title, created_date, deadline, description, CONCAT('{workspace_link}', id) AS task_link
                FROM planz_tasks
                WHERE status_id = 2 AND project_id = X AND (
                    assigned_to = {user_id}
                    OR FIND_IN_SET({user_id}, collaborators)
                ) AND deleted=0 ORDER BY created_date DESC;
                """,
    },
    {
        "input": "Check my completed tasks in this event | What have I finished?",
        "project_id": "X",
        "query": """
                SELECT id, title, created_date, deadline, description, CONCAT('{workspace_link}', id) AS task_link
                FROM planz_tasks
                WHERE status_id = 3 AND project_id = X AND (
                    assigned_to = {user_id}
                    OR FIND_IN_SET({user_id}, collaborators)
                ) AND deleted=0 ORDER BY created_date DESC;
                """,
    },
    {
        "input": "Check my late tasks in this event | Show me the tasks I’ve missed deadlines for",
        "project_id": "X",
        "query": """
                SELECT id, title, created_date, deadline, description, CONCAT('{workspace_link}', id) AS task_link
                FROM (
                    SELECT id, title, created_date, deadline, description FROM planz_tasks
                    WHERE deadline < NOW()
                    AND (status_id = 1 OR status_id = 2)
                    AND project_id = X
                    AND deleted=0
                    AND (assigned_to = {user_id} OR FIND_IN_SET({user_id}, collaborators))
        
                    UNION ALL
        
                    SELECT id, title, created_date, deadline, description FROM planz_tasks
                    WHERE status_changed_at > deadline
                    AND status_id = 3
                    AND project_id = X
                    AND deleted=0
                    AND (assigned_to = {user_id} OR FIND_IN_SET({user_id}, collaborators))
                ) AS user_late_tasks ORDER BY created_date DESC;
                """,
    },
    {
        "input": "Check all tasks of James Nguyen in this event | List the tasks assigned to James Nguyen.",
        "project_id": "X",
        "query": """
                SELECT id, title, created_date, deadline, description FROM planz_tasks
                WHERE (assigned_to = (
                    SELECT id FROM planz_users
                    WHERE first_name = 'James' AND last_name = 'Nguyen'
                    LIMIT 1
                ) OR FIND_IN_SET((
                    SELECT id FROM planz_users
                    WHERE first_name = 'James' AND last_name = 'Nguyen'
                    LIMIT 1
                ), collaborators)
                ) AND project_id = X AND deleted=0  ORDER BY created_date DESC;
                """,
    },
    {
        "input": "Check to-do tasks of John Doe in this event | What does John Doe need to do?",
        "project_id": "X",
        "query": """
                SELECT id, title, created_date, deadline, description, CONCAT('{workspace_link}', id) AS task_link
                FROM planz_tasks
                WHERE status_id=1 AND project_id = X AND (
                    assigned_to = (
                        SELECT id FROM planz_users
                        WHERE first_name = 'John' AND last_name = 'Doe'
                        LIMIT 1
                    ) OR FIND_IN_SET((
                        SELECT id FROM planz_users
                        WHERE first_name = 'John' AND last_name = 'Doe'
                        LIMIT 1
                    ), collaborators)
                ) AND deleted=0  ORDER BY created_date DESC;
                """,
    },
    {
        "input": "Check in-progress tasks of John Doe in this event | Show the tasks John Doe is currently working on",
        "project_id": "X",
        "query": """
            SELECT id, title, created_date, deadline, description, CONCAT('{workspace_link}', id) AS task_link
            FROM planz_tasks
            WHERE status_id=2 AND project_id = X AND (
                assigned_to = (
                    SELECT id FROM planz_users
                    WHERE first_name = 'John' AND last_name = 'Doe'
                    LIMIT 1
                ) OR FIND_IN_SET((
                    SELECT id FROM planz_users
                    WHERE first_name = 'John' AND last_name = 'Doe'
                    LIMIT 1
                ), collaborators)
            ) AND deleted=0  ORDER BY created_date DESC;
            """,
    },
    {
        "input": "Check done tasks of John Doe in this event | What has John Doe finished?",
        "project_id": "X",
        "query": """
        SELECT id, title, created_date, deadline, description, CONCAT('{workspace_link}', id) AS task_link
        FROM planz_tasks
        WHERE status_id=3 AND project_id = X AND (
            assigned_to = (
                SELECT id FROM planz_users
                WHERE first_name = 'John' AND last_name = 'Doe'
                LIMIT 1
            ) OR FIND_IN_SET((
                SELECT id FROM planz_users
                WHERE first_name = 'John' AND last_name = 'Doe'
                LIMIT 1
            ), collaborators)
        ) AND deleted=0  ORDER BY created_date DESC;
        """,
    },
    {
        "input": "List John Doe’s late tasks in this event | What overdue tasks does John Doe have?",
        "project_id": "X",
        "query": """
                SELECT id, title, created_date, deadline, description, CONCAT('{workspace_link}', id) AS task_link
                FROM (
                    SELECT id, title, created_date, deadline, description FROM planz_tasks
                    WHERE deadline < NOW()
                    AND (status_id = 1 OR status_id = 2)
                    AND project_id = X
                    AND deleted=0
                    AND (assigned_to = (
                        SELECT id FROM planz_users
                        WHERE first_name = 'John' AND last_name = 'Doe'
                        LIMIT 1
                    ) OR FIND_IN_SET((
                        SELECT id FROM planz_users
                        WHERE first_name = 'John' AND last_name = 'Doe'
                        LIMIT 1
                    ), collaborators))
        
                    UNION ALL
        
                    SELECT id, title, created_date, deadline, description FROM planz_tasks
                    WHERE status_changed_at > deadline
                    AND status_id = 3
                    AND deleted=0
                    AND project_id = X
                    AND (assigned_to = (
                        SELECT id FROM planz_users
                        WHERE first_name = 'John' AND last_name = 'Doe'
                        LIMIT 1
                    ) OR FIND_IN_SET((
                        SELECT id FROM planz_users
                        WHERE first_name = 'John' AND last_name = 'Doe'
                        LIMIT 1
                    ), collaborators))
                ) AS user_late_tasks  ORDER BY created_date DESC;
                """,
    },
    {
        "input": "Check tasks not assigned to anyone | What tasks haven't been assigned yet?",
        "project_id": "X",
        "query": "SELECT id, title, deadline, description, CONCAT({workspace_link}, id) AS task_link FROM planz_tasks WHERE assigned_to = 0 AND project_id = X AND deleted=0 ORDER BY created_date DESC;",
    },
    {
        "input": "List the tasks with no budget? | Show me tasks that don't have a budget.",
        "project_id": "X",
        "query": "SELECT id, title, deadline, description, CONCAT({workspace_link}, id) AS task_link FROM planz_tasks WHERE budget_id = 0 AND project_id = X AND deleted=0 ORDER BY created_date DESC;",
    },
    {
        "input": "List the tasks with no deadline? | Have all tasks been assigned to the appropriate team members with clear deadlines?",
        "project_id": "X",
        "query": "SELECT id, title, deadline, description, CONCAT({workspace_link}, id) FROM planz_tasks WHERE estimate_id = 0 AND project_id = X AND deleted=0 ORDER BY created_date DESC;",
    },
]
