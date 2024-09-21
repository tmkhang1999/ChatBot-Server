import ast
from typing import Any, List, Tuple, Type

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.pydantic_v1 import BaseModel, Field, conint
from langchain.tools import BaseTool
from langchain_community.utilities import SQLDatabase

# Define the template as a constant at the top for clarity
task_checker_template = """
As a name verification system, your task is to evaluate an input name against a predefined list of valid names.
The input name can be the first name or the last name. Your response should follow these guidelines:
- If the name is correct, return its full name ('first_name', 'last_name') from the list.
- If the name does not exist in the list, just return None.
- If the input is a misspelling or close to a name from the list, return its full correct name ('first_name', 'last_name').

Here are some examples:

User: 'abc'
Names: [('abc', 'xyz')]
AI: ('abc', 'xyz')

User: 'xyz'
Names: [('abc', 'xyz'), ('qwe', 'mnl')]
AI: ('abc', 'xyz')

User: 'acb'
Names: [('abc', 'xyz'), ('qwe', 'mnl')]
AI: ('abc', 'xyz')

User: '123'
Names: [('abc', 'xyz'), ('qwe', 'mnl')]
AI: None

User: {input_name}
Names: {names}
AI: """

task_checker_prompt_template = PromptTemplate(
    input_variables=["input_name", "names"],
    template=task_checker_template
)


class CheckerInput(BaseModel):
    project_id: int = Field(description="The project ID the person is working on")
    input_name: str = Field(
        description="Name of the specific person to check tasks for, OR 'me' for the user himself, OR 'all' for everyone.")
    task_status: conint(ge=0, le=4) = Field(
        description=(
            "The status of tasks to check, the value should be:\n"
            "0: all tasks\n"
            "1: to-do tasks\n"
            "2: in-progress tasks\n"
            "3: done/completed tasks\n"
            "4: late tasks"
        )
    )
    workspace_link: str = Field(description="The entire original workspace link")
    user_id: int = Field(description="The user's ID for personal task checks")


class SpecificTaskChecker(BaseTool):
    name = "specific_task_checker"
    description = (
        "Tool for checking tasks assigned to a specific person, everyone, or the user."
    )
    args_schema: Type[BaseModel] = CheckerInput
    db: SQLDatabase
    name_checker_chain: LLMChain

    def __init__(self, db: Any, llm: Any):
        super(SpecificTaskChecker, self).__init__(
            db=db, name_checker_chain=LLMChain(llm=llm, prompt=task_checker_prompt_template, verbose=True))

    def check_name(self, input_name: str, names: List[Tuple[str, str]]) -> str:
        # Prepare names list for the prompt
        names_str = str(names)
        answer = self.name_checker_chain.invoke({"input_name": input_name, "names": names_str})
        return answer["text"]

    def _run(self, project_id: int, input_name: str, task_status: int, workspace_link: str, user_id: int):
        if input_name.lower() == "me" or input_name.lower() == str(user_id):
            return self.check_tasks_for_myself(user_id, project_id, task_status, workspace_link)

        if input_name.lower() == "all":
            return self.check_tasks_for_all_user(project_id, task_status, workspace_link)

        # Fetch users' names associated with the project
        query = f"""
           SELECT DISTINCT u.first_name, u.last_name
           FROM planz_users u
           JOIN planz_tasks t ON u.id = t.assigned_to
           WHERE t.project_id = {project_id}
           """
        names_list = self.db.run(query)
        closest_name = self.check_name(input_name, names_list)
        print(closest_name)

        if closest_name == "None":
            return f"I couldn't find that name in this event. Please choose available names: {names_list}"

        # Parse the closest name back to a tuple
        first_name, last_name = ast.literal_eval(closest_name)

        if task_status == 0:
            task_query = f"""
              SELECT id, title, created_date, deadline, description, CONCAT('{workspace_link}', id) AS task_link FROM planz_tasks
              WHERE (assigned_to = (
                  SELECT id FROM planz_users
                  WHERE first_name = '{first_name}' AND last_name = '{last_name}'
                  LIMIT 1
              ) OR FIND_IN_SET((
                  SELECT id FROM planz_users
                  WHERE first_name = '{first_name}' AND last_name = '{last_name}'
                  LIMIT 1
              ), collaborators)
              )
              AND project_id = {project_id} AND deleted=0 ORDER BY;
              """
        elif task_status == 4:
            task_query = f"""
            SELECT id, title, created_date, deadline, description, CONCAT('{workspace_link}', id) AS task_link
            FROM (
                SELECT id, title, created_date, deadline, description FROM planz_tasks
                WHERE deadline < NOW()
                AND (status_id = 1 OR status_id = 2)
                AND project_id = {project_id}
                AND deleted=0
                AND (assigned_to = (
                    SELECT id FROM planz_users
                    WHERE first_name = '{first_name}' AND last_name = '{last_name}'
                    LIMIT 1
                ) OR FIND_IN_SET((
                    SELECT id FROM planz_users
                    WHERE first_name = '{first_name}' AND last_name = '{last_name}'
                    LIMIT 1
                ), collaborators))

                UNION ALL

                SELECT id, title, created_date, deadline, description FROM planz_tasks
                WHERE status_changed_at > deadline
                AND status_id = 3
                AND project_id = {project_id}
                AND deleted=0
                AND (assigned_to = (
                    SELECT id FROM planz_users
                    WHERE first_name = '{first_name}' AND last_name = '{last_name}'
                    LIMIT 1
                ) OR FIND_IN_SET((
                    SELECT id FROM planz_users
                    WHERE first_name = '{first_name}' AND last_name = '{last_name}'
                    LIMIT 1
                ), collaborators))
            ) AS user_late_tasks;
            """
        else:
            task_query = f"""
              SELECT id, title, created_date, deadline, description, CONCAT('{workspace_link}', id) AS task_link FROM planz_tasks
              WHERE (assigned_to = (
                  SELECT id FROM planz_users
                  WHERE first_name = '{first_name}' AND last_name = '{last_name}'
                  LIMIT 1
              ) OR FIND_IN_SET((
                  SELECT id FROM planz_users
                  WHERE first_name = '{first_name}' AND last_name = '{last_name}'
                  LIMIT 1
              ), collaborators)
              )
              AND project_id = {project_id} AND status_id={task_status} AND deleted=0;
            """
        tasks = self.db.run(task_query)
        return tasks

    def check_tasks_for_all_user(self, project_id: int, task_status: int, workspace_link: str):
        if task_status == 0:
            task_query = f"SELECT id, title, created_date, deadline, description, CONCAT('{workspace_link}', id) AS task_link FROM planz_tasks WHERE project_id={project_id} AND deleted=0;"
        elif task_status == 4:
            task_query = f"""
            SELECT id, title, created_date, deadline, description, CONCAT('{workspace_link}', id) AS task_link
            FROM (
                SELECT id, title, created_date, deadline, description FROM planz_tasks
                WHERE deadline < NOW()
                AND (status_id = 1 OR status_id = 2)
                AND deleted=0
                AND project_id = {project_id}

                UNION ALL

                SELECT id, title, created_date, deadline, description FROM planz_tasks
                WHERE status_changed_at > deadline
                AND status_id = 3
                AND deleted=0
                AND project_id = {project_id}
            ) AS miss_deadline_tasks
            """
        else:
            task_query = f"SELECT id, title, created_date, deadline, description, CONCAT('{workspace_link}', id) AS task_link FROM planz_tasks WHERE status_id={task_status} AND project_id={project_id} AND deleted=0;"
        tasks = self.db.run(task_query)
        return tasks

    def check_tasks_for_myself(self, user_id: int, project_id: int, task_status: int, workspace_link: str):
        if task_status == 0:
            task_query = f"""
                SELECT id, title, created_date, deadline, description, CONCAT('{workspace_link}', id) AS task_link
                FROM planz_tasks
                WHERE project_id = {project_id} AND (
                    assigned_to = {user_id}
                    OR FIND_IN_SET({user_id}, collaborators)
                ) AND deleted=0;
            """
        elif task_status == 4:
            task_query = f"""
                SELECT id, title, created_date, deadline, description, CONCAT('{workspace_link}', id) AS task_link
                FROM (
                    SELECT id, title, created_date, deadline, description FROM planz_tasks
                    WHERE deadline < NOW()
                    AND (status_id = 1 OR status_id = 2)
                    AND project_id = {project_id}
                    AND deleted=0
                    AND (assigned_to = {user_id} OR FIND_IN_SET({user_id}, collaborators))

                    UNION ALL

                    SELECT id, title, created_date, deadline, description FROM planz_tasks
                    WHERE status_changed_at > deadline
                    AND status_id = 3
                    AND project_id = {project_id}
                    AND deleted=0
                    AND (assigned_to = {user_id} OR FIND_IN_SET({user_id}, collaborators))
                ) AS user_late_tasks;
            """
        else:
            task_query = f"""
                SELECT id, title, created_date, deadline, description, CONCAT('{workspace_link}', id) AS task_link
                FROM planz_tasks
                WHERE project_id = {project_id} AND status_id={task_status}
                AND (assigned_to = {user_id} OR FIND_IN_SET({user_id}, collaborators))
                AND deleted=0;
            """
        tasks = self.db.run(task_query)
        return tasks

    def _arun(self, project_id: int, input_name: str) -> None:
        raise NotImplementedError("This tool does not support async.")