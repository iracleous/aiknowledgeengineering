# 01_parameters.py
import os

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

load_dotenv()

llm = AzureChatOpenAI(
    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
)

prompt = "Suggest three creative names for an AI training academy."

experiments = [
    ("Low temperature", {"temperature": 0.1}),
    ("High temperature", {"temperature": 1.2}),
    ("Restricted top_p", {"top_p": 0.3}),
    ("Short output", {"temperature": 0.1, "max_tokens": 25}),
]

for label, settings in experiments:
    # Set defaults, then apply this experiment's overrides.
    parameters = {
        "temperature": 1.0,
        "top_p": 1.0,
        "max_tokens": 150,
        **settings,
    }

    response = llm.invoke(
        [("human", prompt)],
        **parameters,
    )

    print(f"\n--- {label} ---")
    print(response.content)
    print("Finish reason:", response.response_metadata.get("finish_reason"))