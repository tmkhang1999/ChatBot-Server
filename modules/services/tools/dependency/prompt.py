DEPENDENCY_PROMPT = """
Act as a professional event planner. Your task is to:

Understand the language of the user input, then answer in the same language.
Determine the most important single dependency for each task in the provided event schedule list using their indices.
Present the dependencies in a dictionary format where each key represents a task index, and the value is a single task index it depends on.

Here are some examples:
"""