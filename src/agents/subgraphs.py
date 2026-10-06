# Subgraphs: composable workflows with independent states.
# Parent and subgraph have different state schemas, bridged by a wrapper node.

import os
from typing import TypedDict

from dotenv import load_dotenv
 
from langgraph.graph import END, START, StateGraph
from langchain_openai import AzureChatOpenAI

load_dotenv()

llm = AzureChatOpenAI(model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")) 


class TriageState(TypedDict):
    ticket: str
    category: str | None
    reply: str | None


def classify(state: TriageState) -> dict:
    """Classify a ticket."""
    return {"category": llm.invoke(f"One word category (billing/bug/general): {state['ticket']!r}").content.strip()}


def draft_reply(state: TriageState) -> dict:
    prompt = f"Write a short reply to this {state['category']} ticket: {state['ticket']!r}"
    return {"reply": llm.invoke(prompt).content}


triage_graph = StateGraph(TriageState)
triage_graph.add_node("classify", classify)
triage_graph.add_node("draft_reply", draft_reply)
triage_graph.add_edge(START, "classify")
triage_graph.add_edge("classify", "draft_reply")
triage_graph.add_edge("draft_reply", END)
triage_subgraph = triage_graph.compile()

triage_subgraph = triage_graph.compile()

triage_subgraph.get_graph().draw_mermaid_png(output_file_path="graph-triage.png")    

# ── Parent graph: a different state schema -- a wrapper node bridges them ─
class EscalationState(TypedDict):
    ticket: str
    category: str | None
    reply: str | None
    escalated: bool


def run_triage(state: EscalationState) -> dict:
    """Wrapper node: parent and subgraph states differ, so this node
    translates between them -- calling the subgraph as a single unit."""
    triage_result = triage_subgraph.invoke({"ticket": state["ticket"], "category": None, "reply": None})
    return {"category": triage_result["category"], "reply": triage_result["reply"]}


def check_escalation(state: EscalationState) -> dict:
    return {"escalated": state["category"].lower() == "bug"}


parent_graph = StateGraph(EscalationState)
parent_graph.add_node("triage", run_triage)
parent_graph.add_node("check_escalation", check_escalation)
parent_graph.add_edge(START, "triage")
parent_graph.add_edge("triage", "check_escalation")
parent_graph.add_edge("check_escalation", END)
app = parent_graph.compile()

app.get_graph().draw_mermaid_png(output_file_path="graph-parent.png")

result = app.invoke({"ticket": "The app crashes every time I log in", "category": None, "reply": None, "escalated": False})
print(f"category={result['category']}  escalated={result['escalated']}")
print(result["reply"])
