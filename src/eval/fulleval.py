# Uses LLM-as-judge with structured output to evaluate answers semantically.
# Shows position bias: when comparing answers, their order can flip the verdict.
# Solution: test both orderings to avoid bias.

import os

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from pydantic import BaseModel, Field

load_dotenv()

llm = AzureChatOpenAI(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
)


class Judgment(BaseModel):
    completness: int = Field(description="Score from 0-100 for how complete the answer is")
    faithfulness: int = Field(description="Score from 0-100 for how faithful the answer is to the rubric")  
    correctness: int = Field(description="Score from 0-100 for how correct the answer is")
    conciseness: int = Field(description="Score from 0-100 for how concise the answer is")
    clarity: int = Field(description="Score from 0-100 for how clear the answer is")
    groundedness: int = Field(description="Score from 0-100 for how well the answer is grounded in the rubric")
    passed: bool = Field(description="True if the answer correctly states the refund timeline is 3-5 business days")
    reasoning: str = Field(description="One sentence explaining the verdict")


def judge(candidate_answer: str, rubric: str) -> Judgment:
    prompt = (f"""
        Judge this candidate answer against the rubric below. 
        Evaluate these five criteria:
    - correctness: factual and technical accuracy against the reference.
     - relevance: directly addresses the question.
    - completeness: covers the points needed to answer the question.
    - clarity: understandable, precise, and well structured.
    - groundedness: claims are supported by the supplied reference.
    - faithfulness: the answer is faithful to the reference and does not hallucinate.    
    -   passed if score is 60 or above for all criteria, otherwise failed. 
        .\n\n
        Rubric: {rubric}\n
        Candidate answer: {candidate_answer!r}
        """
    )
    return llm.with_structured_output(Judgment, method="function_calling").invoke(prompt)

question="What is the difference between a Python list and a tuple?",
rubric="A list is mutable, while a tuple is immutable.",

 

candidate = llm.invoke(question).content
verdict = judge(candidate, rubric)
print(f"[judge] passed={verdict.passed} \n"
      f"reasoning={verdict.reasoning} \n"
      f"completeness={verdict.completness} \n"
      f"faithfulness={verdict.faithfulness} \n"
      f"correctness={verdict.correctness} \n"
      f"conciseness={verdict.conciseness} \n"
      f"clarity={verdict.clarity} \n"
      f"groundedness={verdict.groundedness}"
      )
