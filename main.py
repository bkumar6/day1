from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, status
from fastapi import WebSocket, WebSocketDisconnect
from jose import jwt, JWTError # Added import for JWT handling
from typing import Optional
import json

# 1. Contract for the incoming login request
class LoginRequest(BaseModel):
    username: str
    password: str

# 2. Contract for the outgoing success response
class TokenResponse(BaseModel):
    status: str = "success"
    token: str

# 3. Contract for the outgoing error response (optional but good practice)
class ErrorResponse(BaseModel):
    status: str = "error"
    message: str



app = FastAPI(title="Secure AI Backend")

# --- Dummy Database/User Setup ---
# This simulates checking the database. We use a hardcoded user for Phase 1.
HARDCODED_USERNAME = "testuser"
HARDCODED_PASSWORD = "password123"
DUMMY_JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InRlc3R1c2VyIiwiaXNzIjoiYmFja2VuZCIsImV4cCI6MjAwMDAwMDAwMH0.s_MOCK_TOKEN_FOR_FRONTEND_TESTING_12345"

@app.post(
    "/api/v1/auth/login",
    response_model=TokenResponse, # Use the success contract for documentation
    responses={
        401: {"model": ErrorResponse, "description": "Authentication Failed"}
    }
)
async def login(credentials: LoginRequest):
    """
    Handles user login. Verifies credentials and issues a token.
    (Currently uses dummy verification and issues a mock token).
    """
    if credentials.username == HARDCODED_USERNAME and credentials.password == HARDCODED_PASSWORD:
        # SUCCESS: Return the agreed-upon dummy token
        return TokenResponse(token=DUMMY_JWT_TOKEN)
    else:
        # FAILURE: Raise an HTTP exception (401 Unauthorized)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# --- JWT Configuration (Placeholder for now) ---
# In a real app, use an environment variable for a complex secret
SECRET_KEY = "SUPER_SECRET_KEY_FOR_JWT_SIGNING" 
ALGORITHM = "HS256"

def verify_jwt_and_get_username(token: str) -> str:
    """
    Simulates JWT verification using a real library structure.
    In a real app, you'd decode and check token validity and expiration.
    """
    if token == DUMMY_JWT_TOKEN:
        # Since our DUMMY_JWT_TOKEN is hardcoded, we mock the result of decoding
        return HARDCODED_USERNAME
    
    # In a real scenario, you'd use the library to check the token signature:
    try:
        # payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # username: str = payload.get("username")
        # if username is None:
        #     raise JWTError
        # return username
        pass # Using the simple check above for the dummy token
    except JWTError:
        # Raised if the signature is invalid, token is expired, etc.
        raise ValueError("Invalid authentication token")
    
    # Fallback for any other invalid token not matching the dummy
    raise ValueError("Invalid authentication token")

@app.websocket("/api/v1/ai/chat")
async def websocket_endpoint(websocket: WebSocket, token: str = None):
    # Connection Acceptance and Auth Check (Handshake)
    if not token:
        # This will fail the handshake before accepting the connection
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Authentication token missing")
        return

    try:
        # Verify the token using the function from Step 2
        username = verify_jwt_and_get_username(token)
        print(f"User {username} authenticated. Establishing connection.")
        await websocket.accept() # CRITICAL: Accept the connection only if authenticated
        
    except ValueError as e:
        # Close connection with a policy violation code if auth fails
        print(f"Authentication failed: {e}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason=str(e))
        return

    # Communication Loop
    try:
        while True:
            # Server waits to receive a message from the client
            data = await websocket.receive_text()
            
            # 1. Parse the incoming JSON message (according to the contract)
            message = json.loads(data)
            print(f"[{username}] received: {message.get('data')}")
            
            # 2. Process the AI Query (DUMMY RESPONSE)
            user_question = message.get("data", "No question")
            ai_response = f"Hello {username}, you asked: '{user_question}'. This is the AI's dummy answer."
            
            # 3. Send the response back (according to the contract)
            response_json = json.dumps({
                "type": "ai_response",
                "data": ai_response,
                "status": "complete"
            })
            await websocket.send_text(response_json)

    except WebSocketDisconnect:
        print(f"User {username} disconnected.")
    except Exception as e:
        print(f"An error occurred: {e}")