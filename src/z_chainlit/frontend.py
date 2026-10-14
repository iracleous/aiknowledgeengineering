"""
Chainlit frontend for the chat application.

chainlit run src\z_chainlit\frontend.py -w --port 8001

"""


from uuid import uuid4

import chainlit as cl
import httpx

BACKEND_URL = "http://127.0.0.1:8000"


@cl.on_chat_start
async def start():
    cl.user_session.set("session_id", str(uuid4()))

    await cl.Message(
        content="Hello! I can remember our conversation within this chat."
    ).send()


@cl.on_message
async def respond(message: cl.Message):
    session_id = cl.user_session.get("session_id")

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{BACKEND_URL}/chat",
                json={
                    "session_id": session_id,
                    "message": message.content,
                },
            )

            response.raise_for_status()
            answer = response.json()["answer"]

    except httpx.HTTPError:
        await cl.Message(
            content="Unable to get a response from the backend. Please try again."
        ).send()
        return

    await cl.Message(content=answer).send()