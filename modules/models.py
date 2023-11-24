from typing import Union
from pydantic import BaseModel


class TrialRequest(BaseModel):
    """Request body for trial streaming before login."""
    conversation_id: Union[None, str]
    message: str


class AddUserRequest(BaseModel):
    """Request body for adding user. Conversation_id is not None if the user try before login"""
    user_id: str
    conversation_id: Union[None, str]


class ChatRequest(BaseModel):
    """Request body for chat streaming after login."""
    user_id: str
    conversation_id: Union[None, str]
    conversation_name: Union[None, str]
    message: str

