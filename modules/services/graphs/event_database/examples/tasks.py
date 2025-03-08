task_examples = [
    {
      "input": "What is the overall progress of all tasks for the event?",
      "project_id": "X",
      "query": """
        SELECT
          COUNT(*) AS total_tasks,
          SUM(CASE WHEN status_id = 3 THEN 1 ELSE 0 END) AS completed_tasks
        FROM planz_tasks
        WHERE project_id = X AND deleted = 0;
      """
    },
    {
      "input": "How many tasks are completed, in progress, and pending?",
      "project_id": "X",
      "query": """
        SELECT
          SUM(CASE WHEN status_id = 1 THEN 1 ELSE 0 END) AS to_do_tasks,
          SUM(CASE WHEN status_id = 2 THEN 1 ELSE 0 END) AS in_progress_tasks,
          SUM(CASE WHEN status_id = 3 THEN 1 ELSE 0 END) AS completed_tasks
        FROM planz_tasks
        WHERE project_id = X AND deleted = 0;
      """
    },
    {
      "input": "Show all tasks for the team",
      "project_id": "X",
      "query": """
        SELECT
          id, title, created_date, deadline, description,
          CONCAT('{workspace_link}', id) AS task_link
        FROM planz_tasks
        WHERE project_id = X AND deleted = 0
        ORDER BY created_date DESC;
      """
    },
    {
      "input": "Check to-do tasks",
      "project_id": "X",
      "query": """
        SELECT
          id, title, deadline, description,
          CONCAT('{workspace_link}', id) AS task_link
        FROM planz_tasks
        WHERE status_id = 1 AND project_id = X AND deleted = 0
        ORDER BY created_date DESC;
      """
    },
    {
      "input": "Check in-progress tasks",
      "project_id": "X",
      "query": """
        SELECT
          id, title, deadline, description,
          CONCAT('{workspace_link}', id) AS task_link
        FROM planz_tasks
        WHERE status_id = 2 AND project_id = X AND deleted = 0
        ORDER BY created_date DESC;
      """
    },
    {
      "input": "Check completed tasks",
      "project_id": "X",
      "query": """
        SELECT
          id, title, deadline, description,
          CONCAT('{workspace_link}', id) AS task_link
        FROM planz_tasks
        WHERE status_id = 3 AND project_id = X AND deleted = 0
        ORDER BY created_date DESC;
      """
    },
    {
      "input": "How many tasks have been completed in the last 24 hours?",
      "project_id": "X",
      "query": """
        SELECT id, title, deadline, description, CONCAT('{workspace_link}', id) AS task_link
        FROM planz_tasks
        WHERE project_id = X AND status_id = 3
        AND status_changed_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
        AND deleted = 0;
      """
    },
    {
      "input": "How many tasks have missed deadlines? | Check late tasks",
      "project_id": "X",
      "query": """
        SELECT
          id, title, deadline, description,
          CONCAT('{workspace_link}', id) AS task_link
        FROM planz_tasks
        WHERE project_id = X AND deleted = 0
        AND deadline < NOW()
        AND (status_id IN (1, 2) OR (status_id = 3 AND status_changed_at > deadline))
        ORDER BY deadline ASC;
      """
    },
    {
      "input": "Are there any overdue tasks that need immediate attention?",
      "project_id": "X",
      "query": """
        SELECT
          id, title, deadline, description,
          CONCAT('{workspace_link}', id) AS task_link
        FROM planz_tasks
        WHERE project_id = X AND deadline =< CURDATE()
        AND status_id IN (1,2) AND deleted = 0
        ORDER BY deadline ASC;
      """
    },
    {
      "input": "Which tasks are the highest priority right now?",
      "project_id": "X",
      "query": """
        SELECT
          id, title, deadline, description, priority_id,
          CONCAT('{workspace_link}', id) AS task_link
        FROM planz_tasks
        WHERE project_id = X
        AND status_id IN (1, 2)          -- To-do or In-progress
        AND priority_id IN (1, 2)        -- Medium or High priority
        AND deleted = 0
        ORDER BY priority_id DESC, deadline ASC  -- High priority first, then by deadline
        LIMIT 5;                        -- Top 5 tasks
      """
    },
    {
      "input": "Provide a summary of tasks due today or this week",
      "project_id": "X",
      "query": """
        SELECT
          id, title, deadline, description,
          CONCAT('{workspace_link}', id) AS task_link
        FROM planz_tasks
        WHERE project_id = X
        AND deadline BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)
        AND deleted = 0
        ORDER BY deadline ASC;
      """
    },
    {
      "input": "What tasks should be focused on today to stay on track?",
      "project_id": "X",
      "query": """
        SELECT
          id, title, assigned_to, deadline, description,
          CONCAT('{workspace_link}', id) AS task_link
        FROM planz_tasks
        WHERE project_id = X AND status_id IN (1, 2) AND deleted = 0
        ORDER BY deadline ASC LIMIT 5;
      """
    },
    {
      "input": "Check my tasks",
      "project_id": "X",
      "query": """
        SELECT
          id, title, created_date, deadline, description,
          CONCAT('{workspace_link}', id) AS task_link
        FROM planz_tasks
        WHERE project_id = X
        AND (assigned_to = Y OR FIND_IN_SET(Y, collaborators))
        AND deleted = 0;
      """
    },
    {
      "input": "List all tasks assigned to a specific team member",
      "project_id": "X",
      "query": """
        SELECT id, title, created_date, deadline, description
        FROM planz_tasks
        WHERE (assigned_to = (
          SELECT id FROM planz_users WHERE first_name = 'James' AND last_name = 'Nguyen' LIMIT 1
        ) OR FIND_IN_SET((
          SELECT id FROM planz_users WHERE first_name = 'James' AND last_name = 'Nguyen' LIMIT 1
        ), collaborators))
        AND project_id = X AND deleted = 0
        ORDER BY created_date DESC;
      """
    },
    {
      "input": "List tasks not assigned to anyone",
      "project_id": "X",
      "query": """
        SELECT
          id, title, deadline, description,
          CONCAT('{workspace_link}', id) AS task_link
        FROM planz_tasks
        WHERE assigned_to = 0 AND project_id = X AND deleted = 0
        ORDER BY created_date DESC;
      """
    },
    {
      "input": "Have all tasks been assigned to the right team members?",
      "project_id": "X",
      "query": """
        SELECT
          id, title, deadline, description,
          CONCAT('{workspace_link}', id) AS task_link
        FROM planz_tasks
        WHERE project_id = X
        AND (assigned_to IS NULL OR assigned_to = 0)
        AND deleted = 0;
      """
    },
    {
      "input": "List the tasks with no budget",
      "project_id": "X",
      "query": """
        SELECT
          id, title, deadline, description,
          CONCAT('{workspace_link}', id) AS task_link
        FROM planz_tasks
        WHERE budget_id = 0 AND project_id = X AND deleted = 0
        ORDER BY created_date DESC;
      """
    },
    {
      "input": "List the tasks with no deadline",
      "project_id": "X",
      "query": """
        SELECT
          id, title, deadline, description,
          CONCAT('{workspace_link}', id) AS task_link
        FROM planz_tasks
        WHERE deadline IS NULL AND project_id = X AND deleted = 0
        ORDER BY created_date DESC;
      """
    },
    {
      "input": "How many tasks were created in the last month?",
      "project_id": "X",
      "query": """
        SELECT COUNT(*) AS tasks_last_month
        FROM planz_tasks
        WHERE project_id = X
        AND created_date >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
        AND deleted = 0;
      """
    }
]