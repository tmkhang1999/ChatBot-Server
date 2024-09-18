from langchain_community.utilities import SQLDatabase
import ast


def report(project_id: str, db: SQLDatabase):
    # Queries stored in a dictionary
    queries = {
        "new_task": (
            f"SELECT CAST(COUNT(*) AS INT) AS total_new_tasks FROM planz_tasks "
            f"WHERE project_id = {project_id} AND created_date >= (CURRENT_DATE() - INTERVAL 7 DAY)"
        ),
        "done_task": (
            f"SELECT COUNT(*) AS total_done_tasks FROM planz_tasks "
            f"WHERE status_id=3 AND project_id={project_id} AND status_changed_at >= (CURRENT_DATE() - INTERVAL 7 DAY)"
        ),
        "in_progress_task": (
            f"SELECT COUNT(*) AS total_in_progress_tasks FROM planz_tasks "
            f"WHERE status_id=2 AND project_id={project_id} AND status_changed_at >= (CURRENT_DATE() - INTERVAL 7 DAY)"
        ),
        "late_task": (
            f"SELECT COUNT(*) as total_late_tasks FROM ( "
            f"SELECT id, title, deadline FROM planz_tasks "
            f"WHERE deadline < NOW() AND deadline >= (CURRENT_DATE() - INTERVAL 7 DAY) "
            f"AND (status_id = 1 OR status_id = 2) AND project_id = {project_id} "
            f"UNION ALL "
            f"SELECT id, title, deadline FROM planz_tasks "
            f"WHERE status_changed_at > deadline "
            f"AND status_changed_at >= (CURRENT_DATE() - INTERVAL 7 DAY) "
            f"AND status_id = 3 AND project_id = {project_id} "
            f") AS miss_deadline_tasks"
        ),
        "expense": (
            f"SELECT COUNT(*) AS expense_count, SUM(amount) AS weekly_expenses "
            f"FROM planz_expenses WHERE project_id = {project_id} "
            f"AND expense_date >= (CURRENT_DATE() - INTERVAL 7 DAY)"
        ),
        "remaining_budget": (
            f"SELECT "
            f"(SELECT COALESCE(SUM(budget), 0) FROM planz_budgets WHERE project_id={project_id} and deleted=0) AS budget, "
            f"(SELECT SUM(amount) FROM planz_expenses WHERE project_id={project_id}) AS total_expense "
        )
    }

    results = {}
    for key, query in queries.items():
        value = ast.literal_eval(db.run(query))[0]
        results[key] = tuple(x if x is not None else 0 for x in value)

    # Format and print results
    result_str = (
        f"- {results['new_task'][0]} new tasks added.\n"
        f"- {results['done_task'][0]} tasks were marked as done.\n"
        f"- {results['in_progress_task'][0]} tasks were still in progress.\n"
        f"- {results['late_task'][0]} task did not meet its deadline.\n"
        f"- {results['expense'][0]} expenses ({results['expense'][1]}) were submitted.\n"
        f"- Remaining budget is {results['remaining_budget'][0] - results['remaining_budget'][1]}."
    )

    return result_str
