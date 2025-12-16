from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, status
from fastapi import WebSocket, WebSocketDisconnect, Query, Depends
from jose import jwt, JWTError
from typing import Optional, Annotated # <-- ADDED ANNOTATED HERE
import json
import asyncio

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


# This function is run during the connection handshake
async def get_current_user_from_token(websocket: WebSocket, token: str = Query(...)):
    # Placeholder for your actual verification logic
    # In Phase 2, this function should raise an exception if the token is invalid
    # For now, we'll just return the username for use in the chat loop
    if token:
        return "testuser"
    # Simulate extraction of username from a valid token
    raise WebSocketDisconnect(code=1008)  # Policy Violation


app = FastAPI(title="Secure AI Backend")


# --- CORS Configuration ---
# 1. Define the origins (URLs) that are allowed to make requests to your API.
#    Note: Always use specific origins in production, never ["*"]
origins = [
    "http://localhost:8000",  # Teammate's local frontend development server
    "http://127.0.0.1:8000",
    "http://localhost:3000",  # Common frontend framework ports (if applicable)
    "http://127.0.0.1:3000",
    # If your frontend is also deployed: "https://your-frontend-domain.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,             # Allows the origins listed above
    allow_credentials=True,            # Allows cookies and authorization headers
    allow_methods=["*"],               # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],               # Allows all headers
)

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
async def websocket_endpoint(websocket: WebSocket,
    # Inject the username after the JWT is verified by the dependency
    username: Annotated[str, Depends(get_current_user_from_token)]
):
    # If the dependency (get_current_user_from_token) did not raise an exception,
    # the connection is secure, and we accept it.
    await websocket.accept()

    print(f"User {username} connected and authenticated. Starting chat loop.")
    # 

    try:
        while True:
            # 1. RECEIVE: Wait for the client to send a message
            # Use receive_text() since the client sends a JSON string
            data = await websocket.receive_text()
            
            # Parse the agreed-upon inbound JSON contract
            try:
                user_message = json.loads(data)
                question_text = user_message.get("data", "").strip()
                print(f"[{username}] received: {question_text}")

            except json.JSONDecodeError:
                print("Received invalid JSON format. Skipping.")
                continue

            # 2. PROCESS (Phase 3 Simulation: Replace this with real AI later)
            if not question_text:
                response = "Please type a question."
            elif "hello" in question_text.lower() or "hi" in question_text.lower():
                response = f"Hello {username}! I am your secure AI assistant. How can I help you today?"
            else:
                # Simulate a delayed response to mimic AI processing time
                await asyncio.sleep(0.5) 
                response = f"I received your query: '{question_text[:50]}...'. My full AI response is a placeholder for Phase 3 testing."
            
            # 3. SEND: Format the response into the outbound JSON contract and send
            # Use send_json() for cleaner, structured data transmission
            await websocket.send_json({
                "type": "ai_response",
                "data": response,
                "status": "complete"
            })
            
    except WebSocketDisconnect:
        # This handles when the frontend closes the connection gracefully
        print(f"User {username} disconnected.")
    except Exception as e:
        # Catch unexpected errors to prevent the server from crashing
        print(f"An unexpected error occurred in chat loop for {username}: {e}")