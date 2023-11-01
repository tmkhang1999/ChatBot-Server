from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from modules.models import ChatRequest
from modules.services import StreamingConversationChain
from utils.settings import config_manager

chat_router = APIRouter()
chat_response = StreamingConversationChain(
    openai_api_key=config_manager.get("openai_api_key")
)


@chat_router.post("/chat", response_class=StreamingResponse)
async def generate_response(data: ChatRequest) -> StreamingResponse:
    return StreamingResponse(
        chat_response.generate_response(data.conversation_id, data.message),
        media_type="text/event-stream"
    )
