import logging
import uuid
from datetime import datetime, timedelta

import aioschedule as schedule
from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers.openai_functions import OpenAIFunctionsAgentOutputParser
from langchain.memory import ConversationBufferMemory
from langchain_core.runnables import RunnablePassthrough
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain_openai import ChatOpenAI
from langchain.chains.llm import LLMChain

from modules.prompts.few_shot_prompts import EventPromptFactory
from modules.prompts.zero_shot_prompts import CHATBOT_PROMPT_TEMPLATE, CONTEXTUALIZE_PROMPT_TEMPLATE
from modules.services.tools.sql_checker import SQLChecker
from modules.services.tools.weekly_reporter import report
from utils.settings import planz_db

from langgraph.prebuilt import tools_condition

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
EventPromptFactory.init_templates()


def create_my_agent(llm, tools, prompt):
    missing_vars = {"agent_scratchpad"}.difference(prompt.input_variables)
    if missing_vars:
        raise ValueError(f"Prompt missing required variables: {missing_vars}")

    agent = (
            RunnablePassthrough.assign(
                agent_scratchpad=lambda x: format_to_openai_function_messages(
                    x["intermediate_steps"]
                )
            )
            | prompt
            | llm.bind_functions([convert_to_openai_function(tool) for tool in tools])
            | OpenAIFunctionsAgentOutputParser()
    )
    return agent


class StreamingConversationChain:
    memories = {}

    def __init__(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0.7):
        """
        Initializes a streaming conversation chain with a specified language model and temperature.

        :param model_name: Name of the OpenAI model to be used, defaults to 'gpt-3.5-turbo'.
        :param temperature: Creativity temperature for model outputs, defaults to 0.0.
        """
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature)
        self.chatbot_tools = [SQLChecker(planz_db, self.llm, EventPromptFactory.SQL_TEMPLATE)]
        self.agent = create_my_agent(
            llm=self.llm,
            tools=self.chatbot_tools,
            prompt=CHATBOT_PROMPT_TEMPLATE
        )
        self.agent_executor = AgentExecutor(
            name="PlanZ - event assistant",
            agent=self.agent,
            tools=self.chatbot_tools,
            verbose=True)

        schedule.every(15).minutes.do(self.check_and_save_memories)

    def generate_response(self, conversation_id: str, project_id: str, user_id: int, workspace_link: str, message: str) -> tuple:
        """
        Generates a response based on the input message for a given conversation.

        :param conversation_id: Unique identifier for the conversation.
        :param project_id: Identifier for the project related to the conversation.
        :param message: User's input message to the conversation.
        :return: A tuple containing the conversation ID and the generated response.
        """
        contextualizer = LLMChain(
            prompt=CONTEXTUALIZE_PROMPT_TEMPLATE,
            memory=self.get_temporary_memory(conversation_id)["memory"],
            llm=self.llm
        )

        question = contextualizer.invoke({"input": message})
        print(question["text"])
        answer = self.agent_executor.invoke({
            "input": question["text"],
            "project_id": project_id,
            "user_id": user_id,
            "workspace_link": workspace_link
        })
        return answer["output"]

    def get_temporary_memory(self, conversation_id: str) -> dict:
        """
        Retrieves or initializes a temporary memory buffer for a conversation.

        :param conversation_id: The conversation's unique identifier.
        :return: A dictionary with memory information, including the chat history and last used time.
        """
        memory_info = self.memories.get(conversation_id, {
            "memory": ConversationBufferMemory(memory_key="chat_history", input_key="input", k=5, return_messages=True),
            "last_used_time": datetime.now()
        })
        self.memories[conversation_id] = memory_info  # Update or set new
        return memory_info

    @staticmethod
    def generate_unique_conversation_id(temporary_ids: set) -> str:
        """
        Generates a unique identifier for a new conversation.

        :param temporary_ids: A set of temporary IDs to ensure uniqueness.
        :return: A unique conversation ID as a string.
        """
        new_id = str(uuid.uuid4())
        while new_id in temporary_ids:
            new_id = str(uuid.uuid4())
        return new_id

    def check_and_save_memories(self):
        """
        Periodically checks and saves conversation memories if they haven't been used for a specified duration.
        """
        current_time = datetime.now()
        for conversation_id, memory_info in list(self.memories.items()):
            if current_time - memory_info["last_used_time"] > timedelta(minutes=15):
                del self.memories[conversation_id]  # Evict from cache

    @staticmethod
    def report(project_id: str):
        res = report(project_id, planz_db)
        return res

    # async def save_history(self, conversation_id: str):
    #     """
    #     Save the conversation history to a database.
    #
    #     Args:
    #         conversation_id (str): Identifier for the conversation.
    #     """
    #     memory = self.memories.get(conversation_id)["memory"]
    #     extracted_messages = memory.chat_memory.messages
    #     ingest_to_db = messages_to_dict(extracted_messages)
    #     ai_db.update_history(conversation_id, json.dumps(ingest_to_db))
    #
    # async def load_history(self, conversation_id: str):
    #     """
    #     Load conversation history from a database.
    #
    #     Args:
    #         conversation_id (str): Identifier for the conversation.
    #
    #     Returns:
    #         None if the conversation history is not found in the database, or a retrieved memory if found.
    #     """
    #     # Check if the memory is already in the cache (self.memories)
    #     memory_info = self.memories.get(conversation_id)
    #
    #     if memory_info is not None:
    #         extracted_messages = memory_info["memory"].chat_memory.messages
    #         ingest_to_db = messages_to_dict(extracted_messages)
    #         return json.dumps(ingest_to_db)
    #
    #     # If the memory is not in the cache, so attempt to retrieve it from the database
    #     retrieve_from_db = ai_db.get_history(conversation_id)
    #
    #     # If the memory is not found in the database, log a warning and return None
    #     if not retrieve_from_db:
    #         log.error(f"No conversation history with id {conversation_id} found in either the cache or the database.")
    #         return None
    #
    #     # Parse the retrieved memory from JSON and create a ConversationBufferMemory
    #     retrieved_messages = messages_from_dict(json.loads(retrieve_from_db))
    #     retrieved_chat_history = ChatMessageHistory(messages=retrieved_messages)
    #     retrieved_memory = ConversationBufferMemory(
    #         chat_memory=retrieved_chat_history,
    #         memory_key="chat_history",
    #         return_messages=True
    #     )
    #
    #     # Add the retrieved memory_info to the cache
    #     memory_info = {"memory": retrieved_memory, "last_used_time": datetime.now()}
    #     self.memories[conversation_id] = memory_info
    #     return retrieve_from_db
