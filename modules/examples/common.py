import os
import glob
import importlib.util


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
