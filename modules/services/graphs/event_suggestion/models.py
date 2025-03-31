from typing import Dict, Any
from typing import Literal
from pydantic import BaseModel, Field
from datetime import datetime


class PlannerState(BaseModel):
    user_input: str
    query_type: str = None
    language: str = None
    event_details: Dict[str, Any] = None
    final_response: Dict[str, Any] = None


class QueryType(BaseModel):
    category: Literal["GENERAL", "EVENT_RELATED"] = Field(
        description="Given a user question choose to route it to general or event_related answer.",
    )
    language: str = Field(description="the language of the user input")


class EventDetails(BaseModel):
    purpose: str | None = Field(description="The exact purpose of the event")
    guests: str | None = Field(description="Exact number or range of guests")
    budget: str | None = Field(description="Exact budget amount or range")
    deadline: str | None = Field(description="Exact date or timing requirement until deadline")
    duration: str | None = Field(description="Exact duration of the event")
    location: str | None = Field(description="Exact location specified")
    theme: str | None = Field(description="Exact theme or styling specified")
    activities: str | None = Field(description="Exact activities or entertainment specified")