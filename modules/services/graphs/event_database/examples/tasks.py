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
      "input": "How many tasks are pending, in progress and completed?",
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
    #############
    {
      "input": "Show all tasks for the team | Check the task list of all participants",
      "project_id": "X",
      "query": """
        SELECT
          COUNT(*) OVER () AS total_tasks,
          title, deadline, description,
          CONCAT('{workspace_link}', id) AS task_link
        FROM planz_tasks
        WHERE project_id = X
        AND deleted = 0 ORDER BY deadline ASC;
      """
    },
    {
        "input": "Show my tasks for me | Check the task list assigned to me",
        "project_id": "X",
        "query": """
            SELECT
              COUNT(*) OVER () AS my_total_tasks,
              title, deadline, description,
              CONCAT('{workspace_link}', id) AS task_link
            FROM planz_tasks
            WHERE project_id = X
            AND (assigned_to = '{user_id}' OR FIND_IN_SET('{user_id}', collaborators))
            AND deleted = 0 ORDER BY deadline ASC;
          """
    },
    {
        "input": "List all tasks assigned to a specific team member | Check tasks assigned to James Nguyen",
        "project_id": "X",
        "query": """
           SELECT
             title, deadline, description,
             CONCAT('{workspace_link}', id) AS task_link,
             COUNT(*) OVER () AS James_Nguyen_total_tasks
           FROM planz_tasks
           WHERE (assigned_to = (
             SELECT id FROM planz_users WHERE first_name = 'James' AND last_name = 'Nguyen' LIMIT 1
           ) OR FIND_IN_SET((
             SELECT id FROM planz_users WHERE first_name = 'James' AND last_name = 'Nguyen' LIMIT 1
           ), collaborators))
           AND project_id = X AND deleted = 0
           ORDER BY deadline ASC;
        """
    },
    #############
    {
      "input": "Show to-do tasks of everyone | Check to-do tasks of all participants",
      "project_id": "X",
      "query": """
        SELECT
          title, deadline, description,
          CONCAT('{workspace_link}', id) AS task_link,
          COUNT(*) OVER () AS total_to_do_tasks
        FROM planz_tasks
        WHERE status_id = 1 AND project_id = X
        AND deleted = 0 ORDER BY deadline ASC;
      """
    },
    {
        "input": "Show my to-do tasks | Check the to do tasks assigned to me",
        "project_id": "X",
        "query": """
          SELECT
            title, deadline, description,
            CONCAT('{workspace_link}', id) AS task_link,
            COUNT(*) OVER () AS my_total_to_do_tasks
          FROM planz_tasks
          WHERE project_id = X AND status_id = 1
          AND (assigned_to = '{user_id}' OR FIND_IN_SET('{user_id}', collaborators))
          AND deleted = 0 ORDER BY deadline ASC;
        """
    },
    {
        "input": "Check to-do tasks assigned to a specific team member | Show to do tasks assigned to James Nguyen",
        "project_id": "X",
        "query": """
           SELECT
             title, deadline, description,
             CONCAT('{workspace_link}', id) AS task_link,
             COUNT(*) OVER () AS James_Nguyen_total_to_do_tasks
           FROM planz_tasks
           WHERE (assigned_to = (
             SELECT id FROM planz_users WHERE first_name = 'James' AND last_name = 'Nguyen' LIMIT 1
           ) OR FIND_IN_SET((
             SELECT id FROM planz_users WHERE first_name = 'James' AND last_name = 'Nguyen' LIMIT 1
           ), collaborators))
           AND project_id = X AND AND status_id = 1
           AND deleted = 0 ORDER BY deadline ASC;
        """
    },
    #############
    {
      "input": "Show in-progress tasks of everyone | Check in-progress tasks of all participants",
      "project_id": "X",
      "query": """
        SELECT
          title, deadline, description,
          CONCAT('{workspace_link}', id) AS task_link,
          COUNT(*) OVER () AS total_in_progress_tasks
        FROM planz_tasks
        WHERE status_id = 2 AND project_id = X
        AND deleted = 0 ORDER BY deadline ASC;
      """
    },
    {
        "input": "Show my in-progress task list | Check the in-progress tasks assigned to me",
        "project_id": "X",
        "query": """
          SELECT
            title, deadline, description,
            CONCAT('{workspace_link}', id) AS task_link,
            COUNT(*) OVER () AS my_total_in_progress_tasks
          FROM planz_tasks
          WHERE project_id = X AND status_id = 2
          AND (assigned_to = '{user_id}' OR FIND_IN_SET('{user_id}', collaborators))
          AND deleted = 0 ORDER BY deadline ASC;
        """
    },
    {
        "input": "Show in progress tasks assigned to a specific member | Check in-progress tasks of James Nguyen",
        "project_id": "X",
        "query": """
           SELECT
             title, deadline, description,
             CONCAT('{workspace_link}', id) AS task_link,
             COUNT(*) OVER () AS James_Nguyen_total_to_do_tasks
           FROM planz_tasks
           WHERE (assigned_to = (
             SELECT id FROM planz_users WHERE first_name = 'James' AND last_name = 'Nguyen' LIMIT 1
           ) OR FIND_IN_SET((
             SELECT id FROM planz_users WHERE first_name = 'James' AND last_name = 'Nguyen' LIMIT 1
           ), collaborators))
           AND project_id = X AND AND status_id = 2
           AND deleted = 0 ORDER BY deadline ASC;
        """
    },
    #############
    {
      "input": "Check completed tasks of everyone | Show the done task list of all participants",
      "project_id": "X",
      "query": """
        SELECT
          title, deadline, description,
          CONCAT('{workspace_link}', id) AS task_link,
          COUNT(*) OVER () AS total_completed_tasks
        FROM planz_tasks
        WHERE status_id = 3 AND project_id = X
        AND deleted = 0 ORDER BY deadline ASC;
      """
    },
    {
        "input": "Show my done task list | Check the completed tasks assigned to me",
        "project_id": "X",
        "query": """
          SELECT
            title, deadline, description,
            CONCAT('{workspace_link}', id) AS task_link,
            COUNT(*) OVER () AS my_total_completed_tasks
          FROM planz_tasks
          WHERE project_id = X AND status_id = 3
          AND (assigned_to = '{user_id}' OR FIND_IN_SET('{user_id}', collaborators))
          AND deleted = 0 ORDER BY deadline ASC;
        """
    },
    {
        "input": "Check all completed tasks assigned to a specific team member | What tasks has James Nguyen done?",
        "project_id": "X",
        "query": """
           SELECT
             title, deadline, description,
             CONCAT('{workspace_link}', id) AS task_link,
             COUNT(*) OVER () AS James_Nguyen_total_to_do_tasks
           FROM planz_tasks
           WHERE (assigned_to = (
             SELECT id FROM planz_users WHERE first_name = 'James' AND last_name = 'Nguyen' LIMIT 1
           ) OR FIND_IN_SET((
             SELECT id FROM planz_users WHERE first_name = 'James' AND last_name = 'Nguyen' LIMIT 1
           ), collaborators))
           AND project_id = X AND AND status_id = 3
           AND deleted = 0 ORDER BY deadline ASC;
        """
    },
    {
        "input": "How many tasks have been completed in the last 24 hours?",
        "project_id": "X",
        "query": """
            SELECT
              title, deadline, description,
              CONCAT('{workspace_link}', id) AS task_link,
              COUNT(*) OVER () AS total_24_completed_tasks
            FROM planz_tasks
            WHERE project_id = X AND status_id = 3
            AND status_changed_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
            AND deleted = 0 ORDER BY deadline ASC;
        """
    },
    #############
    {
        "input": "How many tasks have missed deadlines? | Show late tasks",
        "project_id": "X",
        "query": """
            SELECT
              COUNT(*) OVER () AS total_late_tasks,
              title, deadline,
              CONCAT('{workspace_link}', id) AS task_link
            FROM planz_tasks
            WHERE project_id = X AND deadline <= NOW()
            AND (status_id IN (1, 2) OR (status_id = 3 AND status_changed_at > deadline))
            AND deleted = 0 ORDER BY deadline ASC;
          """
    },
    {
        "input": "Are there any overdue tasks that need immediate attention?",
        "project_id": "X",
        "query": """
             SELECT
               COUNT(*) OVER () AS total_overdue_tasks,
               title, deadline,
               CONCAT('{workspace_link}', id) AS task_link
             FROM planz_tasks
             WHERE project_id = X AND deadline <= NOW()
             AND status_id IN (1,2)
             AND deleted = 0 ORDER BY deadline ASC;
        """
    },
    #############
    {
      "input": "Which tasks are the highest priority right now?",
      "project_id": "X",
      "query": """
          SELECT
              COUNT(*) OVER () AS total_need_priority_tasks,
              title,
              deadline,
              CASE
                  WHEN priority_id = 1 THEN 'Low'
                  WHEN priority_id = 2 THEN 'Medium'
                  WHEN priority_id = 5 THEN 'High'
                  ELSE 'Unknown'
              END AS priority_level,
              CONCAT('{workspace_link}', id) AS task_link
          FROM planz_tasks
          WHERE project_id = X
              AND status_id IN (1, 2)      -- To-do or In-progress
              AND priority_id IN (1, 2, 5) -- Include Low, Medium, and High priority
              AND deleted = 0
          ORDER BY priority_id DESC, deadline ASC;
      """
    },
    {
        "input": "Which tasks are the medium priority right now?",
        "project_id": "X",
        "query": """
           SELECT
               COUNT(*) OVER () AS total_medium_priority_tasks,
               title, deadline,
               CONCAT('{workspace_link}', id) AS task_link
           FROM planz_tasks
           WHERE project_id = X
               AND status_id IN (1, 2)
               AND priority_id = 2
               AND deleted = 0
           ORDER BY deadline ASC;
       """
    },
    {
      "input": "Provide a summary of tasks due today",
      "project_id": "X",
      "query": """
        SELECT
          COUNT(*) OVER () AS total_today_due_tasks,
          title, deadline, description,
          CONCAT('{workspace_link}', id) AS task_link
        FROM planz_tasks
        WHERE project_id = X
        AND deadline BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)
        AND deleted = 0
        ORDER BY deadline ASC;
      """
    },
    {
      "input": "What tasks should be focused to stay on track?",
      "project_id": "X",
      "query": """
        SELECT
          title, deadline, description,
          CONCAT('{workspace_link}', id) AS task_link
        FROM planz_tasks
        WHERE project_id = X AND status_id IN (1, 2) AND deleted = 0
        ORDER BY deadline ASC LIMIT 5;
      """
    },
    {
      "input": "List tasks not assigned to anyone | Have all tasks been assigned?",
      "project_id": "X",
      "query": """
            SELECT
                COUNT(*) OVER () AS total_unassigned_tasks,
                title AS unassigned_task_title,
                deadline,
                CONCAT('{workspace_link}', id) AS unassigned_task_link
            FROM planz_tasks
            WHERE project_id = X AND assigned_to = 0 AND deleted = 0
            ORDER BY deadline ASC
       """
    },
    {
      "input": "List the tasks with no budget",
      "project_id": "X",
      "query": """
        SELECT
          COUNT(*) OVER () AS total_no_budget_tasks,
          title, deadline, description,
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
          COUNT(*) OVER () AS total_no_deadline_tasks,
          title, deadline, description,
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
        SELECT COUNT(*) AS total_last_month_tasks
        FROM planz_tasks
        WHERE project_id = X
        AND created_date >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
        AND deleted = 0;
      """
    }
]