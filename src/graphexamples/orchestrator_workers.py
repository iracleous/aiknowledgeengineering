# Dynamic worker dispatch: orchestrator decides worker count at runtime using Send.
# LLM plans sections, then parallel workers write each section.

import operator
from typing import Annotated, TypedDict
import os

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send
from pydantic import BaseModel, Field

load_dotenv()

llm = AzureChatOpenAI(model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"))


class Plan(BaseModel):
    sections: list[str] = Field(
        description="2-4 short section titles for this help-center article"
    )


class State(TypedDict):
    topic: str
    sections: Annotated[list[str], operator.add]


class WorkerState(TypedDict):
    topic: str
    section: str


def orchestrator(state: State) -> list[Send]:
    """Plans the work, then dispatches one Send per planned section."""
    plan = llm.with_structured_output(Plan, method="function_calling").invoke(
        f"Plan the sections for a help-center article about: {state['topic']}"
    )
    return [
        Send("write_section", {"topic": state["topic"], "section": section})
        for section in plan.sections
    ]


def write_section(state: WorkerState) -> dict:
    """One worker, run once per planned section, in parallel with the others."""
    text = llm.invoke(
        f"Write one short paragraph for the '{state['section']}' section of an article about {state['topic']}"
    ).content
    return {"sections": [f"## {state['section']}\n{text}"]}


graph = StateGraph(State)
graph.add_node("write_section", write_section)
graph.add_conditional_edges(START, orchestrator, ["write_section"])
graph.add_edge("write_section", END)
app = graph.compile()

app.get_graph().draw_mermaid_png(output_file_path="graph-orchestrator.png")

result = app.invoke({"topic": "resetting your CodeHub password", "sections": []})
print(
    f"-- {len(result['sections'])} sections written by {len(result['sections'])} parallel workers --\n"
)
print("\n\n".join(result["sections"]))
