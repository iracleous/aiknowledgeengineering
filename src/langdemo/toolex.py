# Tool calling with @tool decorator
# Define tools, give them to the model with bind_tools, then manually handle tool calls.

from dotenv import load_dotenv
 
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool

import os
from langchain_openai import AzureChatOpenAI

load_dotenv()

llm = AzureChatOpenAI(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
)



@tool
def get_ticket_count(status: str) -> int:
    """Return how many CodeHub support tickets have the given status."""
    return {"open": 42, "closed": 918}.get(status, 0)

@tool
def get_weather(location: str) -> dict:
    """Returnthe weather condition in the given location."""
    return {"location": location, "forecast": "all good"}



# Step 1: Give the LLM a menu of tools
tools_by_name = {"get_ticket_count": get_ticket_count,
                 "get_weather":get_weather}

llm_with_tools = llm.bind_tools([get_ticket_count, get_weather])

# Step 2: Ask the model a question; it may request tool calls
messages = [HumanMessage("How many open tickets does CodeHub have?")]
messages = [HumanMessage("What is the wether forecast in the location where CodeHub headquarters are?")]


response = llm_with_tools.invoke(messages)
print(response)
print(response.tool_calls)

# Step 3: If the model called a tool, execute it
if response.tool_calls:
    tool_name = response.tool_calls[0]["name"]
    tool_args = response.tool_calls[0]["args"]
    tool_result = tools_by_name[tool_name].invoke(tool_args)
    print("[Tool result]", tool_result)

    # # Step 4: Feed the result back to the model
    messages.append(response)
    messages.append(
        ToolMessage(content=str(tool_result), tool_call_id=response.tool_calls[0]["id"])
    )

    # Let the model formulate the final answer
    final_response = llm_with_tools.invoke(messages)
    print("[Final answer]", final_response.content)
