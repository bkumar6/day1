# websocket_test_client.py

import asyncio
import websockets
import requests
import json

REST_API_URL = "https://day1-backend-test.onrender.com/api/v1/auth/login"
WS_URI_BASE = "wss://day1-backend-test.onrender.com/api/v1/ai/chat"

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
                "Tell me about FastAPI.",
                "What was my first question?",
            ]

            for i, question in enumerate(test_messages, 1):
                await websocket.send(json.dumps({
                    "type": "user_message",
                    "data": question
                }))

                response = await asyncio.wait_for(websocket.recv(), timeout=20)
                parsed = json.loads(response)

                print(f"[{i}] AI:", parsed.get("data"))

    except websockets.exceptions.ConnectionClosed as e:
        print(f"❌ Connection closed | Code: {e.code}, Reason: {e.reason}")
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")


def get_valid_jwt_token():
    print("🔐 Requesting JWT token...")
    response = requests.post(
        REST_API_URL,
        json={"username": TEST_USER, "password": TEST_PASS}
    )
    response.raise_for_status()
    print("✅ Token acquired")
    return response.json()["token"]


async def main():
    token = get_valid_jwt_token()

    await test_websocket_connection(
        token=token,
        test_name="TEST 1 (VALID TOKEN)"
    )

    await asyncio.sleep(1)

    await test_websocket_connection(
        test_name="TEST 2 (NO TOKEN)"
    )

    await test_websocket_connection(
        token="INVALID_TOKEN",
        test_name="TEST 3 (INVALID TOKEN)"
    )


if __name__ == "__main__":
    asyncio.run(main())
