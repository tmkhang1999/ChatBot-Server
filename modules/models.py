from pydantic import BaseModel


class ChatRequest(BaseModel):
    """Request body for streaming."""
    conversation_id: str
    message: str
