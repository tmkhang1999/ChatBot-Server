budget_examples = [
    {
      "input": "What is the total budget allocated for the event?",
      "project_id": "X",
      "query": """
        SELECT
          COALESCE(SUM(budget), 0) AS total_budget,
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
          COALESCE(SUM(amount), 0) AS total_expense,
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
              b.total_budget,
              COALESCE(e.total_expenses, 0) AS total_expenses,
              b.total_budget - COALESCE(e.total_expenses, 0) AS remaining_budget,
              CASE
                  WHEN b.total_budget > 0
                  THEN ((b.total_budget - COALESCE(e.total_expenses, 0)) / b.total_budget) * 100
                  ELSE 0
              END AS remaining_percentage
          FROM
              (SELECT project_id, SUM(budget) AS total_budget FROM planz_budgets WHERE project_id = 348) b
          LEFT JOIN
              (SELECT project_id, SUM(amount) AS total_expenses FROM planz_expenses WHERE project_id = 348) e
              ON b.project_id = e.project_id;
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
                t.total_budget AS total_budget,
                t.total_expenses AS total_expenses,
                (t.total_budget - t.total_expenses) AS remaining_budget,
                c.currency_symbol AS currency_symbol,
                cb.category AS category,
                cb.percentage_spent AS percentage_spent
            FROM totals t
            CROSS JOIN currency c
            LEFT JOIN category_breakdown cb ON 1=1;
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
                t.total_budget AS total_budget,
                c.currency_symbol AS currency_symbol,
                bs.category AS category,
                bs.budget AS category_budget,
                bs.percentage_allocated AS percentage_allocated
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
        SELECT SUM(amount) AS total_expenses FROM planz_expenses WHERE project_id = 'X'
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
          eb.total_spent AS category_spent,
          eb.percentage_spent,
          eb.budget_status,
      FROM totals t
      CROSS JOIN currency c
      LEFT JOIN expense_breakdown eb ON 1=1;
      """
    },
    {
      "input": "Rank the expenses by category",
      "project_id": "X",
      "query": """
          WITH budget_expenses AS (
              SELECT
                  b.title AS title,
                  COALESCE(SUM(e.amount), 0) AS category_spent
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
              RANK() OVER (ORDER BY be.total_spent DESC) AS ranking,
              be.title,
              be.category_spent,
              c.currency_symbol
          FROM budget_expenses be
          CROSS JOIN currency c
          ORDER BY ranking;
      """
    },
    {
      "input": "What are the top 5 highest expenses for the event?",
      "project_id": "X",
      "query": """
          WITH expenses AS (
              SELECT
                  e.title AS expense_title,
                  e.amount AS expense_amount,
                  e.expense_date,
                  b.title AS budget_title
              FROM planz_expenses e
              LEFT JOIN planz_budgets b ON e.budget_id = b.id
              WHERE e.project_id = 'X'
          ),
          currency AS (
              SELECT COALESCE(
                      (SELECT currency_symbol FROM planz_currency WHERE project_id = 'X' LIMIT 1),
                      (SELECT setting_value FROM planz_settings WHERE setting_name = 'currency_symbol')
                    ) AS currency_symbol
          )
          SELECT
              c.currency_symbol,
              e.expense_title AS expense_purpose,
              e.budget_title AS budget_group,
              e.expense_date,
              e.expense_amount
          FROM expenses e
          CROSS JOIN currency c
          ORDER BY e.expense_amount DESC
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
              t.total_expense,
              c.currency_symbol,
              e.expense_title AS expense_purpose,
              e.budget_title AS budget_group,
              e.expense_date,
              e.expense_amount,
          FROM expenses e
          CROSS JOIN total t
          CROSS JOIN currency c
          ORDER BY e.expense_date DESC;
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
            expense_summary_with_rank AS (
                SELECT
                    RANK() OVER (ORDER BY total_expenses DESC) AS category_rank,
                    category,
                    allocated_budget,
                    total_expenses,
                    available_amount,
                    COUNT(*) OVER () AS over_budget_categories -- Calculate total count without a separate CTE
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
                eswr.over_budget_categories,
                c.currency_symbol,
                eswr.category_rank,
                eswr.category,
                eswr.allocated_budget,
                eswr.total_expenses AS expenses,
                eswr.available_amount
            FROM expense_summary_with_rank eswr
            CROSS JOIN currency c
            ORDER BY eswr.category_rank;
      """
    }
]