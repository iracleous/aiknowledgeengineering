# Messages: direct calls to a chat LLM
# Show different ways to structure messages (objects vs dicts).

import os
from dotenv import load_dotenv
 
from langchain_core.messages import HumanMessage, SystemMessage

from langchain_openai import AzureChatOpenAI

load_dotenv()

llm = AzureChatOpenAI(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
)

 

# Objects
messages = [
    SystemMessage("You are a geography expert. Answer in one sentence."),
    HumanMessage("What is the capital of Greece?"),
]
response = llm.invoke(messages)
print("Response:", response.content)

# Dict format (role/content key-value) - usually common in APIs and JSON
messages = [
    {
        "role": "system",
        "content": "You are a geography expert. Answer in one sentence.",
    },
    {"role": "user", "content": "What is the capital of Greece?"},
]
response = llm.invoke(messages)
print("Response:", response.content)

# Tuple format (role, content)
messages = [
    ("system", "You are a geography expert. Answer in one sentence."),
    ("user", "What is the capital of Greece?"),
]
response = llm.invoke(messages)
print("Response:", response.content)


# Multi-turn with dicts
conversation = [
    {"role": "user", "content": "What is the capital of Greece?"},
    {"role": "assistant", "content": "Athens is the capital of Greece."},
    {"role": "user", "content": "And what's its population approximately?"},
]
multi_response = llm.invoke(conversation)
print("Response:", multi_response.content)

# System message with different tones (objects)
configs = [
    ("You are a pirate. Answer in pirate speak.", "What is water?"),
    ("You are a scientist. Be precise and technical.", "What is water?"),
    ("You are a poet. Answer poetically and metaphorically.", "What is water?"),
]

for system_prompt, question in configs:
    msgs = [
        SystemMessage(system_prompt),
        HumanMessage(question),
    ]
    print(f"Messages: {msgs}")
    result = llm.invoke(msgs)
    print(f"Response: {result.content[:100]}...")
