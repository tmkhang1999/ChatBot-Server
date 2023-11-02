import asyncio
import json
import logging
from typing import AsyncIterable, Awaitable

from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory, ChatMessageHistory

from modules.prompts import GENERAL_PROMPT_TEMPLATE
from langchain.schema import messages_to_dict, messages_from_dict
from utils.settings import conversations

log = logging.getLogger(__name__)


class StreamingConversationChain:
    def __init__(self,
                 openai_api_key: str,
                 model_name: str = "gpt-3.5-turbo",
                 temperature: float = 0.0):
        """
        Initialize the StreamingConversationChain.

        Args:
            openai_api_key (str): API key for OpenAI.
            temperature (float, optional): The temperature for model output. Default is 0.0.
        """
        self.memories = {}
        self.openai_api_key = openai_api_key
        self.model_name = model_name
        self.temperature = temperature

    async def generate_response(self, conversation_id: str, message: str) -> AsyncIterable[str]:
        """
        Generate a response for a given conversation and message.

        Args:
            conversation_id (str): Identifier for the conversation.
            message (str): Input message.

        Yields:
            AsyncIterable[str]: A sequence of response tokens.
        """
        callback_handler = AsyncIteratorCallbackHandler()

        llm = ChatOpenAI(
            model_name=self.model_name,
            callbacks=[callback_handler],
            streaming=True,
            temperature=self.temperature,
            openai_api_key=self.openai_api_key,
        )

        memory = self.memories.get(conversation_id)
        if memory is None:
            memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
            self.memories[conversation_id] = memory

        chain = ConversationChain(
            memory=memory,
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

    def save_history(self, conversation_id: str):
        """
        Save the conversation history to a database.

        Args:
            conversation_id (str): Identifier for the conversation.
        """
        memory = self.memories.get(conversation_id)
        extracted_messages = memory.chat_memory.messages
        ingest_to_db = messages_to_dict(extracted_messages)
        conversations.insert(dict(conversation_id=conversation_id, memory=json.dumps(ingest_to_db)))

    def load_history(self, conversation_id: str):
        """
        Load conversation history from a database.

        Args:
            conversation_id (str): Identifier for the conversation.

        Returns:
            None if the conversation history is not found in the database, or a retrieved memory if found.
        """
        retrieve_from_db = conversations.find_one(conversation_id=conversation_id)
        if not retrieve_from_db:
            log.error(f"No conversation history with id {conversation_id} found in the database.")  # Raise a warning
            return None

        retrieved_messages = messages_from_dict(json.loads(retrieve_from_db["memory"]))
        retrieved_chat_history = ChatMessageHistory(messages=retrieved_messages)
        retrieved_memory = ConversationBufferMemory(chat_memory=retrieved_chat_history)
        self.memories[conversation_id] = retrieved_memory

        return retrieve_from_db["memory"]
