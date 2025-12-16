import asyncio
import websockets
import requests
import json
import time

# --- CONFIGURATION (Match your backend settings) ---
REST_API_URL = "http://day1-backend-test.onrender.com/api/v1/auth/login" # Replace with your Render/VPS URL if deployed
WS_URI_BASE = "wss://day1-backend-test.onrender.com/api/v1/ai/chat" # Replace with your Render/VPS URL if deployed
TEST_USER = "testuser"
TEST_PASS = "password123"

async def test_websocket_connection(token: str = None, test_name: str = "Test"):
    """Attempts to establish a WebSocket connection."""
    
    ws_uri = WS_URI_BASE
    if token:
        # Build the URI with the JWT for authentication
        ws_uri = f"{WS_URI_BASE}?token={token}"
        print(f"\n--- {test_name}: Connecting with Token ({len(token)} chars) ---")
    else:
        print(f"\n--- {test_name}: Connecting WITHOUT Token ---")

    try:
        # 1. Establish the connection (the handshake)
        async with websockets.connect(ws_uri) as websocket:
            print("🟢 SUCCESS: Connection established!")
            
            # 2. Test sending and receiving a message (Simple Q&A)
            question = "Hello AI, what is your name?"
            print(f"> Sending question: '{question}'")
            
            # Use the agreed-upon message contract (Phase 2 schema)
            await websocket.send(json.dumps({
                "type": "user_message", 
                "data": question
            }))
            
            # 3. Wait for the response
            response_json = await asyncio.wait_for(websocket.recv(), timeout=5)
            response = json.loads(response_json)
            
            print(f"<- Received AI response (Type: {response.get('type')}): {response.get('data')}...")
            
    except websockets.exceptions.InvalidURI as e:
        print(f"❌ FAILURE: Invalid URI. Check configuration. Error: {e}")
    except websockets.exceptions.ConnectionClosed as e:
        # This is the expected result for a rejected connection (security test)
        print(f"❌ FAILURE: Connection closed by server. This is expected if the token was invalid/missing.")
        print(f"Error details: Code {e.code}, Reason: {e.reason}")
    except asyncio.TimeoutError:
        print("🟡 WARNING: Connection established, but timed out waiting for AI response. (Check backend processing)")
    except Exception as e:
        print(f"An unexpected error occurred: {type(e).__name__}: {e}")

def get_valid_jwt_token():
    """Performs the Phase 1 login to get a fresh token."""
    print("--- Phase 1: Obtaining Valid JWT Token ---")
    try:
        response = requests.post(REST_API_URL, json={"username": TEST_USER, "password": TEST_PASS})
        response.raise_for_status() # Raise exception for 4xx or 5xx status codes
        token = response.json().get('token')
        print("Token acquired successfully.")
        return token
    except requests.exceptions.RequestException as e:
        print(f"FATAL: Could not get JWT token from REST API. Is the server running? Error: {e}")
        return None

async def main():
    # 1. Get a valid token from the REST API
    valid_token = get_valid_jwt_token()
    if not valid_token:
        return

    # 2. Test 1: Successful connection with the valid token
    await test_websocket_connection(token=valid_token, test_name="TEST 1 (VALID TOKEN)")
    
    # Give the backend a second to ensure connection is fully closed
    await asyncio.sleep(1) 

    # 3. Test 2: Rejected connection without any token
    await test_websocket_connection(test_name="TEST 2 (NO TOKEN)")

    # 4. Test 3: Rejected connection with a clearly invalid token
    await test_websocket_connection(token="INVALID_TOKEN_123", test_name="TEST 3 (INVALID TOKEN)")


if __name__ == '__main__':
    # WebSockets uses asyncio, so we must run the main async function
    asyncio.run(main())