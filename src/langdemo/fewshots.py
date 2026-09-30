# 04_few_shot.py
import os

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

load_dotenv()

llm = AzureChatOpenAI(
    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    api_version=os.environ["OPENAI_API_VERSION"],
    temperature=0,
    max_tokens=10,
)

response = llm.invoke(
    [
        (
            "system",
            """
            Classify IT incidents.
            Reply with exactly one label:
            LOW, MEDIUM, or HIGH.
            Follow the classification examples.
            """,
        ),
        (
            "human",
            "One employee cannot change their profile picture.",
        ),
        ("ai", "LOW"),
        (
            "human",
            "One department cannot access its shared printer.",
        ),
        ("ai", "MEDIUM"),
        (
            "human",
            "All customers cannot complete payments.",
        ),
        ("ai", "HIGH"),
        (
            "human",
            "The company website is unavailable to all customers.",
        ),
    ]
)

print(response.content)