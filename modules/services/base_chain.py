import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Awaitable, Any, AsyncGenerator

import aioschedule as schedule
from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.chains import ConversationChain, LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory, ChatMessageHistory
from langchain.schema import messages_to_dict, messages_from_dict

from modules.prompts.zero_shot_prompts import GENERAL_PROMPT_TEMPLATE, NAME_PROMPT_TEMPLATE
from utils.settings import database

log = logging.getLogger(__name__)


class StreamingConversationChain:
    memories = {}

    def __init__(self,
                 openai_api_key: str,
                 model_name: str = "gpt-3.5-turbo",
                 temperature: float = 0.0):
        """
        Initialize the StreamingConversationChain.

        Args:
            openai_api_key (str): API key for OpenAI.
            model_name (str, optional): The name of the language model. Default is "gpt-3.5-turbo".
            temperature (float, optional): The temperature for model output. Default is 0.0.
        """
        self.openai_api_key = openai_api_key
        self.model_name = model_name
        self.temperature = temperature

        # Schedule a task to periodically check and save memories
        schedule.every(15).minutes.do(self.check_and_save_memories)

    async def generate_response(self,
                                conversation_id: str,
                                message: str) -> tuple[Any, AsyncGenerator[str, Any]]:
        """
        Generate a response for a given conversation and message.

        Args:
            conversation_id (str): Identifier for the conversation.
            message (str): Input message.

        Returns:
            tuple: A tuple containing conversation_id and response answer.
        """
        callback_handler = AsyncIteratorCallbackHandler()

        llm = ChatOpenAI(
            model_name=self.model_name,
            callbacks=[callback_handler],
            streaming=True,
            temperature=self.temperature,
            openai_api_key=self.openai_api_key,
        )

        memory_info = self.get_temporary_memory(conversation_id)

        chain = ConversationChain(
            memory=memory_info["memory"],
            prompt=GENERAL_PROMPT_TEMPLATE,
            llm=llm,
        )

        async def wrap_done(fn: Awaitable, event: asyncio.Event):
            """Wrap an awaitable with an event to signal when it's done or an exception is raised."""
            try:
                await fn
            except Exception as e:
                # TODO: handle exception
                print(f"Caught exception: {e}")
            finally:
                # Signal the aiter to stop.
                event.set()

        # Start the chain asynchronously and process tokens from the callback handler
        task = asyncio.create_task(wrap_done(chain.arun(input=message), callback_handler.done))

        async for token in callback_handler.aiter():
            yield token

        await task

    def get_temporary_memory(self, conversation_id: str):
        """
        Get or create a memory associated with a conversation ID.

        Args:
            conversation_id (str or None): Identifier for the conversation.

        Returns:
            dict: A dictionary containing memory information.
            The dictionary includes the chat_history object and the last used time.
        """
        memory_info = self.memories.get(conversation_id)
        if memory_info is None:
            memory_info = {
                "memory": ConversationBufferMemory(memory_key="chat_history", return_messages=True),
                "last_used_time": datetime.now()
            }
            self.memories[conversation_id] = memory_info
        return memory_info

    def generate_name(self, message: str) -> str:
        """
        Generate a name for the conversation based on the input message.

        Args:
            message (str): The input message used to generate the conversation name.

        Returns:
            str: The generated conversation name.
        """
        llm = ChatOpenAI(
            model_name=self.model_name,
            openai_api_key=self.openai_api_key,
        )

        name_chain = LLMChain(
            llm=llm,
            prompt=NAME_PROMPT_TEMPLATE,
        )

        return name_chain.run(input=message)

    async def check_and_save_memories(self):
        """
        Periodically check memories and save them to the database if not used for 15 minutes.
        """
        current_time = datetime.now()
        for conversation_id, memory_info in list(self.memories.items()):
            last_used_time = memory_info["last_used_time"]
            if current_time - last_used_time > timedelta(minutes=15):
                # Save the memory to the database
                await self.save_history(conversation_id)
                # Delete it from the cache
                del self.memories[conversation_id]

    async def save_history(self, conversation_id: str):
        """
        Save the conversation history to a database.

        Args:
            conversation_id (str): Identifier for the conversation.
        """
        memory = self.memories.get(conversation_id)["memory"]
        extracted_messages = memory.chat_memory.messages
        ingest_to_db = messages_to_dict(extracted_messages)
        database.update_history(conversation_id, json.dumps(ingest_to_db))

    async def load_history(self, conversation_id: str):
        """
        Load conversation history from a database.

        Args:
            conversation_id (str): Identifier for the conversation.

        Returns:
            None if the conversation history is not found in the database, or a retrieved memory if found.
        """
        # Check if the memory is already in the cache (self.memories)
        memory_info = self.memories.get(conversation_id)

        if memory_info is not None:
            extracted_messages = memory_info["memory"].chat_memory.messages
            ingest_to_db = messages_to_dict(extracted_messages)
            return json.dumps(ingest_to_db)

        # If the memory is not in the cache, so attempt to retrieve it from the database
        retrieve_from_db = await database.get_history(conversation_id)

        # If the memory is not found in the database, log a warning and return None
        if not retrieve_from_db:
            log.error(f"No conversation history with id {conversation_id} found in either the cache or the database.")
            return None

        # Parse the retrieved memory from JSON and create a ConversationBufferMemory
        retrieved_messages = messages_from_dict(json.loads(retrieve_from_db["memory"]))
        retrieved_chat_history = ChatMessageHistory(messages=retrieved_messages)
        retrieved_memory = ConversationBufferMemory(
            chat_memory=retrieved_chat_history,
            memory_key="chat_history",
            return_messages=True
        )

        # Add the retrieved memory_info to the cache
        memory_info = {"memory": retrieved_memory, "last_used_time": datetime.now()}
        self.memories[conversation_id] = memory_info
        return retrieve_from_db["memory"]
