# 05_react.py
import json
import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import AzureChatOpenAI

load_dotenv()

llm = AzureChatOpenAI(
    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    api_version=os.environ["OPENAI_API_VERSION"],
    temperature=0,
    max_tokens=300,
)


@tool
def get_stock(product: str) -> dict:
    """Look up stock for a singular product name: laptop, monitor, or keyboard."""
    inventory = {
        "laptop": 12,
        "monitor": 0,
        "keyboard": 35,
    }

    return {
        "product": product,
        "quantity": inventory.get(product.lower()),
    }


# Make the tool available to the model.
llm_with_tools = llm.bind_tools([get_stock])

tools_by_name = {
    get_stock.name: get_stock,
}

messages = [
    SystemMessage(
        content="""
        You are an inventory assistant.
        Use get_stock for inventory questions.
        Use singular product names when calling the tool.
        Never invent stock quantities.
        If the tool returns null, say the product is unknown.
        Give a concise answer based on the tool results.
        """
    ),
    HumanMessage(content="Can I buy 5 laptops and 2 monitors?"),
]

# Limit the number of model calls.
for step in range(5):
    response = llm_with_tools.invoke(messages)

    # Preserve the AI response, including any tool calls.
    messages.append(response)

    if not response.tool_calls:
        print("\nFinal answer:")
        print(response.content)
        break

    for call in response.tool_calls:
        tool_name = call["name"]
        arguments = call["args"]

        selected_tool = tools_by_name.get(tool_name)

        if selected_tool is None:
            result = {"error": f"Unknown tool: {tool_name}"}
        else:
            result = selected_tool.invoke(arguments)

        print("Action:", tool_name, arguments)
        print("Observation:", result)

        # Return the result for this specific tool call.
        messages.append(
            ToolMessage(
                content=json.dumps(result),
                tool_call_id=call["id"],
            )
        )
else:
    print("Stopped: maximum number of model calls reached.")
