# Execution Environment with Filesystem Loading
# Loads policy documents from the real filesystem into an agent's virtual filesystem.
# Agent can access and read these documents but cannot modify them.

import os

from deepagents import FilesystemPermission, create_deep_agent
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import AzureChatOpenAI
 

load_dotenv()

# 2. Initialize the Agent
llm = AzureChatOpenAI(model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")) 

agent = create_deep_agent(
    llm,
    system_prompt=(
        "You are a CodeHub support assistant. Relevant documents are "
        "in your virtual filesystem -- read them before answering, don't guess."
    ),
    permissions=[
        FilesystemPermission(operations=["write"], paths=["/**"], mode="deny")
    ],
)


def load_file_to_virtual_fs(real_path):
    """Read file from real filesystem and format for virtual filesystem."""
    with open(real_path, "r", encoding="utf-8") as f:
        content = f.read()
    return {
        "content": content,
        "encoding": "utf-8",
    }


# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
policies_file = os.path.join(script_dir, "company_policies.md")

# Create initial state with files loaded from real filesystem
initial_state = {
    "messages": [
        {
            "role": "user",
            "content": "What's our warranty policy and how long does standard shipping take?",
        }
    ],
    "files": {
        "/policies/company_policies.md": load_file_to_virtual_fs(policies_file),
    },
}

result = agent.invoke(initial_state)
print("Agent Response:")
print(result["messages"][-1].content)
print("\nFiles in virtual filesystem:", list(result["files"].keys()))
