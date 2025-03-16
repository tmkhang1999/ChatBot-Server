general_examples = [
    {
      "input": "Introduce this event",
      "project_id": "X",
      "query": """
          SELECT 
              p.title AS project_title,
              p.description,
              p.start_date,
              p.deadline,
              COALESCE(pb.total_budget, 0) AS total_budget,
              COALESCE(pe.total_expense, 0) AS total_expense,
              (COALESCE(cpt.completed_points, 0) / NULLIF(COALESCE(tpt.total_points, 0), 0)) * 100 AS progress
          FROM planz_projects p
          LEFT JOIN (SELECT project_id, SUM(budget) AS total_budget FROM planz_budgets GROUP BY project_id) pb ON pb.project_id = p.id
          LEFT JOIN (SELECT project_id, SUM(amount) AS total_expense FROM planz_expenses GROUP BY project_id) pe ON pe.project_id = p.id
          LEFT JOIN (SELECT project_id, SUM(points) AS total_points FROM planz_tasks WHERE deleted = 0 GROUP BY project_id) tpt ON tpt.project_id = p.id
          LEFT JOIN (SELECT project_id, SUM(points) AS completed_points FROM planz_tasks WHERE deleted = 0 AND status_id = 3 GROUP BY project_id) cpt ON cpt.project_id = p.id
          WHERE p.deleted = 0 AND p.id = X;
      """
    },
    {
      "input": "When is the deadline/start date of the event",
      "project_id": "X",
      "query": "SELECT start_date, deadline FROM planz_projects WHERE id = X;"
    },
    {
      "input": "What is the title/name of the event",
      "project_id": "X",
      "query": "SELECT title FROM planz_projects WHERE id = X;"
    },
    {
      "input": "Who is working on this event | List the participants",
      "project_id": "X",
      "query": """
        SELECT DISTINCT 
            COUNT (*) AS total_event_members,
            u.first_name, 
            u.last_name
        FROM planz_users u
        JOIN planz_tasks t ON u.id = t.assigned_to
        WHERE t.project_id = 'X'
      """
    },
    {
      "input": "List participants working on the events and their roles | Check the member roles",
      "project_id": "X",
      "query": """
        SELECT DISTINCT 
            COUNT (*) AS total_event_members,
            u.first_name, 
            u.last_name, 
            COALESCE(r.title, 'No Role Assigned') AS role
        FROM planz_users u
        JOIN planz_tasks t ON u.id = t.assigned_to
        LEFT JOIN planz_roles_in_project rp ON u.id = rp.user_id
        LEFT JOIN planz_roles r ON rp.role_id = r.id
        WHERE t.project_id = 'X'
      """
    }
]