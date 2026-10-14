"""
to execute this file, run the following command in the terminal:

uv run uvicorn src.z_chainlit.backe_end:app --reload --port 8000

"""


import asyncio
import os
from uuid import UUID

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_openai import AzureChatOpenAI
from pydantic import BaseModel, Field

load_dotenv()

app = FastAPI(title="Chat Backend")

model = AzureChatOpenAI(
    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
    temperature=0.2,
)

# In-memory storage for this demonstration.
conversations: dict[str, list] = {}
session_locks: dict[str, asyncio.Lock] = {}


class ChatRequest(BaseModel):
    session_id: UUID
    message: str = Field(min_length=1, max_length=10000)


class ChatResponse(BaseModel):
    answer: str


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    session_id = str(request.session_id)

    # Serialize requests within the same conversation.
    lock = session_locks.setdefault(session_id, asyncio.Lock())

    async with lock:
        history = conversations.get(
            session_id,
            [
                SystemMessage(
                    content=(
                        "You are a helpful assistant. "
                        "Use conversation history to answer follow-up questions."
                    )
                )
            ],
        )

        messages = [
            *history,
            HumanMessage(content=request.message),
        ]

        try:
            response = await model.ainvoke(messages)
        except Exception as exc:
            raise HTTPException(
                status_code=502,
                detail="The model request failed.",
            ) from exc

        # This example expects a text response.
        answer = response.content
        if not isinstance(answer, str):
            raise HTTPException(
                status_code=502,
                detail="The model returned an unexpected response format.",
            )

        # Save only successfully completed turns.
        conversations[session_id] = [
            *messages,
            AIMessage(content=answer),
        ]

        return ChatResponse(answer=answer)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)