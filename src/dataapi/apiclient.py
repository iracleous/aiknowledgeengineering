import requests

url = "https://dimmer.icywave-779ead63.germanywestcentral.azurecontainerapps.io/ticket"

payload =   {
    "ticketId" : "12",
    "name": "Dimitris",
    "description":"Broken phone"
    }
 

response = requests.post(
   url,
    json=payload,
    timeout=10,
)

print(response.status_code)  # 201

print(response)

print(response.json())
print(response.json()["responseId"])
