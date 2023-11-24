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
def generate_trial_response(data: TrialRequest):
    if data.conversation_id is None:
        temporary_ids = list(trial_chain.memories.keys())
        data.conversation_id = database.generate_unique_conversation_id(temporary_ids)

    response = trial_chain.first_try(data.conversation_id, data.message)

    return JSONResponse(status_code=200,
                        content={"conversation_id": data.conversation_id,
                                 "message": response})

    # return StreamingResponse(
    #     response,
    #     media_type="text/event-stream",
    #     headers={"conversation_id": data.conversation_id}
    # )


@trial_router.post("/schedule")
def generate_schedule(data: TrialRequest):
    response = trial_chain.schedule(data.conversation_id, data.message)

    return JSONResponse(status_code=200,
                        content={"conversation_id": data.conversation_id,
                                 "message": response})
