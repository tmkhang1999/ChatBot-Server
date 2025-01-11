import logging
import uuid

from langchain_openai import ChatOpenAI

from modules.services.graphs import EventChatbot
from modules.services.tools.weekly_reporter import report
from utils.settings import planz_db


class StreamingConversationChain:
    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 0.7):
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature)
        self.agent = EventChatbot(MODEL_NAME=model_name, TEMPERATURE=temperature, database=planz_db)
        self.thread_ids = set()

    def generate_response(self, conversation_id: str, project_id: str, user_id: int, workspace_link: str, message: str):
        return self.agent.execute_workflow(conversation_id, message, project_id, user_id, workspace_link)

    def generate_id(self) -> str:
        new_id = str(uuid.uuid4())
        while new_id in self.thread_ids:
            new_id = str(uuid.uuid4())
        self.thread_ids.add(new_id)
        return new_id

    @staticmethod
    def report(project_id: str):
        res = report(project_id, planz_db)
        return res
