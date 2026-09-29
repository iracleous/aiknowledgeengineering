# Cross-thread memory with Store API: user preferences persist across threads.
# Unlike checkpoints (per-thread), store is per-user.

from typing import Annotated, TypedDict

from dotenv import load_dotenv
 
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.store.memory import InMemoryStore

import os
from langchain_openai import AzureChatOpenAI

load_dotenv()

llm = AzureChatOpenAI(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
)



class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def remember_preference(state: State, *, config, store) -> dict:
    """Store user language preference in cross-thread memory."""
    user_id = config["configurable"]["user_id"]
    store.put(("preferences", user_id), "language", {"value": "Greek"})
    return {"messages": [AIMessage("Got it, I'll reply in Greek from now on.")]}


def use_preference(state: State, *, config, store) -> dict:
    """Retrieve user language preference from cross-thread memory."""
    user_id = config["configurable"]["user_id"]
    item = store.get(("preferences", user_id), "language")
    language = item.value["value"] if item else "unknown"
    return {"messages": [AIMessage(f"Your saved preferred language is: {language}")]}


store = InMemoryStore()

remember_graph = StateGraph(State)
remember_graph.add_node("remember", remember_preference)
remember_graph.add_edge(START, "remember")
remember_graph.add_edge("remember", END)
remember_app = remember_graph.compile(store=store)

use_graph = StateGraph(State)
use_graph.add_node("use", use_preference)
use_graph.add_edge(START, "use")
use_graph.add_edge("use", END)
use_app = use_graph.compile(store=store)

# Thread A: the user states a preference.
remember_app.invoke(
    {"messages": [HumanMessage("Please always reply in Greek.")]},
    {"configurable": {"thread_id": "thread-A", "user_id": "user-42"}},
)

# Thread B: a COMPLETELY different thread_id, same user_id -- the checkpointer
# (per-thread) would know nothing here, but the store (per-user) still does.
result = use_app.invoke(
    {"messages": [HumanMessage("What language did I ask for?")]},
    {"configurable": {"thread_id": "thread-B", "user_id": "user-42"}},
)
print("[cross-thread memory]", result["messages"][-1].content)
