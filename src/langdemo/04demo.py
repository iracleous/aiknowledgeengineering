# 04_validate_output.py
import os
from typing import Literal

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI
from pydantic import BaseModel, Field, ValidationError

load_dotenv()


class IncidentAssessment(BaseModel):
    severity: Literal["LOW", "MEDIUM", "HIGH"]
    reason: str = Field(min_length=1)
    recommendation: str = Field(min_length=1)


llm = AzureChatOpenAI(
    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
    api_version=os.environ["OPENAI_API_VERSION"],
)

structured_llm = llm.with_structured_output(
    IncidentAssessment,
    method="function_calling",
)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Assess IT incidents and recommend a practical next action.",
        ),
        ("human", "{incident}"),
    ]
)

chain = prompt | structured_llm

try:
    assessment = chain.invoke(
        {"incident": "The company website is unavailable to all customers."}
    )

    print("Severity:", assessment.severity)
    print("Reason:", assessment.reason)
    print("Recommendation:", assessment.recommendation)

    print("\nJSON:")
    print(assessment.model_dump_json(indent=2))

except ValidationError as error:
    print("Output failed schema validation:", error)