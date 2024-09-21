from typing import Union
from pydantic import BaseModel


class TrialRequest(BaseModel):
    conversation_id: Union[None, str]
    message: str


class OneTimeRequest(BaseModel):
    message: str


class ChatRequest(BaseModel):
    conversation_id: Union[None, str]
    project_id: Union[None, str]
    user_id: Union[None, int]
    workspace_link: Union[None, str]
    message: Union[None, str]


class ReportRequest(BaseModel):
    project_id: Union[None, str]

