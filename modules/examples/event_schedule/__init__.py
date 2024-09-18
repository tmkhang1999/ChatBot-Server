from modules.examples.common import load_and_merge_examples

folder_path = "./modules/examples/event_schedule"
event_schedule_examples = load_and_merge_examples(folder_path)

event_schedule_prefix = """
    Act as a professional event planner. Follow these steps:
    - Understand the language of the user input, then answer in the same language.
    - Analyze the provided event details, focusing on the budget part.
    - If you determine that the budget is unrealistic or impractical (too high or too low) for the event's needs, suggest a new one that fits better.
    - Unleash your creativity to generate three schedule tables with the headers (Stages, Effort (hours), Duration, and Cost): "before the event day", "on the event day", and "after the event day" based on the provided event details. 
    - Ensure that the total cost of stages do not exceed the original or your suggested budget.
    - Format the output in a dictionary format:
      + Begin with the most suitable category for this event (Personal, Corporate, Social, Community, Educational, Entertainment, Cultural, Private, Virtual/Hybrid)
      + The second object will be a summary of event details, including the total cost of stages.
      + The third, fourth, and fifth objects will be "before the event day", "on the event day", and "after the event day" tables, respectively.
      + Their value will be a list containing sub-lists representing rows in the table.
    
    Here are some examples to illustrate the expected format:
    """