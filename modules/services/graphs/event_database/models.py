import operator
from enum import Enum
from typing import Annotated
from typing import Any, List, Optional

from pydantic import BaseModel, Field, validator
from typing_extensions import TypedDict


class Query(BaseModel):
    statement: str = Field(description="SQL query statement")
    reasoning: str = Field(description="Reasoning behind the query definition")
    is_valid: bool = Field(True, description="Indicates if the statement is syntactically valid")
    result: List[Any] = Field("", description="Query result")
    error: str = Field("", description="Error message if exists")

    @property
    def error_info(self) -> str:
        """Returns formatted error information."""
        return (
            f"Failed SQL query:\n{self.statement}\n\n"
            f"Reasoning:\n{self.reasoning}\n\n"
            f"Error: {self.error}"
        )

class QuestionType(Enum):
    GENERAL_REQUEST = "general_request"
    BUDGET_REQUEST = "budget_request"
    TASK_REQUEST = "task_request"
    MILESTONE_REQUEST = "milestone_request"
    NON_PROJECT = "non_project"


class ClassificationOutput(BaseModel):
    question_type: QuestionType
    confidence: float = Field(description="Classification confidence between 0 and 1")
    requires_clarification: bool = Field(
        description="Indicates if the query is unclear and needs further clarification")
    suggested_clarification: str = Field(
        description="A suggested clarifying question if clarification is needed; otherwise, empty")
    answer: str = Field(
        description="A response to be used for non-project queries (e.g., greetings or capability inquiries). If not applicable, leave empty.")

    @validator('question_type', pre=True)
    def normalize_question_type(cls, value):
        if isinstance(value, str):
            return value.lower()
        return value


class QueryResponse(BaseModel):
    """Structure for query generation response."""
    statement: str = Field(description="SQL query statement")
    reasoning: str = Field(description="Query design reasoning")


class SQLState(TypedDict):
    current_question: str
    project_id: int
    user_id: int
    workspace_link: str
    max_attempts: int
    attempts: int
    current_query: Optional[Query]
    error_message: Optional[str]
    tables_info: Optional[str]
    answer: str
    history_context: Optional[str]
    context_window: int
    requires_clarification: bool
    suggested_clarification: str
    question_type: Optional[QuestionType]


class SchemaRelevance(BaseModel):
    """Structure for schema relevance results"""
    relevant_tables: List[str] = Field(description="List of relevant database tables")
    reasoning: str = Field(description="Reasoning for the relevance determination")
