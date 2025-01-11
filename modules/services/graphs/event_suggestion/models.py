from typing import Dict, Any
from typing import Literal

from pydantic import BaseModel, Field


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
    purpose: str | None = Field(description="The main reason for the event, including relationships if mentioned")
    guests: int | None = Field(description="Estimated number of attendees")
    budget: str | None = Field(description="Estimated or stated budget")
    deadline: str | None = Field(description="When the event needs to be organized by")
    duration: str | None = Field(description="How long the event is expected to last")
    location: str | None = Field(description="Where the event will take place")
    theme: str | None = Field(description="Any specific theme or colors for decorations/styling")
    activities: str | None = Field(description="Planned activities or entertainment")
