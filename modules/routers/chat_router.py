from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse

from modules.models import ChatRequest
from modules.services.base_chain import StreamingConversationChain
from utils.settings import config_manager, database

chat_router = APIRouter()
base_chain = StreamingConversationChain(
    openai_api_key=config_manager.get("openai")["api_key"]
)


@chat_router.post("/chat", response_class=StreamingResponse)
async def generate_response(data: ChatRequest) -> StreamingResponse:
    if data.conversation_id is None:
        temporary_ids = list(base_chain.memories.keys())
        data.conversation_id = database.generate_unique_conversation_id(temporary_ids)

        if data.conversation_name is None:
            data.conversation_name = base_chain.generate_name(data.message)

        database.add_conversation(data.user_id, data.conversation_id, data.conversation_name)

    response = base_chain.generate_response(data.conversation_id, data.message)

    # async def generate():
    #     return await base_chain.generate_response(data.conversation_id, data.message)
    #
    # response = await generate()

    return StreamingResponse(
        response,
        media_type="text/event-stream",
        headers={"conversation_id": data.conversation_id, "conversation_name": data.conversation_name}
    )


@chat_router.get("/load_history/{conversation_id}")
async def load_history(conversation_id: str):
    retrieved_history = base_chain.load_history(conversation_id)
    if retrieved_history is not None:
        return JSONResponse(status_code=200,
                            content={"message": "Conversation history loaded successfully",
                                     "history": retrieved_history})
    else:
        raise HTTPException(status_code=404,
                            detail="Conversation history not found")


@chat_router.post("/save_history/{conversation_id}")
async def save_history(conversation_id: str):
    await base_chain.save_history(conversation_id)
    return JSONResponse(status_code=200,
                        content={"message": "Conversation history saved successfully"})
