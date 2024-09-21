import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from modules.routers.models import TrialRequest, OneTimeRequest
from modules.services.chain.trial_chain import TrialConversationChain

# Constants
MAX_ATTEMPTS = 3

# Router and Chain instance
trial_router = APIRouter()
trial_chain = TrialConversationChain()

# Logger configuration
logger = logging.getLogger(__name__)


def parse_json_response(response: str):
    """Attempt to parse JSON response and log failure."""
    try:
        return json.loads(response), True
    except json.JSONDecodeError:
        logger.warning("JSON decoding failed.")
        return None, False


def handle_response(response, conversation_id):
    """Create a JSON response based on the success of parsing the input response."""
    response_dict, success = parse_json_response(response)
    if success:
        content = {
            "conversation_id": conversation_id,
            "message": None,
            "data": response_dict
        }
    else:
        content = {
            "conversation_id": conversation_id,
            "message": response,
            "data": None
        }
    print(content)
    return JSONResponse(status_code=status.HTTP_200_OK, content=content)


@trial_router.post("/try")
async def generate_trial_response(data: TrialRequest):
    """Generate a trial response for a given trial request."""
    if data.conversation_id is None:
        logger.info("Generating a unique conversation ID.")
        temporary_ids = set(trial_chain.memories.keys())
        data.conversation_id = trial_chain.generate_unique_conversation_id(temporary_ids)
    response = trial_chain.first_try(data.conversation_id, data.message)
    return handle_response(response, data.conversation_id)


@trial_router.post("/schedule", response_class=JSONResponse)
async def generate_schedule(data: TrialRequest):
    """Generate a schedule based on the provided message."""
    if data.conversation_id is None:
        logger.info("Generating a unique schedule ID.")
        temporary_ids = set(trial_chain.memories.keys())
        data.conversation_id = trial_chain.generate_unique_conversation_id(temporary_ids)

    for attempt in range(MAX_ATTEMPTS):
        response = trial_chain.schedule(data.conversation_id, data.message)
        response_dict, success = parse_json_response(response)
        print(response_dict)
        if success:
            return JSONResponse(status_code=status.HTTP_200_OK,
                                content={"conversation_id": data.conversation_id,
                                         "data": response_dict})
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed after multiple attempts.")


@trial_router.post("/description", response_class=JSONResponse)
async def generate_description(data: OneTimeRequest):
    """Generate a description based on the provided message."""
    for attempt in range(MAX_ATTEMPTS):
        response = trial_chain.description(data.message)
        response_dict, success = parse_json_response(response)
        print(response)
        if success:
            return JSONResponse(status_code=status.HTTP_200_OK, content={"data": response_dict})
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed after multiple attempts.")


@trial_router.post("/new_description", response_class=JSONResponse)
async def generate_new_description(data: OneTimeRequest):
    """Process multiple description generation tasks concurrently."""
    try:
        tasks = json.loads(data.message)
    except json.JSONDecodeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON format for message.")

    if not tasks or not isinstance(tasks, list):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Message content must be a non-empty list of tasks.")

    results = {}

    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(trial_chain.new_description, task): task for task in tasks}
        for future in as_completed(futures):
            task = futures[future]
            results[task] = future.result()

    return JSONResponse(status_code=status.HTTP_200_OK, content={"data": results})


@trial_router.post("/dependency", response_class=JSONResponse)
async def generate_dependency(data: OneTimeRequest):
    """Generate a dependency list based on the provided message."""
    try:
        tasks = json.loads(data.message)
    except json.JSONDecodeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON format for message.")

    if not tasks or not isinstance(tasks, list):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Message content must be a non-empty list of tasks.")

    for attempt in range(MAX_ATTEMPTS):
        response = trial_chain.dependency(data.message)
        response_dict, success = parse_json_response(response)
        print(response)
        if success:
            return JSONResponse(status_code=status.HTTP_200_OK, content={"data": response_dict})
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed after multiple attempts.")


@trial_router.post("/budget_category", response_class=JSONResponse)
async def generate_budget_category(data: OneTimeRequest):
    """Generate a dependency list based on the provided message."""
    try:
        tasks = json.loads(data.message)
    except json.JSONDecodeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON format for message.")

    if not tasks or not isinstance(tasks, list):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Message content must be a non-empty list of tasks.")

    for attempt in range(MAX_ATTEMPTS):
        response = trial_chain.budget_category(data.message)
        response_dict, success = parse_json_response(response)
        print(response)
        if success:
            return JSONResponse(status_code=status.HTTP_200_OK, content={"data": response_dict})
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed after multiple attempts.")
