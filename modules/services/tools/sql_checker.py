from typing import Type
from typing import Any

from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool
from langchain.agents.agent import AgentExecutor
from langchain_community.agent_toolkits import create_sql_agent
from langchain.chains.llm import LLMChain
from modules.prompts.zero_shot_prompts import ANSWER_FILTER_PROMPT_TEMPLATE

from modules.services.tools.specific_task_checker import SpecificTaskChecker


class SQLInput(BaseModel):
    input: str = Field(description="the original user input")
    project_id: str = Field(description="The ID of the project in the database")
    workspace_link: str = Field(description="The entire original workspace link")
    user_id: int = Field(description="The user's ID for personal task checks")


class SQLChecker(BaseTool):
    name = "sql_checker"
    description = "Tool for querying and retrieving information from the database"
    args_schema: Type[BaseModel] = SQLInput
    sql_agent: AgentExecutor
    answer_filter: LLMChain
    return_direct = True

    def __init__(self, db: Any, llm: Any, prompt: Any):
        super(SQLChecker, self).__init__(
            sql_agent=create_sql_agent(
                llm=llm,
                db=db,
                extra_tools=[SpecificTaskChecker(db=db, llm=llm)],
                prompt=prompt,
                agent_type="openai-tools",
                verbose=True,
            ),
            answer_filter=LLMChain(
                prompt=ANSWER_FILTER_PROMPT_TEMPLATE,
                llm=llm,
                verbose=True)
        )

    def _run(self, input: str, project_id: str, workspace_link: str, user_id: int):
        answer = self.sql_agent.invoke(
            {"input": input, "project_id": project_id, "user_id": user_id, "workspace_link": workspace_link})
        filtered_answer = self.answer_filter.invoke({"input": answer["output"]})
        return filtered_answer["text"]

    def _arun(self, project_id: int, input_name: str) -> None:
        raise NotImplementedError("This tool does not support async.")
