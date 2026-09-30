# Planning agent: plan → execute steps → replan based on findings.
# Dynamically adjusts plan as it learns more.

import operator
from typing import Annotated, Literal, TypedDict
import os


from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command
from pydantic import BaseModel, Field

load_dotenv()

llm = AzureChatOpenAI(model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"))


class Plan(BaseModel):
    steps: list[str] = Field(description="2-4 ordered, concrete steps needed to answer the question")


class Replan(BaseModel):
    done: bool = Field(description="True if enough is now known to answer the original question")
    remaining_steps: list[str] = Field(description="Updated remaining steps if not done; [] if done")


class State(TypedDict):
    question: str
    plan: list[str]
    past_steps: Annotated[list[str], operator.add]
    response: str | None


def planner(state: State) -> dict:
    """Break question into ordered steps."""
    plan = llm.with_structured_output(Plan, method="function_calling").invoke(
        f"Break this question into concrete steps: {state['question']!r}"
    )
    return {"plan": plan.steps}


def executor(state: State) -> dict:
    step = state["plan"][0]
    result = llm.invoke(f"Question: {state['question']!r}\nDo this one step and report the finding: {step}").content
    return {"plan": state["plan"][1:], "past_steps": [f"[{step}] -> {result}"]}


def replanner(state: State) -> Command[Literal["executor", "__end__"]]:
    if not state["plan"]:
        decision = Replan(done=True, remaining_steps=[])
    else:
        decision = llm.with_structured_output(Replan, method="function_calling").invoke(
            f"Question: {state['question']!r}\n"
            f"Findings so far: {state['past_steps']}\n"
            f"Remaining planned steps: {state['plan']}\n"
            "Is there enough to answer now? If not, return the updated remaining steps."
        )
    if decision.done:
        answer = llm.invoke(
            f"Question: {state['question']!r}\nFindings: {state['past_steps']}\nGive the final answer in 1-2 sentences."
        ).content
        return Command(goto=END, update={"response": answer})
    return Command(goto="executor", update={"plan": decision.remaining_steps})


graph = StateGraph(State)
graph.add_node("planner", planner)
graph.add_node("executor", executor)
graph.add_node("replanner", replanner)
graph.add_edge(START, "planner")
graph.add_edge("planner", "executor")
graph.add_edge("executor", "replanner")
app = graph.compile()

app.get_graph().draw_mermaid_png(output_file_path="graph-planner.png")


result = app.invoke({
    "question": "Should CodeHub raise its support team's SLA from 24h to 12h for medium-priority tickets?",
    "plan": [], "past_steps": [], "response": None,
})
print(f"-- {len(result['past_steps'])} step(s) executed --")
for step in result["past_steps"]:
    print(" ", step)
print("\nFinal answer:", result["response"])
