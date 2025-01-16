examples = [
    {
        "input": "Is ABC overbudget?",
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
                    WHERE project_id = X AND title = 'ABC'
                )
                SELECT
                    b.title,
                    b.budget,
                    e.total_expenses,
                    CASE
                        WHEN e.total_expenses > b.budget THEN 'Over Budget'
                        ELSE 'Within Budget'
                    END AS status
                FROM
                    budgets b
                    LEFT JOIN expenses e ON b.budget_id = e.budget_id
                ORDER BY
                    b.title;
                """,
    },
    {
        "input": "What is my total budget (Combination of all budget categories)",
        "project_id": "X",
        "query": "SELECT SUM(budget) AS total_budget FROM planz_budgets WHERE project_id = X;",
    },
    {
        "input": "What is my total expense so far? (Combination of all expenses)",
        "project_id": "X",
        "query": "SELECT SUM(amount) AS total_expense FROM planz_expenses WHERE project_id = X;",
    },
    {
        "input": "Which one is the biggest expense?",
        "project_id": "X",
        "query": """
        SELECT budget_id, SUM(amount) AS total_expense FROM planz_expenses
        WHERE project_id = X
        GROUP BY budget_id
        ORDER BY total_expense DESC
        LIMIT 1;
        """,
    },
    {
        "input": "What are my top 3 expenses?",
        "project_id": "X",
        "query": """
        SELECT budget_id, SUM(amount) AS total_expense
        FROM planz_expenses
        WHERE project_id = X
        GROUP BY budget_id
        ORDER BY total_expense DESC
        LIMIT 3; 
        """,
    },
    {
        "input": "Check all expense/budget category | What is the overall budget for the event |  Are we overspending in any category ",
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
        )
        SELECT
            b.title,
            b.budget,
            e.total_expenses,
            CASE
                WHEN e.total_expenses > b.budget THEN 'Over Budget'
                ELSE 'Within Budget'
            END AS status
        FROM
            budgets b
            LEFT JOIN expenses e ON b.budget_id = e.budget_id
        ORDER BY
            b.title;
        """,
    }
]
