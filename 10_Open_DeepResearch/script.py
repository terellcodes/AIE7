import requests
import json

# Correct endpoint URL
url = "http://localhost:8000/api/v1/research/start"

# Request payload
data = {
    "topic": "AI Ethics in Healthcare",
    "search_api": "tavily",
    "number_of_queries": 1,
    "max_search_depth": 1
}

try:
    print(f"Making request to: {url}")
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        result = response.json()
        thread_id = result["thread_id"]
        print(f"Thread ID: {thread_id}")
    else:
        print(f"Error: {response.json()}")
        
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to API. Make sure the server is running on localhost:8000")
except KeyError as e:
    print(f"❌ Missing key in response: {e}")
    print(f"Full response: {response.json()}")
except Exception as e:
    print(f"❌ Error: {e}")

# Approve plan
if data["status"] == "awaiting_feedback":
    requests.post("http://localhost:8000/api/v1/research/feedback", json={
        "thread_id": thread_id,
        "approve": True
    })

# Get final report
status = requests.get(f"http://localhost:8000/api/v1/research/status/{thread_id}")
if status.json()["status"] == "completed":
    print(status.json()["final_report"])