budget_examples = [
    {
      "input": "What is the total budget allocated for the event?",
      "project_id": "X",
      "query": """
        SELECT 
          SUM(budget) AS total_budget, 
          COALESCE(
            (SELECT currency_symbol FROM planz_currency WHERE project_id = X LIMIT 1),
            (SELECT setting_value FROM planz_settings WHERE setting_name = 'currency_symbol')
          ) AS currency_symbol 
        FROM planz_budgets 
        WHERE project_id = X;
      """
    },
    {
      "input": "How much of the budget has been spent so far?",
      "project_id": "X",
      "query": """
        SELECT 
          SUM(amount) AS total_expense, 
          COALESCE(
            (SELECT currency_symbol FROM planz_currency WHERE project_id = X LIMIT 1),
            (SELECT setting_value FROM planz_settings WHERE setting_name = 'currency_symbol')
          ) AS currency_symbol 
        FROM planz_expenses 
        WHERE project_id = X;
      """
    },
    {
      "input": "What percentage of the budget remains?",
      "project_id": "X",
      "query": """
        WITH totals AS (
          SELECT 
            SUM(b.budget) AS total_budget, 
            SUM(e.amount) AS total_expenses 
          FROM planz_budgets b 
          LEFT JOIN planz_expenses e ON b.id = e.budget_id 
          WHERE b.project_id = X
        ) 
        SELECT 
          t.total_budget, 
          t.total_expenses, 
          ROUND(((t.total_budget - t.total_expenses) / t.total_budget) * 100, 2) AS remaining_budget_percentage 
        FROM totals t;
      """
    },
    {
      "input": "Can you provide a high-level summary of the budget status?",
      "project_id": "X",
      "query": """
        WITH totals AS (
          SELECT 
            SUM(b.budget) AS total_budget, 
            SUM(e.amount) AS total_expenses 
          FROM planz_budgets b 
          LEFT JOIN planz_expenses e ON b.id = e.budget_id 
          WHERE b.project_id = X
        ), 
        category_breakdown AS (
          SELECT 
            b.title AS category, 
            SUM(e.amount) AS total_spent, 
            ROUND((SUM(e.amount) / (SELECT SUM(amount) FROM planz_expenses WHERE project_id = X)) * 100, 2) AS percentage_spent 
          FROM planz_budgets b 
          LEFT JOIN planz_expenses e ON b.id = e.budget_id 
          WHERE b.project_id = X 
          GROUP BY b.title
        ) 
        SELECT 
          t.total_budget, 
          t.total_expenses, 
          (t.total_budget - t.total_expenses) AS remaining_budget, 
          c.category, 
          c.total_spent, 
          c.percentage_spent 
        FROM totals t 
        LEFT JOIN category_breakdown c ON 1=1;
      """
    },
    {
      "input": "How much budget is allocated to each category (e.g., venue, catering, marketing)?",
      "project_id": "X",
      "query": """
        SELECT 
          title AS category, 
          budget, 
          ROUND((budget / (SELECT SUM(budget) FROM planz_budgets WHERE project_id = X)) * 100, 2) AS percentage_allocated, 
          COALESCE(
            (SELECT currency_symbol FROM planz_currency WHERE project_id = X LIMIT 1),
            (SELECT setting_value FROM planz_settings WHERE setting_name = 'currency_symbol')
          ) AS currency_symbol 
        FROM planz_budgets 
        WHERE project_id = X;
      """
    },
    {
      "input": "Can you provide a breakdown of expenses by category?",
      "project_id": "X",
      "query": """
        SELECT 
          b.title AS category, 
          SUM(e.amount) AS total_expense, 
          ROUND((SUM(e.amount) / (SELECT SUM(amount) FROM planz_expenses WHERE project_id = X)) * 100, 2) AS percentage_of_expense, 
          COALESCE(
            (SELECT currency_symbol FROM planz_currency WHERE project_id = X LIMIT 1),
            (SELECT setting_value FROM planz_settings WHERE setting_name = 'currency_symbol')
          ) AS currency_symbol 
        FROM planz_budgets b 
        LEFT JOIN planz_expenses e ON b.id = e.budget_id 
        WHERE b.project_id = X 
        GROUP BY b.title;
      """
    },
    {
      "input": "What are the top 5 highest expenses for the event?",
      "project_id": "X",
      "query": """
        SELECT 
          title, 
          amount AS expense_amount, 
          COALESCE(
            (SELECT currency_symbol FROM planz_currency WHERE project_id = X LIMIT 1),
            (SELECT setting_value FROM planz_settings WHERE setting_name = 'currency_symbol')
          ) AS currency_symbol 
        FROM planz_expenses 
        WHERE project_id = X 
        ORDER BY amount DESC 
        LIMIT 5;
      """
    },
    {
      "input": "Can you list all expenses recorded in the last 7 days?",
      "project_id": "X",
      "query": """
        SELECT 
          title, 
          amount AS expense_amount, 
          date_incurred, 
          COALESCE(
            (SELECT currency_symbol FROM planz_currency WHERE project_id = X LIMIT 1),
            (SELECT setting_value FROM planz_settings WHERE setting_name = 'currency_symbol')
          ) AS currency_symbol 
        FROM planz_expenses 
        WHERE project_id = X 
        AND date_incurred >= CURDATE() - INTERVAL 7 DAY 
        ORDER BY date_incurred DESC;
      """
    },
    {
      "input": "Are there any categories where spending is exceeding the allocated budget?",
      "project_id": "X",
      "query": """
        WITH expense_summary AS (
          SELECT 
            budget_id, 
            SUM(amount) AS total_expenses 
          FROM planz_expenses 
          WHERE project_id = X 
          GROUP BY budget_id
        ) 
        SELECT 
          b.title, 
          b.budget, 
          COALESCE(e.total_expenses, 0) AS total_expenses, 
          (b.budget - COALESCE(e.total_expenses, 0)) AS remaining_amount, 
          CASE 
            WHEN COALESCE(e.total_expenses, 0) > b.budget THEN 'Over Budget' 
            ELSE 'Within Budget' 
          END AS status 
        FROM planz_budgets b 
        LEFT JOIN expense_summary e ON b.id = e.budget_id 
        WHERE b.project_id = X 
        AND COALESCE(e.total_expenses, 0) > b.budget;
      """
    }
]