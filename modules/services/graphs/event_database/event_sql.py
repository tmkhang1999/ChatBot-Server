import logging

from langchain.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph

from modules.services.common import create_few_shot_prompt_template
from utils.settings import planz_db_info
from .examples import sql_examples
from .models import ClassificationOutput, QueryResponse, Query, QuestionType, SQLState, SchemaRelevance
from .prompt import CLASSIFICATION_PROMPT, GENERATE_PROMPT, FIX_PROMPT, TASK_PROMPT, EXAMPLE_PROMPT, \
    RELEVANT_TABLES_PROMPT, ANSWER_FILTER_PROMPT, BUDGET_PROMPT


class EventChatbot:
    def __init__(self, MODEL_NAME, database):
        self.memory_saver = MemorySaver()
        self.sql_workflow = self._create_workflow()
        self.database = database
        self.logger = self._setup_logging()

        self.MAX_ATTEMPTS_DEFAULT = 3
        self.INVALID_QUESTION_ERROR = "The question is not related to the database schema"
        self.MAX_ATTEMPTS_ERROR = "Maximum number of attempts reached without success"

        self.example_selector = SemanticSimilarityExampleSelector.from_examples(
            sql_examples,
            OpenAIEmbeddings(),
            FAISS,
            k=2,
            input_keys=["input", "project_id"],
        )

        self.classify_llm = ChatOpenAI(model=MODEL_NAME, temperature=0.3, verbose=True)
        self.query_llm = ChatOpenAI(model=MODEL_NAME, temperature=0.7, verbose=True)
        self.schema_llm = ChatOpenAI(model_name=MODEL_NAME, temperature=0.5, verbose=True)
        self.answer_llm = ChatOpenAI(model=MODEL_NAME, temperature=0.5, verbose=True)

    def _create_workflow(self) -> CompiledStateGraph:
        """Create the workflow graph."""
        # Initialize the graph
        workflow = StateGraph(SQLState)

        # Add nodes
        workflow.add_node("classify", self.classify)
        workflow.add_node("generate_query", self.generate_query)
        workflow.add_node("execute_query", self.execute_query)
        workflow.add_node("select_relevant_schemas", self.select_relevant_schemas)
        workflow.add_node("generate_answer", self.generate_answer)

        def should_process_query(state: SQLState):
            """Determine if the query needs SQL processing."""
            if state["question_type"] == QuestionType.NON_PROJECT:
                return "direct_answer"
            return "generate_query"

        def should_retry_query(state: SQLState):
            """Route based on query execution results."""
            query = state["current_query"]
            return "generate_answer" if query.is_valid else "retry_query"

        # Define edges
        workflow.set_entry_point("classify")
        workflow.add_conditional_edges(
            "classify",
            should_process_query,
            {
                "direct_answer": "generate_answer",
                "generate_query": "generate_query"
            }
        )

        workflow.add_edge("generate_query", "execute_query")
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

    def classify(self, state: SQLState) -> SQLState:
        """Classify the current question type."""
        self.logger.info("Classifying question type")
        print("Classifying question type")

        state["current_query"] = None
        state["attempts"] = 0

        classification_prompt_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(CLASSIFICATION_PROMPT),
            HumanMessagePromptTemplate.from_template(
                "Previous conversation:\n{history}\n\nCurrent question: {input}"
            ),
        ])

        classifier = classification_prompt_template | self.classify_llm.with_structured_output(ClassificationOutput,
                                                                                               method="function_calling")
        response = classifier.invoke({
            "input": state.get("current_question"),
            "history": state.get("history_context", "")
        })
        x = state.get("history_context", "")

        self.logger.info(f"History: {x}")
        print(f"History: {x}")

        # Update state and current turn
        state["question_type"] = dict(response).get("question_type")
        state["answer"] = dict(response).get("answer")
        state["requires_clarification"] = dict(response).get("requires_clarification")
        state["suggested_clarification"] = dict(response).get("suggested_clarification")

        return state

    def generate_query(self, state: SQLState) -> SQLState:
        """Generates SQL query with historical context."""
        self.logger.info("Generating query with history")
        print("Generating query with history")

        attempts = state.get("attempts", 0)
        max_attempts = state.get("max_attempts", self.MAX_ATTEMPTS_DEFAULT)

        self.logger.info(f"Attempt {attempts + 1} of {max_attempts}")
        print(f"Attempt {attempts + 1} of {max_attempts}")

        question_type = state["question_type"]
        project_id = state["project_id"]
        current_query = state.get("current_query", None)
        table_names = planz_db_info["tables"]

        # Choose appropriate instruction template
        if not current_query:
            if question_type == QuestionType.TASK_REQUEST:
                list_names = self.database.run(
                    f"SELECT DISTINCT u.first_name, u.last_name FROM planz_users u "
                    f"JOIN planz_tasks t ON u.id = t.assigned_to WHERE t.project_id = {project_id}"
                )
                instructions = GENERATE_PROMPT + TASK_PROMPT.format(list_names=list_names)
            elif question_type == QuestionType.BUDGET_REQUEST:
                budget_categories = self.database.run(
                    f"SELECT title FROM planz_budgets WHERE project_id = {project_id} ORDER BY title;"
                )
                instructions = GENERATE_PROMPT + BUDGET_PROMPT.format(budget_categories=budget_categories)
            else:
                instructions = GENERATE_PROMPT

            instructions = instructions.format(table_names=table_names) + EXAMPLE_PROMPT
        else:
            info = state["tables_info"].replace("{", "{{").replace("}", "}}")
            error_info = str(current_query.error_info).replace("{", "{{").replace("}", "}}")
            instructions = FIX_PROMPT.format(
                info=info,
                error_info=error_info,
                table_names=table_names
            ) + EXAMPLE_PROMPT

        # Generate query with historical context
        query_generation_template = create_few_shot_prompt_template(
            self.example_selector,
            "User input: {input}\nProject ID: {project_id}\nSQL query: {query}",
            instructions,
            "\nQuestion: {input}\nProject ID: {project_id}",
            ["input", "project_id", "user_id", "workspace_link", "s", " "]
        )

        x = self.example_selector.select_examples({"input": state["current_question"], "project_id": "1"})
        self.logger.info(f"Examples: {x}")
        print(f"Examples: {x}")

        generator = query_generation_template | self.query_llm.with_structured_output(QueryResponse)
        gen_response = generator.invoke({
            "input": state["current_question"],
            "project_id": project_id,
            # "history": state.get("history_context", ""),
            "user_id": state["user_id"],
            "workspace_link": state["workspace_link"],
            "s": "",
            " ": ""
        })

        # Update state and current turn
        query = Query(
            statement=dict(gen_response).get("statement"),
            reasoning=dict(gen_response).get("reasoning")
        )
        state["current_query"] = query
        self.logger.info(query)
        print(query)
        return state

    def execute_query(self, state: SQLState) -> SQLState:
        """Execute the generated SQL query."""
        self.logger.info("Executing query")
        print("Executing query")

        attempts = state.get("attempts", 0)
        max_attempts = state.get("max_attempts", self.MAX_ATTEMPTS_DEFAULT)

        self.logger.info(f"Attempt {attempts + 1} of {max_attempts}")
        print(f"Attempt {attempts + 1} of {max_attempts}")

        query = state["current_query"]
        if not query.statement:
            state["error_message"] = query.error
            query.is_valid = True
            return state

        try:
            query.result = self.database._execute(query.statement)
            query.is_valid = True

            # Reset attempts after success
            state["attempts"] = 0
            return state
        except Exception as e:
            query.error = str(e)
            query.is_valid = False
            self.logger.error(f"Query execution failed: {e}")

            # Increment the attempts after a failed execution
            state["attempts"] = attempts + 1

            # If maximum attempts are reached, return with an error message
            if state["attempts"] >= max_attempts:
                query.is_valid = True
                state["error_message"] = "Maximum number of attempts reached without success"
                return state

            # If not reached max attempts, return updated state for retry
            return state

    def select_relevant_schemas(self, state: SQLState) -> SQLState:
        self.logger.info("Retrying")

        attempts = state.get("attempts", 0)
        max_attempts = state.get("max_attempts", self.MAX_ATTEMPTS_DEFAULT)
        self.logger.info(f"Attempt {attempts + 1} of {max_attempts}")

        question = state["current_question"]
        schema_relevance_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(RELEVANT_TABLES_PROMPT),
            HumanMessagePromptTemplate.from_template("Question: {question}")
        ])

        schema_classifier = schema_relevance_template | self.schema_llm.with_structured_output(SchemaRelevance)
        schema_relevance = schema_classifier.invoke({
            "question": question,
            "table_names": self.database.get_usable_table_names()
        })

        relevant_tables = dict(schema_relevance).get("relevant_tables")
        if not relevant_tables:
            self.logger.error(f"No relevant tables found for question: {question}")
            state["error_message"] = "No relevant tables found for the question."
            state["tables_info"] = None
            return state
        else:
            state["tables_info"] = self.database.get_table_info(relevant_tables)

            return state

    def generate_answer(self, state: SQLState) -> SQLState:
        """Generate final answer based on query results and update conversation history."""
        self.logger.info("Generating answer")
        print("Generating answer")

        def update_history(state: SQLState) -> None:
            """Update history_context with the current question."""
            if state.get("current_question"):
                turns = state.get("history_context", "")
                turns = turns.split("\n---\n") if turns else []

                turns.append(state["current_question"])
                context_window = state.get("context_window", len(turns))
                turns = turns[-context_window:]
                state["history_context"] = "\n---\n".join(turns)

        # Check for any error messages in the state.
        if error_message := state.get("error_message"):
            self.logger.error(f"Error encountered: {error_message}")
            state["answer"] = error_message
            update_history(state)
            return state

        # Handle simple question types that don't need SQL query generation.
        if state["question_type"] == QuestionType.NON_PROJECT:
            self.logger.info("Simple question type detected, returning pre-set answer.")
            if state["requires_clarification"]:
                state["answer"] = state["suggested_clarification"]
                state["requires_clarification"] = False
            else:
                state["answer"] = state["answer"]
            update_history(state)
            return state

        answer_template = PromptTemplate(template=ANSWER_FILTER_PROMPT,
                                         input_variables=["query_details", "question"])

        self.logger.info(state["current_query"].result)
        print(state["current_query"].result)

        answer_filter = answer_template | self.answer_llm
        response = answer_filter.invoke({
            "question": state["current_question"],
            "query_details": state["current_query"].result
        })

        state["answer"] = response.content
        update_history(state)
        return state

    def execute_workflow(self, conversation_id: str, question: str, project_id: str, user_id: int,
                         workspace_link: str) -> str:
        config = {"configurable": {"thread_id": conversation_id}}
        input = {"current_question": question,
                 "project_id": project_id,
                 "user_id": user_id,
                 "workspace_link": workspace_link,
                 "max_attempts": 3,
                 "context_window": 3}
        response = self.sql_workflow.invoke(input, config)
        return response["answer"]
