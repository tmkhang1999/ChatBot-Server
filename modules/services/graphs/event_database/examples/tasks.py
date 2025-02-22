examples = [
    {
        "input": "What is the overall progress of all tasks for the event?",
        "project_id": "X",
        "query": "SELECT COUNT(*) AS total_tasks, SUM(CASE WHEN status_id = 3 THEN 1 ELSE 0 END) AS completed_tasks FROM planz_tasks WHERE project_id = X AND deleted = 0;"
    },
    {
        "input": "How many tasks are completed, in progress, and pending?",
        "project_id": "X",
        "query": "SELECT SUM(CASE WHEN status_id = 1 THEN 1 ELSE 0 END) AS to_do_tasks, SUM(CASE WHEN status_id = 2 THEN 1 ELSE 0 END) AS in_progress_tasks, SUM(CASE WHEN status_id = 3 THEN 1 ELSE 0 END) AS completed_tasks FROM planz_tasks WHERE project_id = X AND deleted = 0;"
    },
    {
        "input": "Check all tasks for everyone | Show all tasks for the team.",
        "project_id": "X",
        "query": "SELECT id, title, created_date, deadline, description, CONCAT('{workspace_link}', id) AS task_link FROM planz_tasks WHERE project_id={project_id} AND deleted=0 ORDER BY created_date DESC;",
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
        "input": "How many tasks have been completed in the last 24 hours?",
        "project_id": "X",
        "query": "SELECT id, title FROM planz_tasks WHERE project_id = X AND status_id = 3 AND status_changed_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR) AND deleted = 0;"
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
        "input": "Are there any overdue tasks that need immediate attention?",
        "project_id": "X",
        "query": "SELECT id, title, deadline, description, CONCAT('{workspace_link}', id) AS task_link FROM planz_tasks WHERE project_id = X AND deadline < CURDATE() AND (status_id = 1 OR status_id = 2) AND deleted = 0 ORDER BY deadline ASC;"
    },
    {
        "input": "Which tasks are the highest priority right now?",
        "project_id": "X",
        "query": "SELECT id, title, deadline, description, CONCAT('{workspace_link}', id) AS task_link FROM planz_tasks WHERE project_id = X AND (status_id = 1 OR status_id = 2) AND deleted = 0 ORDER BY deadline ASC LIMIT 5;"
    },
    {
        "input": "Can you provide a summary of tasks due today or this week?",
        "project_id": "X",
        "query": "SELECT id, title, deadline, description, CONCAT('{workspace_link}', id) AS task_link FROM planz_tasks WHERE project_id = X AND deadline BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY) AND deleted = 0 ORDER BY deadline ASC;"
    },
    {
        "input": "What tasks should be focused on today to stay on track?",
        "project_id": "X",
        "query": "SELECT id, title, assigned_to, deadline FROM planz_tasks WHERE project_id = X AND deadline = CURDATE() AND deleted = 0 ORDER BY deadline ASC;"
    },
    {
        "input": "Check my tasks",
        "project_id": "X",
        "query": """
                SELECT id, title, created_date, deadline, description, CONCAT('{workspace_link}', id) AS task_link
                FROM planz_tasks
                WHERE project_id = {project_id} AND (
                    assigned_to = {user_id}
                    OR FIND_IN_SET({user_id}, collaborators)
                ) AND deleted=0;
                """,
    },
    {
        "input": "Can you list all tasks assigned to [specific team member or vendor]?",
        "project_id": "X",
        "query": """
                SELECT id, title, created_date, deadline, description FROM planz_tasks
                WHERE (assigned_to = (
                    SELECT id FROM planz_users
                    WHERE first_name = james AND last_name = Nguyen
                    LIMIT 1
                ) OR FIND_IN_SET((
                    SELECT id FROM planz_users
                    WHERE first_name = james AND last_name = Nguyen
                    LIMIT 1
                ), collaborators)
                )
                AND project_id = X AND deleted=0 ORDER BY;"
                """
    },
    {
        "input": "List tasks not assigned to anyone",
        "project_id": "X",
        "query": "SELECT id, title, deadline, description, CONCAT({workspace_link}, id) AS task_link FROM planz_tasks WHERE assigned_to = 0 AND project_id = X AND deleted=0 ORDER BY created_date DESC;",
    },
    {
        "input": "Have all tasks been assigned to the right team members?",
        "project_id": "X",
        "query": "SELECT id, title, deadline, description, CONCAT({workspace_link}, id) AS task_link FROM planz_tasks WHERE project_id = X AND (assigned_to IS NULL OR assigned_to = 0) AND deleted = 0;"
    },
    {
        "input": "List the tasks with no budget?",
        "project_id": "X",
        "query": "SELECT id, title, deadline, description, CONCAT({workspace_link}, id) AS task_link FROM planz_tasks WHERE budget_id = 0 AND project_id = X AND deleted=0 ORDER BY created_date DESC;",
    },
    {
        "input": "List the tasks with no deadline?",
        "project_id": "X",
        "query": "SELECT id, title, deadline, description, CONCAT({workspace_link}, id) AS task_link FROM planz_tasks WHERE deadline IS NULL AND project_id = X AND deleted = 0 ORDER BY created_date DESC;"
    }

]
