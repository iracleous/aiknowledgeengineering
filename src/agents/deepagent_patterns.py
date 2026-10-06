# Deep Agent Patterns: Researcher Pattern
# Demonstrates a lead agent that breaks down complex questions into simple facts
# and delegates each fact to a specialized researcher subagent.

import os

from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import AzureChatOpenAI

load_dotenv()

llm = AzureChatOpenAI(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
)

@tool
def search_docs(query: str) -> str:
    """Search documentation for a query."""
    docs = {
        "refund": "Refunds are issued in 3-5 business days to the original payment method.",
        "sla": "Standard support SLA is 24 hours; critical bugs get 1 hour.",
        "uptime": "CodeHub's platform SLA guarantees 99.9% monthly uptime.",
    }
    # Return matching document or default message
    hit = next((v for k, v in docs.items() if k in query.lower()), "No matching document found.")
    return hit


# Researcher subagent: looks up one fact at a time
researcher = {
    "name": "researcher",
    "description": "Looks up ONE specific fact in CodeHub's docs using search_docs.",
    "system_prompt": "Answer with just the fact you found, one sentence, no extra commentary.",
    "tools": [search_docs],
}

# Lead agent: breaks down questions and coordinates with researchers
lead_agent = create_deep_agent(
    llm,
    system_prompt=(
        "Break the user's question into individual facts that need looking up, "
        "delegate EACH one separately to the `researcher` subagent via the `task` tool, "
        "then combine all the answers into one short summary."
    ),
    subagents=[researcher],
)

result = lead_agent.invoke({
    "messages": [{"role": "user", "content": "Summarize our refund policy, our support SLA, and our uptime guarantee."}]
})
print(result["messages"][-1].content)
