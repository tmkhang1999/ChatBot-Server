from modules.examples.common import load_and_merge_examples

folder_path = "./modules/examples/budget_category"
budget_category_examples = load_and_merge_examples(folder_path)

budget_category_prefix = """
    Act as a professional event planner. Your task is to:

    Understand the language of the user input, then answer in the same language.
    Assign the most suitable budget category from the list provided to each task in the event schedule.
    Present the output in a dictionary format where each key is the task index, and the value is the budget category.
    Budget Categories: ["Venue", "Food and Drinks", "Transportation", "Decorations and Ambiance", "Entertainment", "Marketing and Promotion", "Staffing", "Technology", "Accommodation", "Printing and Signage", "Logistics", "Others"]

    Here are some examples:
    """