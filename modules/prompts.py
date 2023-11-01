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