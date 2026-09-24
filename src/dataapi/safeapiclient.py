import json
import os

import requests

response = requests.post(
    "http://127.0.0.1:8000/incidents",
    headers={"X-API-Key": "fwer123523fewy45yervwf32r3AScc@@#$"},
    json={
        "title": "Database unavailable",
        "severity": "critical",
    },
    timeout=10,
)

print("Status:", response.status_code)
print(response.json())