from typing import Any

from langchain.chains import LLMChain
from langchain.tools import BaseTool
from modules.prompts.few_shot_prompts import EventPromptFactory


class EventExtractor(BaseTool):
    name = "event_extractor"
    description = "Use this tool for the input related to event"
    return_direct = True
    event_extractor_chain: LLMChain

    def __init__(self, llm: Any):
        super(EventExtractor, self).__init__(
            event_extractor_chain=LLMChain(llm=llm, prompt=EventPromptFactory.EVENT_EXTRACTION_PROMPT_TEMPLATE, verbose=True))

    def _run(self, input: str):
        answer = self.event_extractor_chain.invoke({"input": input})
        return answer["text"]

    def _arun(self, project_id: int, input_name: str) -> None:
        raise NotImplementedError("This tool does not support async.")