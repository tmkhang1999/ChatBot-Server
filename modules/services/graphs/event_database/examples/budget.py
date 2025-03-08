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
            SELECT
        (SELECT SUM(budget) FROM planz_budgets WHERE project_id = X) AS total_budget,
        (SELECT SUM(amount) FROM planz_expenses WHERE project_id = X) AS total_expenses,
        (SELECT SUM(budget) FROM planz_budgets WHERE project_id = X) -
        (SELECT SUM(amount) FROM planz_expenses WHERE project_id = X) AS remaining_budget,
        COALESCE(
            (SELECT currency_symbol FROM planz_currency WHERE project_id = X LIMIT 1),
            (SELECT setting_value FROM planz_settings WHERE setting_name = 'currency_symbol')
        ) AS currency_symbol;
      """
    },
    {
      "input": "Can you provide a high-level summary of the budget status?",
      "project_id": "X",
      "query": """
          WITH totals AS (
              SELECT 
                  (SELECT SUM(budget) FROM planz_budgets WHERE project_id = 'X') AS total_budget,
                  (SELECT SUM(amount) FROM planz_expenses WHERE project_id = 'X') AS total_expenses
          ),
          category_breakdown AS (
              SELECT
                  b.title AS category,
                  SUM(e.amount) AS total_spent,
                  ROUND((SUM(e.amount) / (SELECT SUM(amount) FROM planz_expenses WHERE project_id = 'X')) * 100, 2) AS percentage_spent
              FROM planz_budgets b
              LEFT JOIN planz_expenses e ON b.id = e.budget_id
              WHERE b.project_id = 'X'
              GROUP BY b.title
          ),
          currency AS (
              SELECT
                  COALESCE(
                      (SELECT currency_symbol FROM planz_currency WHERE project_id = 'X' LIMIT 1),
                      (SELECT setting_value FROM planz_settings WHERE setting_name = 'currency_symbol')
                  ) AS currency_symbol
          )
          SELECT
              CONCAT('Total budget: ', c.currency_symbol, t.total_budget) AS total_budget_summary,
              CONCAT('Total expense: ', c.currency_symbol, t.total_expenses) AS total_expense_summary,
              CONCAT('Remaining budget: ', c.currency_symbol, (t.total_budget - t.total_expenses)) AS remaining_budget_summary,
              GROUP_CONCAT(
                  CONCAT(ROUND(cb.percentage_spent), '% of expense is for ', cb.category)
                  SEPARATOR '\n'
              ) AS category_expense_breakdown
          FROM totals t
          CROSS JOIN currency c
          LEFT JOIN category_breakdown cb ON 1=1
          GROUP BY t.total_budget, t.total_expenses;
      """
    },
    {
      "input": "How much budget is allocated to each category (e.g., venue, catering, marketing)?",
      "project_id": "X",
      "query": """
          WITH total_budget_cte AS (
            SELECT SUM(budget) AS total_budget
            FROM planz_budgets
            WHERE project_id = 'X'
        ),
        budget_summary AS (
            SELECT
              title AS category,
              budget,
              ROUND((budget / (SELECT total_budget FROM total_budget_cte)) * 100, 2) AS percentage_allocated
            FROM planz_budgets
            WHERE project_id = 'X'
        ),
        currency AS (
            SELECT
              COALESCE(
                (SELECT currency_symbol FROM planz_currency WHERE project_id = 'X' LIMIT 1),
                (SELECT setting_value FROM planz_settings WHERE setting_name = 'currency_symbol')
              ) AS currency_symbol
        )
        SELECT
          CONCAT(
            'Total budget: ', c.currency_symbol, t.total_budget, '\n',
            GROUP_CONCAT(
              CONCAT(bs.percentage_allocated, '% (', c.currency_symbol, bs.budget, ') for ', bs.category)
              SEPARATOR '\n'
            )
          ) AS budget_allocation_breakdown
        FROM budget_summary bs
        CROSS JOIN currency c
        CROSS JOIN total_budget_cte t;
      """
    },
    {
      "input": "Can you provide a breakdown of expenses by category?",
      "project_id": "X",
      "query": """
      WITH totals AS (
        SELECT
          SUM(amount) AS total_expenses
        FROM planz_expenses
        WHERE project_id = 'X'
      ),
      budget_expenses AS (
        SELECT
          b.id,
          b.title,
          b.budget,
          COALESCE(SUM(e.amount), 0) AS total_spent
        FROM planz_budgets b
        LEFT JOIN planz_expenses e ON b.id = e.budget_id
        WHERE b.project_id = 'X'
        GROUP BY b.id, b.title, b.budget
      ),
      expense_breakdown AS (
        SELECT
          title AS category,
          SUM(budget) AS allocated_budget,
          SUM(total_spent) AS total_spent,
          ROUND(
            (SUM(total_spent) / (SELECT SUM(amount) FROM planz_expenses WHERE project_id = 'X')) * 100,
            2
          ) AS percentage_spent,
          CASE
            WHEN SUM(total_spent) < SUM(budget) THEN 'under budget'
            WHEN SUM(total_spent) = SUM(budget) THEN 'at budget'
            WHEN SUM(total_spent) > SUM(budget) THEN 'over budget'
            ELSE 'no expenses'
          END AS budget_status
        FROM budget_expenses
        GROUP BY title
      ),
      currency AS (
        SELECT
          COALESCE(
            (SELECT currency_symbol FROM planz_currency WHERE project_id = 'X' LIMIT 1),
            (SELECT setting_value FROM planz_settings WHERE setting_name = 'currency_symbol')
          ) AS currency_symbol
      )
      SELECT 
          t.total_expenses,
          c.currency_symbol,
          eb.category,
          eb.percentage_spent,
          eb.total_spent,
          eb.budget_status
      FROM totals t
      CROSS JOIN currency c
      LEFT JOIN expense_breakdown eb ON 1=1;
      """
    },
    {
      "input": "What are the top 5 highest expenses for the event?",
      "project_id": "X",
      "query": """
        WITH budget_expenses AS (
          SELECT
            b.title AS title,
            COALESCE(SUM(e.amount), 0) AS total_spent
          FROM planz_budgets b
          LEFT JOIN planz_expenses e ON b.id = e.budget_id
          WHERE b.project_id = 'X'
          GROUP BY b.title
        ),
        currency AS (
          SELECT
            COALESCE(
              (SELECT currency_symbol FROM planz_currency WHERE project_id = 'X' LIMIT 1),
              (SELECT setting_value FROM planz_settings WHERE setting_name = 'currency_symbol')
            ) AS currency_symbol
        )
        SELECT 
          be.title,
          be.total_spent,
          c.currency_symbol
        FROM budget_expenses be
        CROSS JOIN currency c
        ORDER BY be.total_spent DESC
        LIMIT 5;
      """
    },
    {
      "input": "Can you list all expenses recorded in the last 7 days?",
      "project_id": "X",
      "query": """
          WITH expenses AS (
              SELECT
                  e.title AS expense_title,
                  e.amount AS expense_amount,
                  e.expense_date,
                  DATE_FORMAT(e.expense_date, '%d - %b - %Y') AS formatted_date,
                  b.title AS budget_title
              FROM planz_expenses e
              LEFT JOIN planz_budgets b ON e.budget_id = b.id
              WHERE e.project_id = 'X'
                AND e.expense_date >= CURDATE() - INTERVAL 7 DAY
          ),
          total AS (
              SELECT SUM(expense_amount) AS total_expense FROM expenses
          ),
          currency AS (
              SELECT
                COALESCE(
                  (SELECT currency_symbol FROM planz_currency WHERE project_id = 'X' LIMIT 1),
                  (SELECT setting_value FROM planz_settings WHERE setting_name = 'currency_symbol')
                ) AS currency_symbol
          )
          SELECT 
              CONCAT(c.currency_symbol, t.total_expense) AS total_expense,
              e.expense_title,
              e.budget_title,
              e.formatted_date AS expense_date,
              e.expense_amount
          FROM expenses e
          CROSS JOIN total t
          CROSS JOIN currency c;
      """
    },
    {
      "input": "Are there any categories where spending is exceeding the allocated budget?",
      "project_id": "X",
      "query": """
          WITH expense_summary AS (
            SELECT
              b.title AS category,
              b.budget AS allocated_budget,
              COALESCE(SUM(e.amount), 0) AS total_expenses,
              (b.budget - COALESCE(SUM(e.amount), 0)) AS available_amount
            FROM planz_budgets b
            LEFT JOIN planz_expenses e ON b.id = e.budget_id
            WHERE b.project_id = 'X'
            GROUP BY b.title, b.budget
            HAVING COALESCE(SUM(e.amount), 0) > b.budget
          ),
          expense_summary_with_row_num AS (
            SELECT
              ROW_NUMBER() OVER (ORDER BY total_expenses DESC) AS rn,
              category,
              allocated_budget,
              total_expenses,
              available_amount
            FROM expense_summary
          ),
          over_budget_count AS (
            SELECT COUNT(*) AS over_budget_categories
            FROM expense_summary
          ),
          currency AS (
            SELECT
              COALESCE(
                (SELECT currency_symbol FROM planz_currency WHERE project_id = 'X' LIMIT 1),
                (SELECT setting_value FROM planz_settings WHERE setting_name = 'currency_symbol')
              ) AS currency_symbol
          )
          SELECT
            CONCAT(
              'There are ', obc.over_budget_categories, ' categories where spending exceeds the allocated budget.' , '\n',
              GROUP_CONCAT(
                CONCAT(
                  esrn.rn, '. ', esrn.category, ':\n',
                  'Allocated budget: ', c.currency_symbol, esrn.allocated_budget, '\n',
                  'Expenses: ', c.currency_symbol, esrn.total_expenses, '\n',
                  'Available: ', c.currency_symbol, esrn.available_amount
                )
                SEPARATOR '\n\n'
              )
            ) AS over_budget_summary
          FROM over_budget_count obc
          CROSS JOIN currency c
          LEFT JOIN expense_summary_with_row_num esrn ON 1 = 1
          GROUP BY obc.over_budget_categories;
      """
    }
]