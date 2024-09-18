examples = [
    {
        "input": "The overview of the event",
        "project_id": "X",
        "query": """
        SELECT
            planz_projects.title AS project_title,
            planz_projects.description,
            planz_projects.start_date,
            planz_projects.deadline,
            (SELECT budget FROM planz_budgets WHERE project_id = planz_projects.id) AS budget,
            (SELECT SUM(amount) FROM planz_expenses WHERE project_id = planz_projects.id) AS total_expense,
            (IFNULL(completed_points_table.completed_points, 0) / IFNULL(total_points_table.total_points, 1)) * 100 AS progress
        FROM
            planz_projects
        LEFT JOIN (
            SELECT project_id, SUM(points) AS total_points
            FROM planz_tasks
            WHERE deleted = 0
            GROUP BY project_id
        ) AS total_points_table ON total_points_table.project_id = planz_projects.id
        LEFT JOIN (
            SELECT project_id, SUM(points) AS completed_points
            FROM planz_tasks
            WHERE deleted = 0 AND status_id = 3 -- Assuming '3' indicates completed tasks
            GROUP BY project_id
        ) AS completed_points_table ON completed_points_table.project_id = planz_projects.id
        WHERE
            planz_projects.deleted = 0
            AND planz_projects.id = X;

        """,
    },
    {
        "input": "The progress of the event",
        "project_id": "X",
        "query": """
        SELECT
            planz_projects.title AS project_title,
            planz_clients.company_name AS client_name,
            planz_clients.currency_symbol,
            planz_project_status.key_name AS status_key_name,
            planz_project_status.title_language_key,
            planz_project_status.title AS status_title,
            planz_project_status.icon AS status_icon,
            IFNULL(total_points_table.total_points, 0) AS total_points,
            IFNULL(completed_points_table.completed_points, 0) AS completed_points,
        (IFNULL(completed_points_table.completed_points, 0) / IFNULL(total_points_table.total_points, 1)) * 100 AS completion_percentage
        FROM
            planz_projects
        LEFT JOIN planz_clients ON planz_clients.id = planz_projects.client_id
        LEFT JOIN planz_project_status ON planz_project_status.id = planz_projects.status_id
        LEFT JOIN (
            SELECT project_id, SUM(points) AS total_points
            FROM planz_tasks
            WHERE deleted = 0
            GROUP BY project_id
        ) AS total_points_table ON total_points_table.project_id = planz_projects.id
        LEFT JOIN (
            SELECT project_id, SUM(points) AS completed_points
            FROM planz_tasks
            WHERE deleted = 0 AND status_id = 3 -- Giả sử '3' chỉ trạng thái công việc đã hoàn thành
            GROUP BY project_id
        ) AS completed_points_table ON completed_points_table.project_id = planz_projects.id
        WHERE
            planz_projects.deleted = 0
            AND planz_projects.id = X;
        """
    },
    {
        "input": "Check deadline | start date of the event",
        "project_id": "X",
        "query": "SELECT start_date, deadline FROM planz_projects WHERE id = X;",
    },
    {
        "input": "Check title | name of the event",
        "project_id": "X",
        "query": "SELECT title FROM planz_projects WHERE id = X;",
    },
    {
        "input": "Participants in this event",
        "project_id": "X",
        "query": """
        SELECT DISTINCT u.first_name, u.last_name FROM planz_users u JOIN planz_tasks t ON u.id = t.assigned_to WHERE t.project_id = X;
        """
    }
]
