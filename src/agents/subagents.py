# Subagents for Task Delegation
# Demonstrates a main agent that delegates specialized tasks to specialized subagents.
# Each subagent has its own system prompt and expertise for handling specific domains.

import os

from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

load_dotenv()

llm = AzureChatOpenAI(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
)

billing_specialist = {
    "name": "billing-specialist",
    "description": "Handles billing questions: charges, refunds, invoices, subscriptions.",
    "system_prompt": "You are CodeHub's billing specialist. Be precise about refund timelines (3-5 business days).",
}

tech_specialist = {
    "name": "tech-specialist",
    "description": "Handles technical bug reports: crashes, errors, broken features.",
    "system_prompt": "You are CodeHub's technical support specialist. Ask for reproduction steps if missing.",
}

# Main agent that routes tasks to specialized subagents
agent = create_deep_agent(
    llm,
    system_prompt=(
        "You triage CodeHub support tickets. For anything billing- or tech-specific, "
        "delegate to the matching subagent via the `task` tool instead of answering yourself."
    ),
    subagents=[billing_specialist, tech_specialist],
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "I was charged twice for my subscription this month."}]
})
print("Agent Response:")
print(result["messages"][-1].content)
