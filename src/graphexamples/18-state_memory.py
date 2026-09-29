# Persistent state with MemorySaver: conversation history survives across invocations.
# Thread IDs separate independent conversations.

from typing import Annotated, TypedDict

from dotenv import load_dotenv
 
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

import os
from langchain_openai import AzureChatOpenAI

load_dotenv()

llm = AzureChatOpenAI(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
)



class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def chat(state: State) -> dict:
    """Invoke LLM with conversation history."""
    return {"messages": [llm.invoke(state["messages"])]}


graph = StateGraph(State)
graph.add_node("chat", chat)
graph.add_edge(START, "chat")
graph.add_edge("chat", END)
app = graph.compile(checkpointer=MemorySaver())

app.get_graph().draw_mermaid_png(output_file_path="graph.png")


# Same thread_id across calls -- the checkpointer loads prior state first,
# so `messages` accumulates instead of starting fresh each time.
config = {"configurable": {"thread_id": "ticket-T-101"}}

r1 = app.invoke(
    {"messages": [HumanMessage("My name is Nikos. Remember that.")]}, config
)
print("[turn 1]", r1["messages"][-1].content)

r2 = app.invoke({"messages": [HumanMessage("What's my name?")]}, config)
print("[turn 2]", r2["messages"][-1].content)

# A different thread_id starts a completely separate, empty conversation.
other = app.invoke(
    {"messages": [HumanMessage("What's my name?")]},
    {"configurable": {"thread_id": "other-thread"}},
)
print("[other thread]", other["messages"][-1].content)
