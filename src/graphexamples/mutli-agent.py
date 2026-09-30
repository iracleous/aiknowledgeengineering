# Multi-agent supervisor: one supervisor routes tickets to specialist agents.
# Each specialist handles their domain, then optionally hands off to another.

from typing import Annotated, Literal, TypedDict

from dotenv import load_dotenv
 
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.types import Command
from pydantic import BaseModel, Field
 
from langchain_openai import AzureChatOpenAI 
import os
 

load_dotenv()

llm = AzureChatOpenAI(model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"))




class Route(BaseModel):
    agent: Literal["billing_agent", "tech_agent"] = Field(
        description="which specialist should handle this first"
    )


class HandoffCheck(BaseModel):
    needs_other_specialist: bool = Field(
        description="True only if the ticket ALSO needs the other specialist"
    )


class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def supervisor(state: State) -> Command[Literal["billing_agent", "tech_agent"]]:
    """Route ticket to appropriate specialist agent."""
    route = llm.with_structured_output(Route, method="function_calling").invoke(
        f"Which specialist should first handle this ticket? {state['messages'][-1].content!r}"
    )
    return Command(goto=route.agent)


def billing_agent(state: State) -> Command[Literal["tech_agent", "__end__"]]:
    """Handle billing issues and decide if handoff to tech agent needed."""
    ticket = state["messages"][0].content
    check = llm.with_structured_output(HandoffCheck, method="function_calling").invoke(
        f"Billing agent reviewing: {ticket!r}. Does this ALSO describe a technical bug (not just a billing issue)?"
    )
    reply = llm.invoke(
        f"As the billing specialist, address the billing part of: {ticket!r}"
    ).content
    msg = AIMessage(content=f"[billing_agent] {reply}")
    if check.needs_other_specialist:
        return Command(goto="tech_agent", update={"messages": [msg]})
    return Command(goto=END, update={"messages": [msg]})


def tech_agent(state: State) -> Command[Literal["__end__"]]:
    """Handle technical issues and conclude."""
    ticket = state["messages"][0].content
    reply = llm.invoke(
        f"As the technical support specialist, address the bug in: {ticket!r}"
    ).content
    return Command(
        goto=END, update={"messages": [AIMessage(content=f"[tech_agent] {reply}")]}
    )


graph = StateGraph(State)
graph.add_node("supervisor", supervisor)
graph.add_node("billing_agent", billing_agent)
graph.add_node("tech_agent", tech_agent)
graph.add_edge(START, "supervisor")
app = graph.compile()

app.get_graph().draw_mermaid_png(output_file_path="multi-agent.png")

ticket = "I was charged twice this month, AND the app crashes every time I open the billing settings page"
result = app.invoke({"messages": [HumanMessage(ticket)]})
for msg in result["messages"]:
    print(f"[{msg.type}]", msg.content)
