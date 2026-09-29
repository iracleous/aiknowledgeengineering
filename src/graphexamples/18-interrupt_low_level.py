# Pauseable workflow: interrupt() freezes execution for human approval.
# Resume with Command(resume=...) to continue from the same point.

from typing import Annotated, TypedDict

from dotenv import load_dotenv
 
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.types import Command, interrupt

import os
from langchain_openai import AzureChatOpenAI

load_dotenv()

llm = AzureChatOpenAI(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
)


class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    amount_usd: float


def request_refund(state: State) -> dict:
    """Pause workflow and wait for human approval of refund."""
    decision = interrupt(
        {
            "question": f"Approve a ${state['amount_usd']:.2f} refund?",
            "amount_usd": state["amount_usd"],
        }
    )
    if decision == "approve":
        return {"messages": [AIMessage(f"Refunded ${state['amount_usd']:.2f}.")]}
    return {"messages": [AIMessage("Refund request rejected.")]}


builder = StateGraph(State)
builder.add_node("request_refund", request_refund)
builder.add_edge(START, "request_refund")
builder.add_edge("request_refund", END)
graph = builder.compile(checkpointer=MemorySaver())

graph.get_graph().draw_mermaid_png(output_file_path="graph2.png")


config = {"configurable": {"thread_id": "refund-low-level-1"}}

# First call: the graph freezes at interrupt() and returns control here.
paused = graph.invoke(
    {"messages": [HumanMessage("Refund order O-1")], "amount_usd": 45.0}, config
)
print("[paused]", paused["__interrupt__"][0].value)

# A human looks at the payload above and decides. Command(resume=...)
# continues the SAME run from the exact interrupt() call.

userInput=input("do you approve")
if userInput=="y" : 
    userInput = "approve"
else:
    unserInput="decline"
final = graph.invoke(Command(resume=userInput), config)
print("[resumed]", final["messages"][-1].content)
