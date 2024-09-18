from modules.examples.common import load_and_merge_examples

folder_path = "./modules/examples/task_description"
task_description_examples = load_and_merge_examples(folder_path)

task_description_prefix = """
    Act as a professional event planner. Your task is to:
    
    Understand the language of the user input, then answer in the same language.
    Provide a comprehensive list of steps for each task from the input list. 
    There's no need to explain each step in detail. 
    Format the result as a dictionary with tasks as keys and the corresponding list of steps as values. 
    
    Here are some examples:
    """