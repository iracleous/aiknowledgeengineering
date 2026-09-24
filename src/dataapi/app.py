"""

"""


from fastapi import FastAPI
from uvicorn import run
from pydantic import BaseModel

class Ticket(BaseModel):
    ticketId:int
    name:str
    description:str

class DepartmentResponse(BaseModel):
    responseId:str
    representative:str
    info:str

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


if __name__ == "__main__":
    run(app, host="0.0.0.0", port=8000)