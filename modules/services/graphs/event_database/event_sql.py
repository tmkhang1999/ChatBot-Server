import logging

from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_core.prompts import AIMessagePromptTemplate
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph

from modules.services.common import create_few_shot_prompt_template
from .examples import sql_examples
from .models import ClassificationOutput, QueryResponse, Query, QuestionType, SQLState, SchemaRelevance
from .prompt import CLASSIFICATION_PROMPT, GENERATE_PROMPT, FIX_PROMPT, TASK_PROMPT, EXAMPLE_PROMPT, QUERY_CHECK_PROMPT, \
    RELEVANT_TABLES_PROMPT, ANSWER_FILTER_PROMPT, BUDGET_PROMPT, CONTEXTUALIZE_PROMPT


class EventChatbot:
    def __init__(self, MODEL_NAME, TEMPERATURE, database):
        self.memory_saver = MemorySaver()
        self.sql_workflow = self._create_workflow()
        self.llm = ChatOpenAI(model_name=MODEL_NAME, temperature=TEMPERATURE)
        self.database = database
        self.logger = self._setup_logging()

        self.MAX_ATTEMPTS_DEFAULT = 3
        self.INVALID_QUESTION_ERROR = "The question is not related to the database schema"
        self.MAX_ATTEMPTS_ERROR = "Maximum number of attempts reached without success"

        self.example_selector = SemanticSimilarityExampleSelector.from_examples(
            sql_examples,
            OpenAIEmbeddings(),
            FAISS,
            k=1,
            input_keys=["input", "project_id"],
        )

    def _create_workflow(self) -> CompiledStateGraph:
        """Create the workflow graph."""
        # Initialize the graph
        workflow = StateGraph(SQLState)

        # Add nodes
        workflow.add_node("contextualize", self.contextualize)
        workflow.add_node("classify", self.classify)
        workflow.add_node("generate_query", self.generate_query)
        workflow.add_node("execute_query", self.execute_query)
        workflow.add_node("select_relevant_schemas", self.select_relevant_schemas)
        workflow.add_node("generate_answer", self.generate_answer)

        def should_process_query(state: SQLState):
            """Determine if the query needs SQL processing."""
            if state["question_type"] in [QuestionType.GREETING, QuestionType.OUT_OF_CONTEXT,
                                          QuestionType.ASK_ABOUT_CAPABILITIES, QuestionType.UNCLEAR]:
                return "direct_answer"
            return "generate_query"

        def should_retry_query(state: SQLState):
            """Route based on query execution results."""
            query = state["query"]
            return "generate_answer" if query.is_valid else "retry_query"

        # Define edges
        workflow.set_entry_point("contextualize")
        workflow.add_edge("contextualize", "classify")
        workflow.add_conditional_edges(
            "classify",
            should_process_query,
            {
                "direct_answer": "generate_answer",
                "generate_query": "generate_query"
            }
        )

        # Generate Query -> Execute Query
        workflow.add_edge("generate_query", "execute_query")

        # Execute Query -> Conditional routing
        workflow.add_conditional_edges(
            "execute_query",
            should_retry_query,
            {
                "generate_answer": "generate_answer",
                "retry_query": "select_relevant_schemas"
            }
        )
        workflow.add_edge("select_relevant_schemas", "generate_query")
        workflow.add_edge("generate_answer", END)

        return workflow.compile(checkpointer=self.memory_saver)

    @staticmethod
    def _setup_logging(log_file: str = 'sql_agent.log') -> logging.Logger:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger

    def contextualize(self, state: SQLState) -> SQLState:
        self.logger.info("Contextualizing query")

        # Initialize messages if they don't exist
        if "messages" not in state:
            state["messages"] = []
            state["messages"].append(state["question"])
            return state

        # Prepare the bot and pass the chat history along with the current question
        bot = ChatPromptTemplate.from_template(CONTEXTUALIZE_PROMPT) | self.llm
        response = bot.invoke({"input": state["question"], "messages": state["messages"]})
        state["question"] = response.content
        state["messages"].append(state["question"])
        state["query"] = None
        print(state["question"])
        return state

    def classify(self, state: SQLState) -> SQLState:
        self.logger.info("Classifying query")

        max_attempts = state.get("max_attempts", 0)
        state["max_attempts"] = max_attempts if max_attempts > 0 else self.MAX_ATTEMPTS_DEFAULT

        classification_prompt_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(CLASSIFICATION_PROMPT),
            HumanMessagePromptTemplate.from_template("{input}"),
        ])

        classifier = classification_prompt_template | self.llm.with_structured_output(ClassificationOutput)
        response = classifier.invoke({"input": state["question"]})
        state["question_type"] = dict(response).get("question_type")
        state["answer"] = dict(response).get("answer")
        return state

    def generate_query(self, state: SQLState) -> SQLState:
        """Generate or fix a SQL query based on the current state."""
        self.logger.info("Generating query")

        question_type = state["question_type"]
        project_id = state["project_id"]
        query = state.get("query", None)

        if not query:
            if question_type == QuestionType.TASK_REQUEST:
                list_names = self.database.run(
                    f"SELECT DISTINCT u.first_name, u.last_name FROM planz_users u JOIN planz_tasks t ON u.id = t.assigned_to WHERE t.project_id = {project_id}")
                instructions = GENERATE_PROMPT + TASK_PROMPT.format(list_names=list_names) + EXAMPLE_PROMPT
            elif question_type == QuestionType.BUDGET_REQUEST:
                budget_categories = self.database.run(
                    f"SELECT title FROM planz_budgets WHERE project_id = {project_id} ORDER BY title;"
                )
                instructions = GENERATE_PROMPT + BUDGET_PROMPT.format(
                    budget_categories=budget_categories) + EXAMPLE_PROMPT
            else:
                instructions = GENERATE_PROMPT + EXAMPLE_PROMPT
        else:
            instructions = FIX_PROMPT.format(info=state["tables_info"], error_info=query.error_info) + EXAMPLE_PROMPT

        # Create prompt with few-shot examples
        query_generation_template = create_few_shot_prompt_template(
            self.example_selector,
            "User input: {input}\nProject ID: {project_id}\nSQL query: {query}",
            instructions,
            "\nPrevious Questions: {messages}\nQuestion: {input}\nProject ID: {project_id}",
            ["messages", "input", "project_id"]
        )

        # Generate and validate query
        generator = query_generation_template | self.llm.with_structured_output(QueryResponse)
        gen_response = generator.invoke({
            "input": state["question"],
            "messages": state["messages"],
            "project_id": project_id,
            "user_id": state["user_id"],
            "workspace_link": state["workspace_link"]
        })

        self.logger.info("Checking query")

        # Check query
        checker_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(QUERY_CHECK_PROMPT),
            AIMessagePromptTemplate.from_template(
                "\nQuery: {query}\nReasoning: {reason}")
        ])

        checker = checker_template | self.llm.with_structured_output(QueryResponse)
        checker_response = checker.invoke({
            "query": dict(gen_response).get("statement"),
            "reason": dict(gen_response).get("reasoning")
        })

        # Compare
        was_corrected = dict(gen_response).get("statement") != dict(checker_response).get("statement")

        final_reasoning = (dict(gen_response).get('reasoning') + "" if not was_corrected
                           else f"First: {dict(gen_response).get('reasoning')}\nCorrection: {dict(checker_response).get('reasoning')}")

        query = Query(
            statement=dict(checker_response).get("statement"),
            reasoning=final_reasoning
        )
        self.logger.info(f"Generated query: {query.info}")
        state["query"] = query

        return state

    def execute_query(self, state: SQLState) -> SQLState:
        """Execute the generated SQL query."""
        self.logger.info("Executing query")

        attempts = state.get("attempts", 0)
        max_attempts = state.get("max_attempts", self.MAX_ATTEMPTS_DEFAULT)
        query = state["query"]

        self.logger.info(f"Attempt {attempts + 1} of {max_attempts}")

        if not query.statement:
            state["error_message"] = query.error
            query.is_valid = True
            return state

        try:
            query.result = self.database.run(query.statement)
            query.is_valid = True
            # Reset attempts after success
            state["attempts"] = 0
            return state
        except Exception as e:
            query.error = str(e)
            query.is_valid = False
            self.logger.error(f"Query execution failed: {e}")

            # Increment the attempts after a failed execution
            state["attempts"] = attempts + 1  # Increment attempts

            # If maximum attempts are reached, return with an error message
            if state["attempts"] >= max_attempts:
                query.is_valid = True
                state["error_message"] = "Maximum number of attempts reached without success"
                return state

            # If not reached max attempts, return updated state for retry
            return state

    def select_relevant_schemas(self, state: SQLState) -> SQLState:
        self.logger.info("Retrying")

        question = state["question"]
        schema_relevance_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(RELEVANT_TABLES_PROMPT),
            HumanMessagePromptTemplate.from_template("Question: {question}")
        ])

        schema_classifier = schema_relevance_template | self.llm.with_structured_output(SchemaRelevance)
        schema_relevance = schema_classifier.invoke({
            "question": question,
            "table_names": self.database.get_usable_table_names()
        })
        relevant_tables = dict(schema_relevance).get("relevant_tables")

        attempts = state.get("attempts", 0)
        if not relevant_tables:
            self.logger.error(f"No relevant tables found for question: {question}")
            state["error_message"] = "No relevant tables found for the question."
            state["tables_info"] = None
            return state
        else:
            state["tables_info"] = self.database.get_table_info(relevant_tables)

            return state

    def generate_answer(self, state: SQLState) -> SQLState:
        """Generate final answer based on query results."""
        self.logger.info("Generating answer")

        # Check for any error messages in the state
        if error_message := state.get("error_message"):
            self.logger.error(f"Error encountered: {error_message}")
            state["answer"] = error_message
            return state

        # Handle simple question types that don't need SQL query generation
        if state["question_type"] in [QuestionType.GREETING, QuestionType.OUT_OF_CONTEXT,
                                      QuestionType.ASK_ABOUT_CAPABILITIES, QuestionType.UNCLEAR]:
            self.logger.info("Simple question type detected, returning pre-set answer.")
            return state

        answer_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(ANSWER_FILTER_PROMPT),
            HumanMessagePromptTemplate.from_template("Question: {input}")
        ])

        answer_filter = answer_template | self.llm
        response = answer_filter.invoke({"input": state["question"], "query_info": state["query"].info})
        state["answer"] = response.content
        return state

    def execute_workflow(self, conversation_id: str, question: str, project_id: str, user_id: int,
                         workspace_link: str, max_attempts: int = 3) -> str:
        config = {"configurable": {"thread_id": conversation_id}}
        input = {"question": question,
                 "project_id": project_id,
                 "user_id": user_id,
                 "workspace_link": workspace_link,
                 "max_attempts": max_attempts}
        response = self.sql_workflow.invoke(input, config)
        return response["answer"]
