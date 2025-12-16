import asyncio
import websockets
import requests
import json
import time


# NOTE: Use HTTPS for Render deployments!
REST_API_URL = "https://day1-backend-test.onrender.com/api/v1/auth/login" # Updated to HTTPS
WS_URI_BASE = "wss://day1-backend-test.onrender.com/api/v1/ai/chat" 
TEST_USER = "testuser"
TEST_PASS = "password123"

async def test_websocket_connection(token: str = None, test_name: str = "Test"):
    """Attempts to establish a WebSocket connection and run multi-message test."""
    
    ws_uri = WS_URI_BASE
    if token:
        ws_uri = f"{WS_URI_BASE}?token={token}"
        print(f"\n--- {test_name}: Connecting with Token ({len(token)} chars) ---")
    else:
        print(f"\n--- {test_name}: Connecting WITHOUT Token ---")

    try:
        async with websockets.connect(ws_uri) as websocket:
            print("🟢 SUCCESS: Connection established!")
            
            # --- MULTI-MESSAGE CONTEXT TEST ---
            
            test_messages = [
                "What is my name?",            # Message 1
                "Tell me about FastAPI.",      # Message 2
                "What was my first question?"  # Message 3 (Should show memory)
            ]

            for i, question in enumerate(test_messages, 1):
                # 1. Send Message
                print(f"[{i}/{len(test_messages)}] > Sending: '{question}'")
                
                await websocket.send(json.dumps({
                    "type": "user_message", 
                    "data": question
                }))
                
                # 2. Receive Response
                response_json = await asyncio.wait_for(websocket.recv(), timeout=15)
                response = json.loads(response_json)
                
                print(f"[{i}/{len(test_messages)}] <- Received: {response.get('data')}")
                
            # --- END MULTI-MESSAGE CONTEXT TEST ---
            
    except websockets.exceptions.InvalidURI as e:
        print(f"❌ FAILURE: Invalid URI. Check configuration. Error: {e}")
    except websockets.exceptions.ConnectionClosed as e:
        print(f"❌ FAILURE: Connection closed by server. Error details: Code {e.code}, Reason: {e.reason}")
    except asyncio.TimeoutError:
        print("🟡 WARNING: Connection established, but timed out waiting for AI response.")
    except Exception as e:
        print(f"An unexpected error occurred: {type(e).__name__}: {e}")


def get_valid_jwt_token():
    """Performs the Phase 1 login to get a fresh token."""
    print("--- Phase 1: Obtaining Valid JWT Token ---")
    try:
        # New credentials based on your database setup
        response = requests.post(REST_API_URL, json={"username": TEST_USER, "password": TEST_PASS})
        response.raise_for_status() # Raise exception for 4xx or 5xx status codes
        token = response.json().get('token')
        print("Token acquired successfully.")
        return token
    except requests.exceptions.RequestException as e:
        print(f"FATAL: Could not get JWT token from REST API. Is the server running? Error: {e}")
        return None

async def main():
    # 1. Get a valid token from the REST API (Tests DB authentication)
    valid_token = get_valid_jwt_token()
    if not valid_token:
        return

    # 2. Test 1: Successful connection with the valid token (Tests Handshake & E2E Chat)
    await test_websocket_connection(token=valid_token, test_name="TEST 1 (VALID TOKEN - DB CHECK)")
    
    # Give the backend a second to ensure connection is fully closed
    await asyncio.sleep(1) 

    # 3. Test 2: Rejected connection without any token (Tests Security Guardrail 1)
    await test_websocket_connection(test_name="TEST 2 (NO TOKEN)")

    # 4. Test 3: Rejected connection with a clearly invalid token (Tests Security Guardrail 2)
    await test_websocket_connection(token="INVALID_TOKEN_123", test_name="TEST 3 (INVALID TOKEN)")


if __name__ == '__main__':
    # WebSockets uses asyncio, so we must run the main async function
    asyncio.run(main())