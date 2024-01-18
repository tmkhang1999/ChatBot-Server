import asyncio
import logging
from typing import AsyncIterator, Dict, Tuple, List

from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.chains import ConversationChain
from langchain.chains.llm import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.chains.router.llm_router import LLMRouterChain, RouterOutputParser
from langchain.chains.router import MultiPromptChain
from langchain.chains.router.multi_prompt_prompt import MULTI_PROMPT_ROUTER_TEMPLATE
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

from modules.services.base_chain import StreamingConversationChain
from modules.prompts.few_shot_prompts import EventPromptFactory
# from modules.prompts.zero_shot_prompts import EVENT_SCHEDULE_PROMPT_TEMPLATE

log = logging.getLogger(__name__)
prompt_factory = EventPromptFactory()


class TrialConversationChain(StreamingConversationChain):
    def __init__(self,
                 openai_api_key: str,
                 model_name: str = "gpt-3.5-turbo",
                 temperature: float = 0.0):
        """
        Initialize the TrialConversationChain.

        Args:
            openai_api_key (str): API key for OpenAI.
            model_name (str, optional): The name of the OpenAI language model. Defaults to "gpt-3.5-turbo".
            temperature (float, optional): The temperature for model output. Defaults to 0.0.
        """
        super().__init__(openai_api_key, model_name, temperature)

    def first_try(self, conversation_id: str, message: str):
        """
        Generate a response for the trial conversation.

        Args:
            conversation_id (str): Identifier for the conversation.
            message (str): Input message.

        Yields:
            AsyncIterator[str]: A sequence of response tokens.
        """
        # callback_handler = AsyncIteratorCallbackHandler()

        llm = ChatOpenAI(
            model_name=self.model_name,
            # callbacks=[callback_handler],
            # streaming=True,
            temperature=self.temperature,
            openai_api_key=self.openai_api_key,
        )

        memory_info = self.get_temporary_memory(conversation_id)

        prompt_infos, destination_chains, default_chain = self.generate_destination_chains(llm, memory_info["memory"])
        multi_prompt_chain = self.generate_router_chain(prompt_infos, destination_chains, default_chain, llm)

        return multi_prompt_chain.run(input=message)

    def schedule(self, conversation_id: str, message: str):
        """
        Generate a response for the trial conversation.

        Args:
            conversation_id (str): Identifier for the conversation.
            message (str): Input message.

        Yields:
            AsyncIterator[str]: A sequence of response tokens.
        """
        # callback_handler = AsyncIteratorCallbackHandler()

        llm = ChatOpenAI(
            model_name=self.model_name,
            # callbacks=[callback_handler],
            # streaming=True,
            temperature=self.temperature,
            openai_api_key=self.openai_api_key,
        )

        memory_info = self.get_temporary_memory(conversation_id)

        schedule_chain = LLMChain(
            memory=memory_info["memory"],
            prompt=prompt_factory.EVENT_SCHEDULE_PROMPT_TEMPLATE,
            llm=llm,
        )

        return schedule_chain.run(input=message)

    @staticmethod
    def generate_destination_chains(chat_model: ChatOpenAI, memory: ConversationBufferMemory) -> Tuple[List[Dict[str, str]], Dict[str, LLMChain], LLMChain]:
        """
        Generate a list of LLM chains with different prompt templates.

        Args:
            chat_model (ChatOpenAI): Chat model instance.
            memory: Memory information.

        Returns:
            Tuple: A tuple containing prompt information, destination chains, and default chain.
        """
        destination_chains: Dict[str, LLMChain] = {}
        for p_info in prompt_factory.prompt_infos:
            chain = LLMChain(
                llm=chat_model,
                prompt=p_info['prompt'],
                memory=memory)
            destination_chains[p_info['name']] = chain

        default_chain = LLMChain(
            llm=chat_model,
            prompt=prompt_factory.IRRELEVANT_PROMPT_TEMPLATE,
            memory=memory
        )
        return prompt_factory.prompt_infos, destination_chains, default_chain

    @staticmethod
    def generate_router_chain(prompt_infos, destination_chains, default_chain, chat_model):
        """
        Generate the router chains from the prompt infos.

        Args:
            prompt_infos: The prompt information generated above.
            destination_chains: Destination LLM chains.
            default_chain: Default conversation chain.
            chat_model: Chat model instance.

        Returns:
            MultiPromptChain: The generated multi-prompt chain.
        """
        destinations = [f"{p['name']}: {p['description']}" for p in prompt_infos]
        destinations_str = '\n'.join(destinations)
        router_template = MULTI_PROMPT_ROUTER_TEMPLATE.format(destinations=destinations_str)
        router_prompt = PromptTemplate(
            template=router_template,
            input_variables=['input'],
            output_parser=RouterOutputParser()
        )
        router_chain = LLMRouterChain.from_llm(chat_model, router_prompt)
        return MultiPromptChain(
            router_chain=router_chain,
            destination_chains=destination_chains,
            default_chain=default_chain,
            # verbose=True,
            # callbacks=[callback_handler]
        )
