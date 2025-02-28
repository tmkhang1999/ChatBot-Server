general_examples = [
    {
      "input": "The overview of the event",
      "project_id": "X",
      "query": """
        SELECT 
          p.title AS project_title, 
          p.description, 
          p.start_date, 
          p.deadline, 
          (SELECT SUM(budget) FROM planz_budgets WHERE project_id = p.id) AS total_budget, 
          (SELECT SUM(amount) FROM planz_expenses WHERE project_id = p.id) AS total_expense, 
          (IFNULL(cpt.completed_points, 0) / IFNULL(tpt.total_points, 1)) * 100 AS progress 
        FROM planz_projects p 
        LEFT JOIN (
          SELECT project_id, SUM(points) AS total_points 
          FROM planz_tasks 
          WHERE deleted = 0 
          GROUP BY project_id
        ) AS tpt ON tpt.project_id = p.id 
        LEFT JOIN (
          SELECT project_id, SUM(points) AS completed_points 
          FROM planz_tasks 
          WHERE deleted = 0 AND status_id = 3 -- Assuming '3' indicates completed tasks 
          GROUP BY project_id
        ) AS cpt ON cpt.project_id = p.id 
        WHERE p.deleted = 0 AND p.id = X;
      """
    },
    {
      "input": "The progress of the event",
      "project_id": "X",
      "query": """
        SELECT 
          p.title AS project_title, 
          c.company_name AS client_name, 
          c.currency_symbol, 
          ps.key_name AS status_key_name, 
          ps.title_language_key, 
          ps.title AS status_title, 
          ps.icon AS status_icon, 
          IFNULL(tpt.total_points, 0) AS total_points, 
          IFNULL(cpt.completed_points, 0) AS completed_points, 
          (IFNULL(cpt.completed_points, 0) / IFNULL(tpt.total_points, 1)) * 100 AS completion_percentage 
        FROM planz_projects p 
        LEFT JOIN planz_clients c ON c.id = p.client_id 
        LEFT JOIN planz_project_status ps ON ps.id = p.status_id 
        LEFT JOIN (
          SELECT project_id, SUM(points) AS total_points 
          FROM planz_tasks 
          WHERE deleted = 0 
          GROUP BY project_id
        ) AS tpt ON tpt.project_id = p.id 
        LEFT JOIN (
          SELECT project_id, SUM(points) AS completed_points 
          FROM planz_tasks 
          WHERE deleted = 0 AND status_id = 3 
          GROUP BY project_id
        ) AS cpt ON cpt.project_id = p.id 
        WHERE p.deleted = 0 AND p.id = X;
      """
    },
    {
      "input": "Check deadline | start date of the event",
      "project_id": "X",
      "query": "SELECT start_date, deadline FROM planz_projects WHERE id = X;"
    },
    {
      "input": "Check title | name of the event",
      "project_id": "X",
      "query": "SELECT title FROM planz_projects WHERE id = X;"
    },
    {
      "input": "Participants in this event | Check the member roles",
      "project_id": "X",
      "query": """
        SELECT DISTINCT 
          u.first_name, 
          u.last_name, 
          COALESCE(r.title, 'No Role Assigned') AS role 
        FROM planz_tasks t 
        JOIN planz_users u ON t.assigned_to = u.id 
        LEFT JOIN planz_roles_in_project rp ON u.id = rp.user_id 
        LEFT JOIN planz_roles r ON rp.role_id = r.id 
        WHERE t.project_id = X;
      """
    },
    {
      "input": "What is the current status of the event?",
      "project_id": "X",
      "query": "SELECT status, status_id FROM planz_projects WHERE id = X;"
    }
]