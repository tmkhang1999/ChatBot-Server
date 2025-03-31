import json

from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph

from modules.services.common import create_few_shot_prompt_template, create_example_selector
from .models import PlannerState, QueryType, EventDetails
from .examples import event_extraction_examples
from .prompt import ROUTE_PROMPT, GENERAL_PROMPT, EVENT_EXTRACTION_PROMPT, EVENT_SUGGESTION_PROMPT


class EventSuggester:
    def __init__(self, MODEL_NAME, TEMPERATURE):
        self.memory_saver = MemorySaver()
        self.planner_workflow = self._create_workflow()
        self.llm = ChatOpenAI(model_name=MODEL_NAME, temperature=TEMPERATURE)
        self.EVENT_SUGGESTION_PROMPT_TEMPLATE = create_few_shot_prompt_template(
            create_example_selector(event_extraction_examples, OpenAIEmbeddings, FAISS, 2, ["input"]),
            "User: {input}\nLanguage: {language}\nAI: {answer}",
            EVENT_SUGGESTION_PROMPT,
            "Extracted event details: {input}\nPlease respond in {language}\nAI:",
            ["input"]
        )

    def _create_workflow(self) -> CompiledStateGraph:
        """Create and compile the LangChain workflow as a graph."""
        # Graph definition
        planner_workflow = StateGraph(PlannerState)

        # Add nodes
        planner_workflow.add_node("classify_query", self.classify_query)
        planner_workflow.add_node("handle_general_query", self.handle_general_query)
        planner_workflow.add_node("extract_event_details", self.extract_event_details)
        planner_workflow.add_node("generate_event_suggestions", self.generate_event_suggestions)

        # Define edges
        planner_workflow.set_entry_point("classify_query")

        def get_query_type(state: PlannerState):
            return state.query_type

        planner_workflow.add_conditional_edges(
            "classify_query",
            get_query_type,
            {
                "GENERAL": "handle_general_query",
                "EVENT_RELATED": "extract_event_details"
            }
        )
        planner_workflow.add_edge("handle_general_query", END)
        planner_workflow.add_edge("extract_event_details", "generate_event_suggestions")
        planner_workflow.add_edge("generate_event_suggestions", END)

        return planner_workflow.compile()

    # Node functions
    def classify_query(self, state: PlannerState) -> PlannerState:
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(ROUTE_PROMPT),
            HumanMessagePromptTemplate.from_template("{question}")
        ])
        classification_chain = prompt | self.llm.with_structured_output(QueryType)
        response = classification_chain.invoke({"question": state.user_input})
        state.query_type = dict(response).get("category")
        state.language = dict(response).get("language")
        return state

    def handle_general_query(self, state: PlannerState) -> PlannerState:
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(GENERAL_PROMPT),
            HumanMessagePromptTemplate.from_template("{user_input}")
        ])
        response = self.llm(prompt.format_messages(user_input=state.user_input, language=state.language))
        state.final_response = response.content
        return state

    def extract_event_details(self, state: PlannerState) -> PlannerState:
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(EVENT_EXTRACTION_PROMPT),
            HumanMessagePromptTemplate.from_template(
                "Extract exact details from: {user_input}\n"
                "Do not modify any specified values."
            )
        ])

        extraction_chain = prompt | self.llm.with_structured_output(EventDetails, method="function_calling")
        response = extraction_chain.invoke({"user_input": state.user_input})

        state.event_details = dict(response)
        print("Extracted event details:", state.event_details)

        return state

    def generate_event_suggestions(self, state: PlannerState) -> PlannerState:
        event_suggestor = LLMChain(llm=self.llm, prompt=self.EVENT_SUGGESTION_PROMPT_TEMPLATE, verbose=True)
        response = event_suggestor.invoke({"input": json.dumps(state.event_details), "language": state.language})
        state.final_response = response["text"]
        return state

    def execute_workflow(self, user_input: str) -> str:
        ans = self.planner_workflow.invoke({"user_input": user_input})
        return ans["final_response"]
