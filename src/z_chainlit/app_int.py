"""
chainlit run src\z_chainlit\app_int.py -w --port 8001


"""


import os

import chainlit as cl
from dotenv import load_dotenv
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_openai import AzureChatOpenAI

load_dotenv()

model = AzureChatOpenAI(
    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
    temperature=0.2,
)


@cl.on_chat_start
async def start():
    # Each chat session gets its own history.
    cl.user_session.set(
        "history",
        [
            SystemMessage(
                content=(
                    "You are a helpful assistant. "
                    "Use the conversation history to answer follow-up questions."
                )
            )
        ],
    )

    await cl.Message(
        content="Hello! I can remember our conversation within this chat."
    ).send()


@cl.on_message
async def respond(message: cl.Message):
    history = cl.user_session.get("history")

    # Build the request without changing stored history yet.
    request_messages = [
        *history,
        HumanMessage(content=message.content),
    ]

    try:
        response = await model.ainvoke(request_messages)
    except Exception:
        await cl.Message(
            content="The model request failed. Please try again."
        ).send()
        return

    # Save both sides of the successful conversation turn.
    cl.user_session.set(
        "history",
        [
            *request_messages,
            AIMessage(content=response.content),
        ],
    )

    await cl.Message(content=response.content).send()