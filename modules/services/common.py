import os
import glob
import importlib.util

from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate


def load_and_merge_examples(directory_path):
    merged_examples = []

    # Construct the pattern to match all Python files in the directory
    pattern = os.path.join(directory_path, "*.py")

    # Use glob to find all files matching the pattern
    for file_path in glob.glob(pattern):
        # Skip __init__.py.py files
        if "__init__.py" in file_path:
            continue

        # Dynamically import the module based on the file path
        module_name = os.path.basename(file_path)[:-3]  # Remove '.py' from the end
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Inspect all attributes of the module and merge if they are lists
        for attr_name in dir(module):
            attr_value = getattr(module, attr_name)
            if isinstance(attr_value, list):  # Check if the attribute is a list
                merged_examples.extend(attr_value)

    return merged_examples


def create_few_shot_prompt_template(example_selector, example_prompt, prefix, suffix, input_variables,
                                    example_separator="\n\n"):
    """Utility method to create a FewShotPromptTemplate."""
    return FewShotPromptTemplate(
        example_selector=example_selector,
        example_prompt=PromptTemplate.from_template(example_prompt),
        prefix=prefix,
        suffix=suffix,
        input_variables=input_variables,
        example_separator=example_separator
    )


def create_example_selector(examples, embeddings, vector_store, k, input_keys):
    """Utility function to create a SemanticSimilarityExampleSelector."""
    return SemanticSimilarityExampleSelector.from_examples(
        examples,
        embeddings(),
        vector_store,
        k=k,
        input_keys=input_keys
    )
