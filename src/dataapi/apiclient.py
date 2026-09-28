import requests

url = "http://localhost:8000/llm"

payload =   {
    "prompt" : "What is CI/CD"
    }
 

response = requests.post(
   url,
   json=payload,
   timeout=10,
)

print(response.status_code)  # 201

print(response)

print(response.json())
print(response.json()["response"])
