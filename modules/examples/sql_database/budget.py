examples = [
    {
        "input": "Check the budget of ABC | Is ABC overbudget?",
        "project_id": "X",
        "query": """
        -- Define the partial budget category name
        WITH partial_name AS (
            SELECT '%%ABC%%' AS partial_name
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
            CASE
                WHEN COALESCE(e.total_expenses, 0) > b.budget THEN 'Overbudget'
                ELSE 'Within Budget'
            END AS status
        FROM
            matched_budgets b
            LEFT JOIN expenses e ON b.budget_id = e.budget_id
        
        UNION
        
        -- Check if no budget category matches the partial name
        SELECT
            'No matching budget category' AS title,
            NULL AS budget,
            NULL AS total_expenses,
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
        "input": "Check all expense/budget category",
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
