import requests
import json

# URL of the API endpoint
url = "http://localhost:8002/api/recipes/105/analyze"

# JSON payload
payload = {
  "apply_patches": True,
  "reparse": True
}


# Headers to specify JSON content
headers = {
    "Content-Type": "application/json"
}

# Send the POST request
response = requests.post(url, data=json.dumps(payload), headers=headers)

# Check if the request was successful
if response.status_code == 200:
    print("Request successful!")
    print("Response:", response.json())  # Print the JSON response
else:
    print(f"Request failed with status code {response.status_code}")
    print("Response:", response.text)
