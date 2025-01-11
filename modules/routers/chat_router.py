from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from modules.routers.models import ChatRequest, ReportRequest
from modules.services.chain.base_chain import StreamingConversationChain

chat_router = APIRouter()
base_chain = StreamingConversationChain()


@chat_router.post("/chat")
async def generate_chat_response(data: ChatRequest):
    """Handles chat requests, generating responses based on the provided ChatRequest data."""
    try:
        # Assign a unique conversation_id if it's not provided
        if data.conversation_id is None:
            data.conversation_id = base_chain.generate_id()

        # Generate a response based on the provided message or use a default prompt
        response_message = base_chain.generate_response(
            data.conversation_id, data.project_id, data.user_id, data.workspace_link, data.message
        ) if data.message else "What can I help you with today?"
        print(response_message)

        content = {
            "conversation_id": data.conversation_id,
            "message": ' '.join(response_message.split())

        }
        return JSONResponse(status_code=200, content=content)

    except Exception as e:
        # Log the exception or handle it as required
        raise HTTPException(status_code=500, detail=str(e))


@chat_router.post("/report")
async def generate_report_response(data: ReportRequest):
    """Handles report requests and provides a summary or report based on the ReportRequest data."""
    try:
        content = {
            "data": base_chain.report(data.project_id)
        }
        print(content)
        return JSONResponse(status_code=200, content=content)
    except Exception as e:
        # Log the exception or handle it as required
        raise HTTPException(status_code=500, detail=str(e))
