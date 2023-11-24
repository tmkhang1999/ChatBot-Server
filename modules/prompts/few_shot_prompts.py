from langchain.prompts import FewShotPromptTemplate
from langchain.prompts import PromptTemplate
from modules.prompts.examples import EventEntitiesTemplate, IrrelevantTemplate, EventScheduleTemplate

example_template = """
User: {query}
AI: {answer}
"""

example_prompt = PromptTemplate(
    input_variables=["query", "answer"],
    template=example_template
)


class EventPromptFactory:
    EVENT_ENTITY_PROMPT_TEMPLATE = FewShotPromptTemplate(
        examples=EventEntitiesTemplate.examples,
        example_prompt=example_prompt,
        prefix=EventEntitiesTemplate.prefix,
        suffix=EventEntitiesTemplate.suffix,
        input_variables=["input"],
        example_separator="\n\n"
    )

    IRRELEVANT_PROMPT_TEMPLATE = FewShotPromptTemplate(
        examples=IrrelevantTemplate.examples,
        example_prompt=example_prompt,
        prefix=IrrelevantTemplate.prefix,
        suffix=IrrelevantTemplate.suffix,
        input_variables=["input"],
        example_separator="\n\n"
    )

    EVENT_SCHEDULE_PROMPT_TEMPLATE = FewShotPromptTemplate(
        examples=EventScheduleTemplate.examples,
        example_prompt=example_prompt,
        prefix=EventScheduleTemplate.prefix,
        suffix=EventScheduleTemplate.suffix,
        input_variables=["input"],
        example_separator="\n\n"
    )

    prompt_infos = [
        {
            "name": "event",
            "description": "Good for answering specific task related to planning. Note that: Not suitable for "
                           "broader question about the general concept of event planning",
            "prompt": EVENT_ENTITY_PROMPT_TEMPLATE,
        }
    ]
