import asyncio
import logging
from typing import AsyncIterable, Awaitable

from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory

from modules.prompts import GENERAL_PROMPT_TEMPLATE

log = logging.getLogger(__name__)


class StreamingConversationChain:
    def __init__(self, openai_api_key: str, temperature: float = 0.0):
        self.memories = {}
        self.openai_api_key = openai_api_key
        self.temperature = temperature

    async def generate_response(self, conversation_id: str, message: str) -> AsyncIterable[str]:
        callback_handler = AsyncIteratorCallbackHandler()
        llm = ChatOpenAI(
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

        task = asyncio.create_task(wrap_done(chain.arun(input=message), callback_handler.done))

        async for token in callback_handler.aiter():
            yield token

        await task
