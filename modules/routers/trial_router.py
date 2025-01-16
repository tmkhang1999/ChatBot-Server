import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from modules.routers.models import TrialRequest, OneTimeRequest, ScheduleRequest
from modules.services.chain.trial_chain import TrialConversationChain

# Constants
MAX_ATTEMPTS = 3

# Router and Chain initialization
trial_router = APIRouter()
trial_chain = TrialConversationChain()

# Configure logging
logger = logging.getLogger(__name__)


def parse_json_response(response: str) -> tuple[Dict[str, Any] | None, bool]:
    """
    Attempt to parse a JSON response string.

    Args:
        response: JSON string to parse

    Returns:
        Tuple of (parsed_json, success_flag)
    """
    try:
        return json.loads(response), True
    except json.JSONDecodeError:
        logger.warning("Failed to decode JSON response")
        return None, False


def handle_response(response: str, conversation_id: str) -> JSONResponse:
    """
    Create a standardized JSON response.

    Args:
        response: Response string to process
        conversation_id: ID of the conversation

    Returns:
        Formatted JSONResponse object
    """
    response_dict, success = parse_json_response(response)
    content = {
        "conversation_id": conversation_id,
        "message": None if success else response,
        "data": response_dict if success else None
    }
    return JSONResponse(status_code=status.HTTP_200_OK, content=content)


@trial_router.post("/try")
async def generate_trial_response(data: TrialRequest) -> JSONResponse:
    """Generate a trial response for the given message."""
    if data.conversation_id is None:
        logger.info("Generating new conversation ID")
        data.conversation_id = trial_chain.generate_id()

    response = trial_chain.suggest_event(data.message)
    return handle_response(response, data.conversation_id)


@trial_router.post("/schedule")
async def generate_schedule(data: TrialRequest) -> JSONResponse:
    """Generate a schedule based on event data."""
    if data.conversation_id is None:
        logger.info("Generating new conversation ID")
        data.conversation_id = trial_chain.generate_id()

    try:
        event_dict = json.loads(data.message)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to decode JSON message"
        )

    response = trial_chain.generate_schedule(data.conversation_id, event_dict)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "conversation_id": data.conversation_id,
            "data": response
        }
    )


@trial_router.post("/description")
async def generate_description(data: ScheduleRequest) -> JSONResponse:
    """
    Process description generation tasks for different event stages concurrently.
    """
    # Validate and parse input JSON
    try:
        tables = {
            "table_before_event_day": json.loads(data.table_before_event_day),
            "table_on_the_event_day": json.loads(data.table_on_the_event_day),
            "table_after_the_event_day": json.loads(data.table_after_the_event_day)
        }
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON format in one or more tables"
        )

    # Validate table contents
    for table_name, table_data in tables.items():
        if not isinstance(table_data, list):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{table_name} must be a list of tasks"
            )

    # Process tasks concurrently
    results = {table_name: {} for table_name in tables.keys()}

    with ThreadPoolExecutor() as executor:
        futures = {}
        for table_name, table_data in tables.items():
            for task in table_data:
                future = executor.submit(trial_chain.generate_description, task)
                futures[future] = (table_name, task)

        for future in as_completed(futures):
            table_name, task = futures[future]
            results[table_name][task] = future.result()

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"data": results}
    )


@trial_router.post("/dependency")
async def generate_dependency(data: OneTimeRequest) -> JSONResponse:
    """Generate dependency relationships between tasks."""
    try:
        tasks = json.loads(data.message)
        if not isinstance(tasks, list) or not tasks:
            raise ValueError("Invalid task list")
    except (json.JSONDecodeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message must be a non-empty JSON array of tasks"
        )

    for attempt in range(MAX_ATTEMPTS):
        response = trial_chain.detect_dependency(data.message)
        response_dict, success = parse_json_response(response)

        if success:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"data": response_dict}
            )

        logger.warning(f"Attempt {attempt + 1} failed to generate dependencies")

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to generate dependencies after multiple attempts"
    )


@trial_router.post("/budget_category")
async def generate_budget_category(data: OneTimeRequest) -> JSONResponse:
    """Categorize tasks into budget categories."""
    try:
        tasks = json.loads(data.message)
        if not isinstance(tasks, list) or not tasks:
            raise ValueError("Invalid task list")
    except (json.JSONDecodeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message must be a non-empty JSON array of tasks"
        )

    for attempt in range(MAX_ATTEMPTS):
        response = trial_chain.categorize_budget(data.message)
        response_dict, success = parse_json_response(response)

        if success:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"data": response_dict}
            )

        logger.warning(f"Attempt {attempt + 1} failed to categorize budget")

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to categorize budget after multiple attempts"
    )