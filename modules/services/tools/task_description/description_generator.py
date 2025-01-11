from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings

from modules.services.common import create_few_shot_prompt_template, create_example_selector
from .examples import task_description_examples
from .prompt import TASK_DESCRIPTION_PROMPT


class DescriptionGenerator:
    def __init__(self, MODEL_NAME, TEMPERATURE):
        self.llm = ChatOpenAI(model_name=MODEL_NAME, temperature=TEMPERATURE)
        self.TASK_DESCRIPTION_PROMPT_TEMPLATE = create_few_shot_prompt_template(
            create_example_selector(task_description_examples, OpenAIEmbeddings, FAISS, 2, ["input"]),
            "User: {input}\nAI: {answer}",
            TASK_DESCRIPTION_PROMPT,
            "User: {input}\nAI: ",
            ["input"]
        )
        self.chain = self.TASK_DESCRIPTION_PROMPT_TEMPLATE | self.llm

    def execute(self, user_input: str) -> str:
        ans = self.chain.invoke({"input": user_input})
        return ans.content
