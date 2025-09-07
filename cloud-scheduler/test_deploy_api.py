import requests
import json

# 测试部署API
url = "http://localhost:9090/api/apps/test123/deploy"
headers = {"Content-Type": "application/json"}
data = {"app_id": "test123"}

try:
    response = requests.post(url, headers=headers, data=json.dumps(data))
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")