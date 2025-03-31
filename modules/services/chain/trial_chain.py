from langchain_openai import ChatOpenAI

from modules.services.chain.base_chain import StreamingConversationChain
from modules.services.graphs import EventSuggester, EventPlanner
from modules.services.tools import BudgetCategorizer, DependencyDetector, DescriptionGenerator


class TrialConversationChain(StreamingConversationChain):
    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 0.7):
        super().__init__(model_name, temperature)
        self.thread_ids = set()
        self.event_suggester = EventSuggester(MODEL_NAME=model_name, TEMPERATURE=0.3)
        self.event_planner = EventPlanner(MODEL_NAME=model_name, TEMPERATURE=temperature)
        self.budget_categorizer = BudgetCategorizer(MODEL_NAME=model_name, TEMPERATURE=temperature)
        self.dependency_detector = DependencyDetector(MODEL_NAME=model_name, TEMPERATURE=temperature)
        self.description_generator = DescriptionGenerator(MODEL_NAME=model_name, TEMPERATURE=temperature)

    def suggest_event(self, message: str) -> str:
        return self.event_suggester.execute_workflow(message)

    def generate_schedule(self, conversation_id: str, event_details: dict) -> dict:
        return self.event_planner.execute_workflow(conversation_id=conversation_id, user_input=event_details)

    def generate_description(self, message: str) -> str:
        return self.description_generator.execute(user_input=message)

    def detect_dependency(self, message: str) -> str:
        return self.dependency_detector.execute(user_input=message)

    def categorize_budget(self, message: str) -> str:
        return self.budget_categorizer.execute(user_input=message)
