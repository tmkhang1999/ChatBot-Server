from typing import Dict, List, Any, TypedDict
from typing import Literal

from pydantic import BaseModel, Field


class ScheduleUpdate(BaseModel):
    operation: Literal["update", "insert"] = Field(description="The operation to perform: update, add, or insert.")
    table: Literal["before_event_day", "on_event_day", "after_event_day"] = Field(
        description="The table needed to update")
    row_index: int = Field(
        description="The index of the row to update or insert. For the last row, the index must be -1")
    new_values: List[str] = Field(description="The values for the row (e.g., ['Task', 'Effort', 'Duration', 'Cost']).")


class ScheduleUpdateList(BaseModel):
    updates: List[ScheduleUpdate] = Field(description="List of schedule updates.")


# Define base models
class EventBudget(BaseModel):
    new_budget: str | None = Field(
        description="The suggested budget for the event. If no suggested budget is provided, leave it None")
    original_budget: str = Field(description="The original budget for the event")
    currency: str = Field(description="The currency of the budget, such as USD, VND, etc.")


class EventSummary(BaseModel):
    category: str = Field(description="The most suitable category for this event.")
    command: str = Field(description="A summary command for the event planner, including any budget suggestions.")


class ScheduleTables(BaseModel):
    before_event_day: List[List[str]] = Field(
        default_factory=lambda: [["Stages", "Effort (hours)", "Duration", "Cost"], ["Total", "0", "0", "0"]])
    on_event_day: List[List[str]] = Field(
        default_factory=lambda: [["Stages", "Effort (hours)", "Duration", "Cost"], ["Total", "0", "0", "0"]])
    after_event_day: List[List[str]] = Field(
        default_factory=lambda: [["Stages", "Effort (hours)", "Duration", "Cost"], ["Total", "0", "0", "0"]])


class ScheduleAdjustment(BaseModel):
    table: str = Field(description="The table to adjust: 'before_event_day', 'on_event_day', or 'after_event_day'")
    row_index: int = Field(description="The index of the row to adjust")
    column: str = Field(description="The column to adjust: 'Stages', 'Effort (hours)', 'Duration', or 'Cost'")
    new_value: Any = Field(description="The new value for the specified cell")


class ScheduleCheckResult(BaseModel):
    is_within_budget: bool = Field(description="Whether the current schedule is within budget")
    total_cost: float = Field(description="The total cost of the current schedule")
    adjustments: List[ScheduleAdjustment] = Field(description="List of adjustments to make to the schedule")


# Define the state structure
class ScheduleState(TypedDict):
    event_details: Dict[str, Any]
    category: str
    command: str
    currency: str
    original_budget: str
    new_budget: int | None
    adjustment_comment: str | None
    before_event_day: List[List[str]]
    on_event_day: List[List[str]]
    after_event_day: List[List[str]]
    additional_info: str | None
    parsed_table_updates: List[ScheduleUpdate] | None
    adjustment_count: int | None