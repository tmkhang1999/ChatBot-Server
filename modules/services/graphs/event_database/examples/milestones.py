milestone_examples = [
    {
      "input": "List milestones?",
      "project_id": "X",
      "query": "SELECT * FROM planz_milestones WHERE project_id = X;"
    },
    {
      "input": "How much progress has been made on each milestone?",
      "project_id": "X",
      "query": """
        SELECT 
          m.id AS milestone_id, 
          IFNULL(tt.total_tasks, 0) AS total_tasks, 
          IFNULL(ct.completed_tasks, 0) AS completed_tasks, 
          IFNULL((ct.completed_tasks / tt.total_tasks) * 100, 0) AS percentage_tasks_completed 
        FROM (
          SELECT * FROM planz_milestones 
          WHERE project_id = X AND deleted = 0
        ) m 
        LEFT JOIN (
          SELECT 
            milestone_id, 
            COUNT(id) AS total_tasks 
          FROM planz_tasks 
          WHERE deleted = 0 AND project_id = X 
          GROUP BY milestone_id
        ) tt ON tt.milestone_id = m.id 
        LEFT JOIN (
          SELECT 
            milestone_id, 
            COUNT(id) AS completed_tasks 
          FROM planz_tasks 
          WHERE deleted = 0 AND project_id = X AND status_id = 3 
          GROUP BY milestone_id
        ) ct ON ct.milestone_id = m.id;
      """
    },
    {
      "input": "Check milestone Y?",
      "project_id": "X",
      "query": "SELECT * FROM planz_milestones WHERE project_id = X AND id = Y;"
    },
    {
      "input": "Check tasks in milestone Y?",
      "project_id": "X",
      "query": "SELECT * FROM planz_tasks WHERE milestone_id = Y AND project_id = X;"
    },
    {
      "input": "List upcoming milestones",
      "project_id": "X",
      "query": """
        SELECT * FROM planz_milestones 
        WHERE project_id = X AND due_date >= CURDATE() 
        ORDER BY due_date ASC;
      """
    }
]