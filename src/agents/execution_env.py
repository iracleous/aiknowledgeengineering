# Execution Environment with Virtual Filesystem
# Creates an agent with a virtual filesystem containing policy documents.
# Agent can read files but is restricted from writing (read-only execution environment).

from deepagents import FilesystemPermission, create_deep_agent
from dotenv import load_dotenv
from langchain.agents import create_agent
import os
from langchain_openai import AzureChatOpenAI
 

load_dotenv()

# 2. Initialize the Agent
llm = AzureChatOpenAI(model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")) 

agent = create_deep_agent(
    llm,
    system_prompt=(
        "You are a CodeHub support assistant. A relevant document is already "
        "in your virtual filesystem -- read it before answering, don't guess."
    ),
    permissions=[
        # Deny write operations on entire filesystem
        FilesystemPermission(operations=["write"], paths=["/**"], mode="deny")
    ],
)
initial_state = {
    "messages": [
        {"role": "user", "content": "What's our refund policy for duplicate charges?"}
    ],
    "files": {
        "/policies/company_policies.md": {
            "content": "# Refund Policy\n\nDuplicate charges are refunded within 3-5 business days to the original payment method.",
            "encoding": "utf-8",
        },
    },
}

result = agent.invoke(initial_state)
print(result["messages"][-1].content)
print("\nFiles after the run:", list(result["files"].keys()))

# Display all files in the virtual filesystem
print("\n" + "=" * 50)
print("All files in virtual filesystem:")
print("=" * 50)
for path, file_info in result["files"].items():
    print(f"\n📄 {path}")
    print(f"Content:\n{file_info['content']}")
