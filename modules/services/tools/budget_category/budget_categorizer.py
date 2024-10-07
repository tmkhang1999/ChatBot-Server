from langchain.chains.llm import LLMChain
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings

from modules.services.common import create_few_shot_prompt_template, create_example_selector
from .examples import budget_category_examples
from .prompt import BUDGET_CATEGORY_PROMPT

BUDGET_CATEGORY_PROMPT_TEMPLATE = create_few_shot_prompt_template(
    create_example_selector(budget_category_examples, OpenAIEmbeddings, FAISS, 2, ["input"]),
    "User: {input}\nAI: {answer}",
    BUDGET_CATEGORY_PROMPT,
    "User: {input}\nAI: ",
    ["input"]
)


class BudgetCategorizer:
    def __init__(self, MODEL_NAME, TEMPERATURE):
        self.llm = ChatOpenAI(model_name=MODEL_NAME, temperature=TEMPERATURE)
        self.chain = LLMChain(
            prompt=BUDGET_CATEGORY_PROMPT_TEMPLATE,
            llm=self.llm,
            verbose=True
        )

    def execute(self, user_input: str) -> str:
        ans = self.chain.invoke({"input": user_input})
        return ans["text"]
