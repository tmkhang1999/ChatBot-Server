import logging

from langchain.agents import AgentExecutor
from langchain.chains.llm import LLMChain
from langchain_openai import ChatOpenAI, OpenAI

from modules.prompts.few_shot_prompts import EventPromptFactory
from modules.services.chain.base_chain import StreamingConversationChain
from modules.services.chain.base_chain import create_my_agent
from modules.services.tools.event_extractor import EventExtractor

# Setup basic logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class TrialConversationChain(StreamingConversationChain):
    def __init__(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0.7):
        """
        Initialize the TrialConversationChain with the model and temperature settings.

        :param model_name: The name of the OpenAI language model, defaults to "gpt-3.5-turbo".
        :param temperature: The creativity for model output, defaults to 0.7.
        """
        super().__init__(model_name, temperature)
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature)

        self.tools = [EventExtractor(self.llm)]

        self.agent = create_my_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=EventPromptFactory.EVENT_TRIAL_PROMPT_TEMPLATE
        )

        self.description_chain = LLMChain(
            prompt=EventPromptFactory.TASK_DESCRIPTION_PROMPT_TEMPLATE,
            llm=self.llm,
            verbose=True
        )

        self.new_description_chain = LLMChain(
            prompt=EventPromptFactory.NEW_TASK_DESCRIPTION_PROMPT_TEMPLATE,
            llm=self.llm
        )

        self.dependency_chain = LLMChain(
            prompt=EventPromptFactory.DEPENDENCY_PROMPT_TEMPLATE,
            llm=self.llm,
            verbose=True
        )

        self.budget_category_chain = LLMChain(
            prompt=EventPromptFactory.BUDGET_CATEGORY_PROMPT_TEMPLATE,
            llm=self.llm,
            verbose=True
        )

    def first_try(self, conversation_id: str, message: str) -> str:
        """
        Generates a response for the initial trial conversation based on the user's
        input message. This method accommodates both general inquiries and specific
        event-related questions, offering tailored responses.

        :param conversation_id: A unique identifier for the ongoing conversation.
                                This ID helps track and manage the conversation's context.
        :param message: The user's input message, which can range from a general
                        query to a specific question about event planning or scheduling.
        :return: A string containing the generated response. The nature of the query
                 dictates the response: a straightforward answer or a structured
                 dictionary. For the latter, it includes questions as keys and an
                 array of three generated options as values.
        """
        agent_executor = AgentExecutor(
            agent=self.agent,
            memory=self.get_temporary_memory(conversation_id)["memory"],
            tools=self.tools,
            verbose=True
        )
        answer = agent_executor.invoke({"input": message})
        return answer["output"]

    def schedule(self, conversation_id: str, message: str) -> str:
        """
        Generates a detailed plan for an event from specified parameters. It processes
        input structured as a dictionary, covering key event aspects like purpose,
        deadline, location, guest count, budget, themes, and activities.

        The output is a plan detailing steps before the event day and the schedule
        for the event day, including budget allocations and coordination instructions.

        :param message: A JSON-like string with event specifications, including keys
                        for event purpose, deadline, duration, location, number of
                        guests, budget range, themes, colors, and activities.
        :return: A stringified JSON outlining the event plan, covering pre-event
                 arrangements and the day-of event schedule, with stages, duration,
                 and budget.
        """
        schedule_chain = LLMChain(
            prompt=EventPromptFactory.EVENT_SCHEDULE_PROMPT_TEMPLATE,
            memory=self.get_temporary_memory(conversation_id)["memory"],
            llm=self.llm,
            verbose=True
        )

        answer = schedule_chain.invoke({"input": message})
        return answer["text"]

    def description(self, message: str) -> str:
        """
        Generates detailed descriptions for specified tasks based on user input.
        This method excels in structuring responses for event planning tasks or
        similar activities that require step-by-step instructions.

        The input is expected to be a query or a set of instructions related to
        the task. The method processes these to deliver a structured response
        that clearly outlines necessary steps or actions.

        :param message: User's input containing task-related queries or
                     instructions. The input format should be a list of tasks
                     or questions seeking detailed descriptions or action plans.
        :return: A structured string providing clear, actionable steps for each
              task or question in the input. This includes enumerating steps
              for execution or offering options and recommendations.
        """

        answer = self.description_chain.invoke({"input": message})
        return answer["text"]

    def new_description(self, message: str) -> str:
        answer = self.new_description_chain.invoke({"input": message})
        return answer["text"]

    def dependency(self, message: str) -> str:
        answer = self.dependency_chain.invoke({"input": message})
        return answer["text"]

    def budget_category(self, message: str) -> str:
        answer = self.budget_category_chain.invoke({"input": message})
        return answer["text"]
