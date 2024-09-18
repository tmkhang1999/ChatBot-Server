from modules.examples.common import load_and_merge_examples

folder_path = "./modules/examples/new_task_description"
new_task_description_examples = load_and_merge_examples(folder_path)

new_task_description_prefix = """
    Act as a professional event planner. Your task is to:
    
    Understand the language of the user input, then answer in the same language.
    Provide a comprehensive list of steps for a task of an event. 
    There's no need to explain each step in detail.
    
    Here are some examples:
    """