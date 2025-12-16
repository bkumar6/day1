# test_client.py
import requests
import json

API_URL = "http://127.0.0.1:8000/api/v1/auth/login"

# --- SUCCESS TEST ---
print("--- TESTING SUCCESSFUL LOGIN ---")
success_payload = {
    "username": "testuser",
    "password": "password123"
}
response_success = requests.post(API_URL, json=success_payload)

print(f"Status Code: {response_success.status_code}")
if response_success.status_code == 200:
    print("SUCCESS! Token received:")
    data = response_success.json()
    print(data.get('token'))
else:
    print(f"FAILURE: {response_success.json()}")

# --- FAILURE TEST ---
print("\n--- TESTING FAILED LOGIN ---")
fail_payload = {
    "username": "wronguser",
    "password": "wrongpassword"
}
response_fail = requests.post(API_URL, json=fail_payload)

print(f"Status Code: {response_fail.status_code}")
if response_fail.status_code == 401:
    print("SUCCESS! Received 401 Unauthorized as expected.")
    print(response_fail.json())
else:
    print(f"FAILURE: Expected 401, got {response_fail.status_code}")