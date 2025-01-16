import operator
from enum import Enum
from typing import List, Optional, Annotated

from pydantic import BaseModel, Field
from typing_extensions import TypedDict


class Query(BaseModel):
    statement: str = Field(description="SQL query statement")
    reasoning: str = Field(description="Reasoning behind the query definition")
    is_valid: bool = Field(True, description="Indicates if the statement is syntactically valid")
    result: str = Field("", description="Query result")
    error: str = Field("", description="Error message if exists")

    @property
    def info(self) -> str:
        """Returns formatted successful query information."""
        return (
            f"SQL query:\n{self.statement}\n\n"
            f"Reasoning:\n{self.reasoning}\n\n"
            f"Result:\n{self.result}"
        )

    @property
    def error_info(self) -> str:
        """Returns formatted error information."""
        return (
            f"Failed SQL query:\n{self.statement}\n\n"
            f"Reasoning:\n{self.reasoning}\n\n"
            f"Error: {self.error}"
        )


class QuestionType(Enum):
    OUT_OF_CONTEXT = "out_of_context"
    GREETING = "greeting"
    ASK_ABOUT_CAPABILITIES = "ask_about_capabilities"
    UNCLEAR = "unclear"
    GENERAL_REQUEST = "general_request"
    BUDGET_REQUEST = "budget_request"
    TASK_REQUEST = "task_request"
    MILESTONE_REQUEST = "milestone_request"


class ClassificationOutput(BaseModel):
    question_type: QuestionType
    answer: str


class QueryResponse(BaseModel):
    """Structure for query generation response."""
    statement: str = Field(description="SQL query statement")
    reasoning: str = Field(description="Query design reasoning")


class SQLState(TypedDict):
    question: str
    question_type: QuestionType
    project_id: int
    max_attempts: int
    user_id: int
    workspace_link: str
    attempts: Annotated[int, operator.add]
    query: Optional[Query]
    error_message: Optional[str]
    tables_info: Optional[str]
    answer: str
    messages: list[str]


class SchemaRelevance(BaseModel):
    """Structure for schema relevance results"""
    relevant_tables: List[str] = Field(description="List of relevant database tables")
    reasoning: str = Field(description="Reasoning for the relevance determination")
