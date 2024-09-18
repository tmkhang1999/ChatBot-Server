def simple_workflow():
    messages = ["Hello, how are you?"]

    def process_message(msg):
        return msg.upper()

    workflow = {}

    # Adding a node using a lambda function
    workflow["uppercase_node"] = lambda state: {
        "ok": [process_message(state["messages"][0])]
    }
    print(workflow)

    # Simulating the workflow execution
    initial_state = {"messages": messages}
    print(initial_state)
    result = workflow["uppercase_node"](initial_state)

    print(result)


simple_workflow()