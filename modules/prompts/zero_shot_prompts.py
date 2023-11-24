from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)

GENERAL_PROMPT_TEMPLATE = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(
            "You are a nice chatbot having a conversation with a human."
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template("{input}"),
    ]
)

NAME_PROMPT_TEMPLATE = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(
            "You are a nice chatbot having a conversation with a human."
        ),
        HumanMessagePromptTemplate.from_template("Given the initial input provided in the first message of the conversation: "
                                                 "\n{input} \nGenerate a creative and fitting name for this conversation. "
                                                 "Consider the tone, context, or any notable keywords in the input to "
                                                 "craft a unique and engaging title.\nName for the Conversation: "),
    ]
)

EVENT_SCHEDULE_PROMPT_TEMPLATE = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(
            "Imagine you're an event planner. Here are the event details:"
        ),
        HumanMessagePromptTemplate.from_template("{input} \nCreate a detailed plan for this event, breaking it down "
                                                 "into two lists: 'before the event day' and 'on the event day.' "
                                                 "Each list should consist of sub-lists where the first sub-list "
                                                 "represents the header with columns 'Stages,' 'Duration,' and 'Budget,' "
                                                 "and the subsequent sub-lists represent the rows with corresponding details."),
    ]
)

RETRIEVAL_PROMPT_TEMPLATE = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(
            "You are an assistant for question-answering tasks."
        ),
        HumanMessagePromptTemplate.from_template("Use the following pieces of retrieved context to answer the "
                                                 "question. If you don't know the answer, just say that you don't "
                                                 "know. Use three sentences maximum and keep the answer concise. "
                                                 "\nQuestion: {question} \nContext: {context} \nAnswer:"),
    ]
)
