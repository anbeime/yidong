import requests
import json

# 测试生成API
url = "http://localhost:9090/api/generate"
headers = {"Content-Type": "application/json"}
data = {"requirement": "创建一个简单的电商网站"}

try:
    response = requests.post(url, headers=headers, data=json.dumps(data))
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")