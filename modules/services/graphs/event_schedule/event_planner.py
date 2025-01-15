import logging

from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END, START
from langgraph.graph.state import CompiledStateGraph

from modules.services.common import create_few_shot_prompt_template, create_example_selector
from .examples import event_schedule_examples
from .models import ScheduleUpdateList, EventBudget, EventSummary, ScheduleTables, ScheduleCheckResult, ScheduleState
from .prompt import UPDATE_PROMPT, BUDGET_RECOMMENDATION_PROMPT, EVENT_SUMMARY_PROMPT, SCHEDULE_GENERATION_PROMPT, \
    SCHEDULE_CHECK_PROMPT

EVENT_SCHEDULE_PROMPT_TEMPLATE = create_few_shot_prompt_template(
    create_example_selector(event_schedule_examples, OpenAIEmbeddings, FAISS, 1, ["input"]),
    "User: {input}\nAI: {answer}",
    SCHEDULE_GENERATION_PROMPT,
    "\nUser: {input}\nAI:",
    ["input"]
)


class EventPlanner:
    def __init__(self, MODEL_NAME, TEMPERATURE):
        self.memory_saver = MemorySaver()
        self.planner_workflow = self._create_workflow()
        self.llm = ChatOpenAI(model_name=MODEL_NAME, temperature=TEMPERATURE)

    def _create_workflow(self) -> CompiledStateGraph:
        # Define the graph
        workflow = StateGraph(ScheduleState)

        # Add nodes to the graph
        workflow.add_node("process_additional_info", self.process_update_info)
        workflow.add_node("apply_table_updates", self.apply_table_updates)
        workflow.add_node("recommend_new_budget", self.recommend_new_budget)
        workflow.add_node("summarize_event", self.summarize_event)
        workflow.add_node("generate_schedules", self.generate_schedules)
        # workflow.add_node("check_schedules", self.check_schedules)

        # Set the entry point
        def determine_entry_point(state: ScheduleState):
            if "additional_info" in state:
                return "process_additional_info"
            else:
                return "recommend_new_budget"

        workflow.add_conditional_edges(
            START,
            determine_entry_point,
            {
                "process_additional_info": "process_additional_info",
                "recommend_new_budget": "recommend_new_budget"
            }
        )

        # Define the edges of the graph
        workflow.add_edge("process_additional_info", "apply_table_updates")
        workflow.add_edge("apply_table_updates", END)

        workflow.add_edge("recommend_new_budget", "generate_schedules")
        workflow.add_edge("generate_schedules", "summarize_event")
        workflow.add_edge("summarize_event", END)

        return workflow.compile(checkpointer=self.memory_saver)

    def process_update_info(self, state: ScheduleState) -> ScheduleState:
        # Create a PydanticOutputParser
        output_parser = PydanticOutputParser(pydantic_object=ScheduleUpdateList)

        # Prepare the input for the LLM prompt
        prompt_input = {
            "before_event_day": state["before_event_day"],
            "on_event_day": state["on_event_day"],
            "after_event_day": state["after_event_day"],
            "additional_info": state["additional_info"],
            "format_instructions": output_parser.get_format_instructions()
        }

        # Create the prompt template
        prompt = PromptTemplate(
            template=UPDATE_PROMPT + "\n{format_instructions}",
            input_variables=["before_event_day", "on_event_day", "after_event_day", "additional_info"],
            partial_variables={"format_instructions": output_parser.get_format_instructions()}
        )

        # Set up the LLM chain
        chain = LLMChain(llm=self.llm, prompt=prompt)

        # Invoke the LLM and get output
        result = chain.run(prompt_input)

        # Parse the output
        try:
            parsed_output = output_parser.parse(result)
            state["parsed_table_updates"] = parsed_output.updates
        except Exception as e:
            print(f"Error parsing LLM output: {e}")
            print(f"Raw LLM output: {result}")
            state["parsed_table_updates"] = []

        return state

    def apply_table_updates(self, state: ScheduleState) -> ScheduleState:
        updates = state.get("parsed_table_updates", [])

        for update in updates:
            table_name = update.table
            row_index = update.row_index
            new_values = update.new_values

            if table_name not in ["before_event_day", "on_event_day", "after_event_day"]:
                logging.warning(f"Invalid table name: {table_name}")
                continue

            table = state[table_name]

            # Perform the specified operation
            if update.operation == "update":
                if 0 <= row_index < len(table):
                    table[row_index] = new_values
                else:
                    logging.warning(f"Invalid row index for update: {row_index}")

            elif update.operation == "insert":
                if 0 <= row_index <= len(table):
                    table.insert(row_index, new_values)
                else:
                    logging.warning(f"Invalid row index for insert: {row_index}")
            else:
                logging.warning(f"Unknown operation: {update.operation}")

            total_cost = sum(float(row[3].replace(',', '')) for row in table[1:-1])
            table[-1][3] = str(total_cost)

            total_effort = sum(float(row[1].replace(',', '')) for row in table[1:-1])
            table[-1][1] = str(total_effort)

        logging.info("Updated schedules:")
        for table_name in ["before_event_day", "on_event_day", "after_event_day"]:
            logging.info(f"{table_name}:\n{state[table_name]}")

        return state

    def recommend_new_budget(self, state: ScheduleState) -> ScheduleState:
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(BUDGET_RECOMMENDATION_PROMPT),
            HumanMessagePromptTemplate.from_template("{event_details}")
        ])
        budget_recommender = prompt | self.llm.with_structured_output(EventBudget)
        response = budget_recommender.invoke({"event_details": state["event_details"]})
        response = dict(response)
        state["new_budget"] = response["new_budget"]
        state["original_budget"] = response["original_budget"]
        state["currency"] = response["currency"]

        print(response)
        return state

    def generate_schedules(self, state: ScheduleState) -> ScheduleState:
        schedule_node = EVENT_SCHEDULE_PROMPT_TEMPLATE | self.llm.with_structured_output(ScheduleTables)
        input_prompt = f"{state['event_details']}\nNew suggested budget: {state['new_budget']}" if "new_budget" in state else \
            state['event_details']
        schedules = schedule_node.invoke({"input": input_prompt})

        state['new_budget'] = 0
        for table_name in ["before_event_day", "on_event_day", "after_event_day"]:
            state[table_name] = dict(schedules)[table_name]
            table = state[table_name]

            if len(table) > 1:  # Check if the table has more than just the header row
                total_cost = sum(float(row[3].replace(',', '')) for row in table[1:-1])
                table[-1][3] = str(total_cost)

                state['new_budget'] = state['new_budget'] + total_cost
                
                # total_effort = sum(float(row[1].replace(',', '')) for row in table[1:-1])
                # table[-1][1] = str(total_effort)
            else:
                logging.warning(f"{table_name} schedule is empty. Only contains header row.")

        return state

    def check_schedules(self, state: ScheduleState) -> ScheduleState:
        output_parser = PydanticOutputParser(pydantic_object=ScheduleCheckResult)

        prompt = PromptTemplate(
            template=SCHEDULE_CHECK_PROMPT + "\n{format_instructions}",
            input_variables=["budget", "currency", "before_event_day", "on_event_day", "after_event_day"],
            partial_variables={"format_instructions": output_parser.get_format_instructions()}
        )

        check_chain = LLMChain(llm=self.llm, prompt=prompt)
        budget = state["new_budget"] if state["new_budget"] is not None else state["original_budget"]
        result = check_chain.run({
            "budget": budget,
            "currency": state["currency"],
            "before_event_day": state["before_event_day"],
            "on_event_day": state["on_event_day"],
            "after_event_day": state["after_event_day"]
        })

        try:
            parsed_result = output_parser.parse(result)
        except Exception as e:
            logging.error(f"Error parsing LLM output: {e}")
            logging.error(f"Raw LLM output: {result}")
            # Handle the error case, perhaps by setting default values
            parsed_result = ScheduleCheckResult(is_within_budget=False, total_cost=0, adjustments=[])

        print(parsed_result)
        if not parsed_result.is_within_budget:
            # Apply the suggested adjustments
            for adjustment in parsed_result.adjustments:
                table = state[adjustment.table]
                row = table[adjustment.row_index]
                column_index = ["Stages", "Effort (hours)", "Duration", "Cost"].index(adjustment.column)
                row[column_index] = str(adjustment.new_value)

            # Update the total cost row in each table
            state['new_budget'] = 0
            for table_name in ["before_event_day", "on_event_day", "after_event_day"]:
                table = state[table_name]

                total_cost = sum(float(row[3].replace(',', '')) for row in table[1:-1])
                table[-1][3] = str(total_cost)

                state['new_budget'] = state['new_budget'] + total_cost

                total_effort = sum(float(row[1].replace(',', '')) for row in table[1:-1])
                table[-1][1] = str(total_effort)

            # Add a comment about the adjustments
            logging.info(
                f"Adjustments were made to bring the total cost from {parsed_result.total_cost} to within the budget of {budget}.")
        else:
            logging.info(
                f"The current schedule is within the budget of {parsed_result}. Total cost: {parsed_result.total_cost}.")

        return state

    def summarize_event(self, state: ScheduleState) -> ScheduleState:
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(EVENT_SUMMARY_PROMPT),
            HumanMessagePromptTemplate.from_template("{event_details}")
        ])

        input_prompt = f"{state['event_details']}\nNew suggested budget: {state['new_budget']}" if "new_budget" in state else \
            state['event_details']
        event_analysis_node = prompt | self.llm.with_structured_output(EventSummary)
        analysis = event_analysis_node.invoke({"event_details": input_prompt})
        analysis = dict(analysis)

        state["category"] = analysis["category"]
        state["command"] = analysis["command"]

        print(analysis)
        return state

    def execute_workflow(self, conversation_id: str, user_input: dict) -> dict:
        config = {"configurable": {"thread_id": conversation_id}}
        if "Additional information" in user_input:
            ans = self.planner_workflow.invoke({"additional_info": user_input["Additional information"]}, config)
        else:
            ans = self.planner_workflow.invoke({"event_details": user_input}, config)

        final_response = {
            "Command": ans["command"],
            "Category": ans["category"],
            "Currency": ans["currency"],
            "Before the event day": ans["before_event_day"],
            "On the event day": ans["on_event_day"],
            "After the event day": ans["after_event_day"],
        }
        return final_response
