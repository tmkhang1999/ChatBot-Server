from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from starlette.responses import JSONResponse

from modules.models import ChatRequest
from modules.services import StreamingConversationChain
from utils.settings import config_manager

chat_router = APIRouter()
chat_response = StreamingConversationChain(
    openai_api_key=config_manager.get("openai")["api_key"],
    model_name=config_manager.get("openai")["model_name"]
)


@chat_router.post("/chat", response_class=StreamingResponse)
async def generate_response(data: ChatRequest) -> StreamingResponse:
    return StreamingResponse(
        chat_response.generate_response(data.conversation_id, data.message),
        media_type="text/event-stream"
    )


@chat_router.get("/load/{conversation_id}")
async def load_history(conversation_id: str):
    retrieved_history = chat_response.load_history(conversation_id)
    if retrieved_history is not None:
        return JSONResponse(status_code=200,
                            content={"message": "Conversation history loaded successfully",
                                     "history": retrieved_history})
    else:
        raise HTTPException(status_code=404,
                            detail="Conversation history not found")


@chat_router.post("/save/{conversation_id}")
async def save_history(conversation_id: str):
    chat_response.save_history(conversation_id)
    return JSONResponse(status_code=200,
                        content={"message": "Conversation history saved successfully"})
