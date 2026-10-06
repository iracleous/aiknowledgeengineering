# Capstone: tools (Unit 08) + a skill (Unit 44) + subagents (Unit 45)
# together in one deep agent. Unit 43's pgvector memory is the natural next
# layer on top of this (swap `backend=FilesystemBackend(...)` for the
# CompositeBackend + PostgresStore combo from that unit) -- omitted here to
# keep this runnable with zero extra infrastructure.
# Run: uv run python 47_deepagent_project.py

import os
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import AzureChatOpenAI

load_dotenv()

llm = AzureChatOpenAI(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
)


@tool
def get_account_status(customer_email: str) -> str:
    """Look up a CodeHub customer's account status and plan."""
    return "active, Pro plan, member since 2024"


billing_specialist = {
    "name": "billing-specialist",
    "description": "Handles billing questions: charges, refunds, invoices, subscriptions.",
    "system_prompt": "You are CodeHub's billing specialist. Refund timeline is 3-5 business days.",
    "tools": [get_account_status],
}

tech_specialist = {
    "name": "tech-specialist",
    "description": "Handles technical bug reports: crashes, errors, broken features.",
    "system_prompt": "You are CodeHub's technical support specialist. Ask for reproduction steps if missing.",
}

agent = create_deep_agent(
    llm,
    backend=FilesystemBackend(root_dir=Path.cwd()),
    skills=["/skills/ticket-triage/"],
    subagents=[billing_specialist, tech_specialist],
    system_prompt="You triage CodeHub support tickets using the ticket-triage skill, then delegate.",
)

result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Customer jane@example.com says she was charged twice this month for her subscription.",
    }]
})
print(result["messages"][-1].content)
