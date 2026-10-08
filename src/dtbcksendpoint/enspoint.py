import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()

HOST = os.environ["DATABRICKS_HOST"].rstrip("/")
TOKEN = os.environ["DATABRICKS_TOKEN"]
WAREHOUSE_ID = os.environ["DATABRICKS_WAREHOUSE_ID"]

API_URL = f"{HOST}/api/2.0/sql/statements"

session = requests.Session()
session.headers.update({
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
})


def execute_sql(statement: str) -> dict:
    response = session.post(
        API_URL,
        json={
            "warehouse_id": WAREHOUSE_ID,
            "statement": statement,
            "wait_timeout": "10s",
            "disposition": "INLINE",
            "format": "JSON_ARRAY",
        },
        timeout=30,
    )
    response.raise_for_status()
    result = response.json()

    statement_id = result["statement_id"]
    deadline = time.monotonic() + 120

    while result["status"]["state"] in {"PENDING", "RUNNING"}:
        if time.monotonic() >= deadline:
            raise TimeoutError(
                f"Statement {statement_id} is still running."
            )

        time.sleep(1)

        response = session.get(
            f"{API_URL}/{statement_id}",
            timeout=30,
        )
        response.raise_for_status()
        result = response.json()


    
    if result["status"]["state"] != "SUCCEEDED":
        raise RuntimeError(result["status"])

    return result


# Test the connection first.
result = execute_sql("SELECT current_user() AS connected_user")

columns = [
    column["name"]
    for column in result["manifest"]["schema"]["columns"]
]

rows = result.get("result", {}).get("data_array", [])

for row in rows:
    print(dict(zip(columns, row)))