examples = [
    {
        "input": "Check the budget of ABC | Is ABC overbudget?",
        "project_id": "X",
        "query": """
        -- Define the partial budget category name
        WITH partial_name AS (
            SELECT '%%ABC%%' AS partial_name
        ),

        -- Get currency symbol
        currency_info AS (
            SELECT COALESCE(
                (SELECT currency_symbol FROM planz_currency WHERE project_id = X LIMIT 1),
                (SELECT setting_value FROM planz_settings WHERE setting_name = 'currency_symbol')
            ) AS currency_symbol
        ),

        -- Check if the partial name exists in the budget categories
        matched_budgets AS (
            SELECT
                id AS budget_id,
                title,
                budget
            FROM
                planz_budgets
            WHERE
                project_id = X
                AND title LIKE (SELECT partial_name FROM partial_name)
        ),

        -- Calculate total expenses for matched budget categories
        expenses AS (
            SELECT
                budget_id,
                SUM(amount) AS total_expenses
            FROM
                planz_expenses
            WHERE
                project_id = X
            GROUP BY
                budget_id
        )

        -- Determine if the matched budget categories are overbudget
        SELECT
            b.title,
            b.budget,
            COALESCE(e.total_expenses, 0) AS total_expenses,
            c.currency_symbol,
            CASE
                WHEN COALESCE(e.total_expenses, 0) > b.budget THEN 'Overbudget'
                ELSE 'Within Budget'
            END AS status
        FROM
            matched_budgets b
            LEFT JOIN expenses e ON b.budget_id = e.budget_id
            CROSS JOIN currency_info c

        UNION

        -- Check if no budget category matches the partial name
        SELECT
            'No matching budget category' AS title,
            NULL AS budget,
            NULL AS total_expenses,
            (SELECT currency_symbol FROM currency_info) AS currency_symbol,
            'This budget category does not exist' AS status
        WHERE
            NOT EXISTS (
                SELECT 1
                FROM matched_budgets
            );
        """,
    },
    {
        "input": "What is my total budget (Combination of all budget categories)",
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
        """,
    },
    {
        "input": "What is my total expense? (Combination of all expenses)",
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
        """,
    },
    {
        "input": "Which is the largest category budget?",
        "project_id": "X",
        "query": """
        SELECT
            title,
            budget,
            COALESCE(
                (SELECT currency_symbol FROM planz_currency WHERE project_id = X LIMIT 1),
                (SELECT setting_value FROM planz_settings WHERE setting_name = 'currency_symbol')
            ) AS currency_symbol
        FROM planz_budgets
        WHERE project_id = X
        ORDER BY budget DESC
        LIMIT 1;
        """,
    },
    {
        "input": "Which one is the biggest expense?",
        "project_id": "X",
        "query": """
        WITH expense_totals AS (
            SELECT
                budget_id,
                SUM(amount) AS total_expense,
                MAX(amount) AS biggest_expense
            FROM planz_expenses
            WHERE project_id = X
            GROUP BY budget_id
        ),
        currency_info AS (
            SELECT COALESCE(
                (SELECT currency_symbol FROM planz_currency WHERE project_id = X LIMIT 1),
                (SELECT setting_value FROM planz_settings WHERE setting_name = 'currency_symbol')
            ) AS currency_symbol
        )
        SELECT
            b.title,
            e.total_expense,
            e.biggest_expense,
            c.currency_symbol
        FROM expense_totals e
        JOIN planz_budgets b ON e.budget_id = b.id
        CROSS JOIN currency_info c
        ORDER BY e.total_expense DESC
        LIMIT 1;
        """,
    },
    {
        "input": "What are my top 3 expenses?",
        "project_id": "X",
        "query": """
        WITH currency_info AS (
            SELECT COALESCE(
                (SELECT currency_symbol FROM planz_currency WHERE project_id = X LIMIT 1),
                (SELECT setting_value FROM planz_settings WHERE setting_name = 'currency_symbol')
            ) AS currency_symbol
        )
        SELECT
            e.title,
            e.amount AS expense_amount,
            c.currency_symbol
        FROM planz_expenses e
        CROSS JOIN currency_info c
        WHERE e.project_id = X
        ORDER BY e.amount DESC
        LIMIT 3;
        """,
    },
    {
        "input": "Check all/each expense/budget category",
        "project_id": "X",
        "query": """
        WITH expenses AS (
            SELECT budget_id, SUM(amount) AS total_expenses
            FROM planz_expenses
            WHERE project_id = X
            GROUP BY budget_id
        ),
        budgets AS (
            SELECT id AS budget_id, title, budget
            FROM planz_budgets
            WHERE project_id = X
        ),
        currency_info AS (
            SELECT COALESCE(
                (SELECT currency_symbol FROM planz_currency WHERE project_id = X LIMIT 1),
                (SELECT setting_value FROM planz_settings WHERE setting_name = 'currency_symbol')
            ) AS currency_symbol
        )
        SELECT
            b.title,
            b.budget,
            e.total_expenses,
            c.currency_symbol,
            CASE
                WHEN e.total_expenses > b.budget THEN 'Over Budget'
                ELSE 'Within Budget'
            END AS status
        FROM
            budgets b
            LEFT JOIN expenses e ON b.budget_id = e.budget_id
            CROSS JOIN currency_info c
        ORDER BY
            b.title;
        """,
    },
    {
        "input": "what percentage of budgets are available for this event? | What is the remaining budget?",
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
        currency_info AS (
            SELECT COALESCE(
                (SELECT currency_symbol FROM planz_currency WHERE project_id = X LIMIT 1),
                (SELECT setting_value FROM planz_settings WHERE setting_name = 'currency_symbol')
            ) AS currency_symbol
        )
        SELECT
            t.total_budget,
            t.total_expenses,
            (t.total_budget - t.total_expenses) AS available_budget,
            ROUND(((t.total_budget - t.total_expenses) / t.total_budget) * 100, 2) AS available_budget_percentage,
            c.currency_symbol
        FROM totals t
        CROSS JOIN currency_info c;
        """,
    },
]
