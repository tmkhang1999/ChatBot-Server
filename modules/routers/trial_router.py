import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse, JSONResponse

from modules.models import TrialRequest
from modules.services.trial_chain import TrialConversationChain
from utils.settings import config_manager, database

trial_router = APIRouter()
trial_chain = TrialConversationChain(
    openai_api_key=config_manager.get("openai")["api_key"]
)


@trial_router.post("/try")
async def generate_trial_response(data: TrialRequest):
    try:
        if data.conversation_id is None:
            temporary_ids = list(trial_chain.memories.keys())
            data.conversation_id = database.generate_unique_conversation_id(temporary_ids)

        response = trial_chain.first_try(data.conversation_id, data.message)

        try:
            response_dict = json.loads(response)
            content = {"conversation_id": data.conversation_id,
                       "message": None,
                       "data": response_dict}
        except json.JSONDecodeError:
            content = {"conversation_id": data.conversation_id,
                       "message": response,
                       "data": None}

        return JSONResponse(status_code=200, content=content)

    except Exception:
        # Log the exception here if needed
        return JSONResponse(status_code=500, content={"error": "Internal Server Error"})


@trial_router.post("/schedule")
async def generate_schedule(data: TrialRequest):
    try:
        response = trial_chain.schedule(data.conversation_id, data.message)

        try:
            response_dict = json.loads(response)
            content = {"conversation_id": data.conversation_id,
                       "message": None,
                       "data": response_dict}
        except json.JSONDecodeError:
            content = {"conversation_id": data.conversation_id,
                       "message": response,
                       "data": None}

        return JSONResponse(status_code=200, content=content)

    except Exception:
        # Log the exception here if needed
        return JSONResponse(status_code=500,
                            content={"error": "Internal Server Error"})

# return StreamingResponse(
#     response,
#     media_type="text/event-stream",
#     headers={"conversation_id": data.conversation_id}
# )
