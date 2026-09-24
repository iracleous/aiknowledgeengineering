import os
import secrets
from typing import Annotated
from dotenv import load_dotenv

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from uvicorn import run

load_dotenv()


app = FastAPI()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


class IncidentRequest(BaseModel):
    title: str
    severity: str


def verify_api_key(
    supplied_key: Annotated[str | None, Depends(api_key_header)],
) -> None:
    expected_key = os.getenv("INCIDENTS_API_KEY")

    if supplied_key is None or not secrets.compare_digest(
        supplied_key, expected_key
    ):
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.post("/incidents", status_code=201)
def create_incident(
    incident: IncidentRequest,
    _: Annotated[None, Depends(verify_api_key)],
):
    return {
        "id": 101,
        "title": incident.title,
        "severity": incident.severity,
        "status": "open",
    }


if __name__ == "__main__":
    run(app, host="0.0.0.0", port=8000)