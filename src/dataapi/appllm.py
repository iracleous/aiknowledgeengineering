"""

"""


from fastapi import FastAPI
from uvicorn import run
from pydantic import BaseModel

import os
from dotenv import load_dotenv
 
from langchain_core.messages import HumanMessage, SystemMessage

from langchain_openai import AzureChatOpenAI

load_dotenv()



class Ticket(BaseModel):
    ticketId:int
    name:str
    description:str

class DepartmentResponse(BaseModel):
    responseId:str
    representative:str
    info:str

class LlmResponse(BaseModel):
    response:str

class Prompt(BaseModel):
    prompt:str

llm = AzureChatOpenAI(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
)
app = FastAPI()

@app.get("/")
def health():
    return {"status": "ok"}  # Health check for Azure

@app.post("/ticket")
def createTicket(data:Ticket)->DepartmentResponse:
    return DepartmentResponse(
        responseId=str(data.ticketId), 
        representative="dpi",
        info="current SLA 2 days")


@app.post("/llm")
def llmresponse(prompt:Prompt)->LlmResponse:
    return LlmResponse(
        response=llm.invoke(prompt.prompt).content
    )

if __name__ == "__main__":
    run(app, host="0.0.0.0", port=8000)