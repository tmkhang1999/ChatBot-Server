from langchain.prompts import (
    ChatPromptTemplate, FewShotPromptTemplate, MessagesPlaceholder,
    SystemMessagePromptTemplate, HumanMessagePromptTemplate, PromptTemplate
)
from langchain_community.vectorstores import FAISS
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_openai import OpenAIEmbeddings

from modules.examples.budget_category import budget_category_examples, budget_category_prefix
from modules.examples.dependency import dependency_examples, dependency_prefix
from modules.examples.event_schedule import event_schedule_examples, event_schedule_prefix
from modules.examples.event_trial import event_extraction_examples, event_extraction_prefix, event_trial_prefix
from modules.examples.new_task_description import new_task_description_examples, new_task_description_prefix
from modules.examples.sql_database import sql_examples, sql_prefix
from modules.examples.task_description import task_description_examples, task_description_prefix

from langgraph.prebuilt import tools_condition
def create_example_selector(examples, embeddings, vector_store, k, input_keys):
    """Utility function to create a SemanticSimilarityExampleSelector."""
    return SemanticSimilarityExampleSelector.from_examples(
        examples,
        embeddings(),
        vector_store,
        k=k,
        input_keys=input_keys
    )


class EventPromptFactory:
    @staticmethod
    def _create_few_shot_prompt_template(example_selector, example_prompt, prefix, suffix, input_variables,
                                         example_separator="\n\n"):
        """Utility method to create a FewShotPromptTemplate."""
        return FewShotPromptTemplate(
            example_selector=example_selector,
            example_prompt=PromptTemplate.from_template(example_prompt),
            prefix=prefix,
            suffix=suffix,
            input_variables=input_variables,
            example_separator=example_separator
        )

    @classmethod
    def init_templates(cls):
        cls.EVENT_TRIAL_PROMPT_TEMPLATE = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(event_trial_prefix),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        cls.EVENT_EXTRACTION_PROMPT_TEMPLATE = cls._create_few_shot_prompt_template(
            create_example_selector(event_extraction_examples, OpenAIEmbeddings, FAISS, 3, ["input"]),
            "User: {input}\nAI: {answer}",
            event_extraction_prefix,
            "User: {input}\nAI:",
            ["input"]
        )

        cls.EVENT_SCHEDULE_PROMPT_TEMPLATE = cls._create_few_shot_prompt_template(
            create_example_selector(event_schedule_examples, OpenAIEmbeddings, FAISS, 1, ["input"]),
            "User: {input}\nAI: {answer}",
            event_schedule_prefix,
            "Use the history to answer the latest question\nHistory: {chat_history}\nUser: {input}\nAI:",
            ["input"]
        )

        cls.TASK_DESCRIPTION_PROMPT_TEMPLATE = cls._create_few_shot_prompt_template(
            create_example_selector(task_description_examples, OpenAIEmbeddings, FAISS, 1, ["input"]),
            "User: {input}\nAI: {answer}",
            task_description_prefix,
            "User: {input}\nAI: ",
            ["input"]
        )

        cls.NEW_TASK_DESCRIPTION_PROMPT_TEMPLATE = cls._create_few_shot_prompt_template(
            create_example_selector(new_task_description_examples, OpenAIEmbeddings, FAISS, 2, ["input"]),
            "User: {input}\nAI: {answer}",
            new_task_description_prefix,
            "User: {input}\nAI: ",
            ["input"]
        )

        cls.DEPENDENCY_PROMPT_TEMPLATE = cls._create_few_shot_prompt_template(
            create_example_selector(dependency_examples, OpenAIEmbeddings, FAISS, 1, ["input"]),
            "User: {input}\nAI: {answer}",
            dependency_prefix,
            "User: {input}\nAI: ",
            ["input"]
        )

        cls.BUDGET_CATEGORY_PROMPT_TEMPLATE = cls._create_few_shot_prompt_template(
            create_example_selector(budget_category_examples, OpenAIEmbeddings, FAISS, 1, ["input"]),
            "User: {input}\nAI: {answer}",
            budget_category_prefix,
            "User: {input}\nAI: ",
            ["input"]
        )

        SQL_PROMPT_TEMPLATE = cls._create_few_shot_prompt_template(
            create_example_selector(sql_examples, OpenAIEmbeddings, FAISS, 3, ["input", "project_id"]),
            "User input: {input}\nProject ID: {project_id}\nSQL query: {query}",
            sql_prefix,
            "Begin!",
            ["input", "project_id"]
        )

        cls.SQL_TEMPLATE = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate(prompt=SQL_PROMPT_TEMPLATE),
            HumanMessagePromptTemplate.from_template(
                "\nQuestion: {input}\nProject ID: {project_id}"
            ),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
