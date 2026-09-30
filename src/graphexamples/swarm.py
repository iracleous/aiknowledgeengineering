# Swarm pattern: peer-to-peer agent handoffs without a supervisor.
# Agents can hand off to each other directly based on problem needs.

from typing import Annotated, Literal, TypedDict

 
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.types import Command
from pydantic import BaseModel, Field

import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
 

load_dotenv()

llm = AzureChatOpenAI(model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"))
 

class HandoffCheck(BaseModel):
    needs_other_specialist: bool = Field(
        description="True only if the OTHER specialist is also needed"
    )


class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def billing_agent(state: State) -> Command[Literal["tech_agent", "__end__"]]:
    """Handle billing issues and decide if handoff to tech agent needed."""
    ticket = state["messages"][0].content
    check = llm.with_structured_output(HandoffCheck, method="function_calling").invoke(
        f"Billing agent reviewing: {ticket!r}. Does this ALSO need the tech specialist?"
    )
    reply = llm.invoke(
        f"As the billing specialist, address the billing part of: {ticket!r}"
    ).content
    msg = AIMessage(f"[billing_agent] {reply}")
    if check.needs_other_specialist:
        return Command(goto="tech_agent", update={"messages": [msg]})
    return Command(goto="__end__", update={"messages": [msg]})


def tech_agent(state: State) -> Command[Literal["billing_agent", "__end__"]]:
    """Handle technical issues and decide if handoff to billing agent needed."""
    ticket = state["messages"][0].content
    check = llm.with_structured_output(HandoffCheck, method="function_calling").invoke(
        f"Tech agent reviewing: {ticket!r}. Does this ALSO need the billing specialist?"
    )
    reply = llm.invoke(
        f"As the technical support specialist, address the bug in: {ticket!r}"
    ).content
    msg = AIMessage(f"[tech_agent] {reply}")
    if check.needs_other_specialist:
        return Command(goto="billing_agent", update={"messages": [msg]})
    return Command(goto="__end__", update={"messages": [msg]})


# Every specialist is a valid ENTRY point in a swarm -- there's no single
# supervisor node deciding the first hop; whichever node the caller starts
# at is the entry.
graph = StateGraph(State)
graph.add_node("billing_agent", billing_agent)
graph.add_node("tech_agent", tech_agent)
graph.add_edge(START, "billing_agent")  # this run happens to start at billing
app = graph.compile()


app.get_graph().draw_mermaid_png(output_file_path="swarm.png")

ticket = "I was charged twice, AND the export button crashes the app."
result = app.invoke({"messages": [HumanMessage(ticket)]})
for msg in result["messages"]:
    print(f"[{msg.type}]", msg.content)
