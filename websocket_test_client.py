# websocket_test_client.py
import asyncio
import websockets
import requests
import json

# Ensure these match your Render URL exactly
BASE_URL = "day1-backend-test.onrender.com"
REST_API_URL = f"https://{BASE_URL}/api/v1/auth/login"
WS_URI_BASE = f"wss://{BASE_URL}/api/v1/ai/chat"

TEST_USER = "testuser"
TEST_PASS = "password123"

async def test_websocket_connection(token: str = None, test_name: str = "Test"):
    ws_uri = WS_URI_BASE
    if token:
        ws_uri = f"{WS_URI_BASE}?token={token}"
        print(f"\n--- {test_name}: WITH TOKEN ---")
    else:
        print(f"\n--- {test_name}: WITHOUT TOKEN ---")

    try:
        async with websockets.connect(ws_uri) as websocket:
            print("🟢 WebSocket connected")
            test_messages = [
                "What is my name?",
                "What was my first question?",
            ]

            for i, question in enumerate(test_messages, 1):
                await websocket.send(json.dumps({"data": question}))
                response = await asyncio.wait_for(websocket.recv(), timeout=20)
                parsed = json.loads(response)
                
                # Check for the new structured log format
                print(f"[{i}] [{parsed.get('timestamp')}] AI Response: {parsed.get('data')}")

    except Exception as e:
        print(f"❌ Connection Result: {e}")

def get_valid_jwt_token():
    print("🔐 Requesting JWT token...")
    try:
        response = requests.post(
            REST_API_URL,
            json={"username": TEST_USER, "password": TEST_PASS}
        )
        response.raise_for_status()
        print("✅ Token acquired")
        return response.json()["token"]
    except Exception as e:
        print(f"❌ Login Failed: {e}")
        return None

async def main():
    token = get_valid_jwt_token()
    if token:
        await test_websocket_connection(token=token, test_name="TEST 1")
    await test_websocket_connection(test_name="TEST 2 (NO TOKEN)")

if __name__ == "__main__":
    asyncio.run(main())