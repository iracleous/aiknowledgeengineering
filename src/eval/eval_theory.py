# Demonstrates evaluation challenges: exact match and keyword matching fail
# on open-ended LLM responses because phrased differently but correct answers
# are still considered failures. This shows why semantic evaluation is needed.

import os

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

load_dotenv()

llm = AzureChatOpenAI(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
)

REFERENCE_ANSWER = "Refunds are processed within 3-5 business days to the original payment method."

candidate = llm.invoke("In one sentence, what's CodeHub's refund timeline?").content

exact_match = candidate.strip() == REFERENCE_ANSWER
print("Exact match:", exact_match)
print("Candidate:  ", candidate)
print("Reference:  ", REFERENCE_ANSWER)

keywords = ["3-5", "business days", "original payment"]
keyword_hits = sum(1 for k in keywords if k in candidate)
print(f"\nKeyword overlap: {keyword_hits}/{len(keywords)} -- still just string matching, not judging meaning")

print(
    "\nNeither check can tell 'refunds take three to five business days back to your card' "
    "apart from a wrong answer that happens to share a keyword. Unit 49 replaces this with "
    "a second LLM call that judges MEANING against a rubric, not string identity."
)
