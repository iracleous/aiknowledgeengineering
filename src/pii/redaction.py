# Two guardrailing approaches with opposite tradeoffs: deterministic (regex, fast/free but brittle)
# vs model-based (LLM judgment, catches paraphrases but costs a call). Shows both techniques.

import os
import re

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from pydantic import BaseModel, Field

load_dotenv()

llm = AzureChatOpenAI(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
)


CREDIT_CARD_PATTERN = re.compile(r"\b(?:\d[ -]?){13,16}\b")
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")



def deterministic_guardrail(text: str) -> bool:
    # Fast, free regex check - matches the exact card number pattern but misses spelled-out numbers
    return CREDIT_CARD_PATTERN.search(text) is not None


class PolicyCheck(BaseModel):
    violates: bool = Field(description="True if the message contains a customer's payment card number, in any form")


def model_guardrail(text: str) -> bool:
    # LLM judgment - catches paraphrases and intent but costs a call and can be wrong
    return llm.with_structured_output(PolicyCheck, method="function_calling").invoke(
        f"Does this message contain a customer's credit/debit card number, written out in any form? {text!r}"
    ).violates


test_messages = [
    "My card number is 4111 1111 1111 1111",
    "It's four one one one, one one one one, twice more like that",
]

for msg in test_messages:
    det = deterministic_guardrail(msg)
    mod = model_guardrail(msg)
    print(f"{msg!r}\n  deterministic={det}  model-based={mod}")
