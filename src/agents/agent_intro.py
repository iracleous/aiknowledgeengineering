# Deep Agents Introduction
# Demonstrates creating and invoking a basic deep agent with custom system prompt.
# Shows how to access agent responses and inspect resulting state keys.



from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain.agents import create_agent
import os
from langchain_openai import AzureChatOpenAI
 

load_dotenv()

# 2. Initialize the Agent
llm = AzureChatOpenAI(model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"))
agent = create_deep_agent(
    llm,
    system_prompt="You are a CodeHub support assistant. Answer directly from your own knowledge; you have no logs or files to check.",
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "Draft a short reply telling a customer we refunded their duplicate charge."}]
})

print(result["messages"][-1].content)
print("\nState keys beyond a plain create_agent():", [k for k in result if k != "messages"])
