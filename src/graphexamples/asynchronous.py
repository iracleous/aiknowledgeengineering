# ex 29
# Async LanggGraph: ainvoke() instead of invoke() for parallel ticket processing.
# Demonstrates speedup from concurrent execution.

import asyncio
import time
import os
from typing import TypedDict

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI 
from langgraph.graph import END, START, StateGraph

load_dotenv()

llm = AzureChatOpenAI(model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"))


class State(TypedDict):
    ticket: str
    reply: str | None


async def reply(state: State) -> dict:
    """Async node that calls ainvoke() instead of invoke()."""
    response = await llm.ainvoke(f"Write a one-sentence reply to: {state['ticket']!r}")
    return {"reply": response.content}


graph = StateGraph(State)
graph.add_node("reply", reply)
graph.add_edge(START, "reply")
graph.add_edge("reply", END)
app = graph.compile()

app.get_graph().draw_mermaid_png(output_file_path="async-orchestrator.png")

TICKETS = ["Payment failed", "App crashes on login", "How do I export my data?"]


async def main():
    start = time.perf_counter()
    sequential = [await app.ainvoke({"ticket": t, "reply": None}) for t in TICKETS]
    sequential_time = time.perf_counter() - start
    print(
        f"sequential (await one at a time): {sequential_time:.2f}s for {len(TICKETS)} tickets"
    )




    start = time.perf_counter()
    concurrent = await asyncio.gather(
        *(app.ainvoke({"ticket": t, "reply": None}) for t in TICKETS)
    )
    concurrent_time = time.perf_counter() - start
    print(
        f"concurrent (asyncio.gather):      {concurrent_time:.2f}s for {len(TICKETS)} tickets"
    )

    assert [r["reply"] for r in sequential] and [r["reply"] for r in concurrent]
    print(f"\nspeedup: {sequential_time / concurrent_time:.1f}x")


asyncio.run(main())

