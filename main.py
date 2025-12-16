from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, status
from fastapi import WebSocket, WebSocketDisconnect, Query, Depends
from jose import jwt, JWTError
from typing import Optional, Annotated 
import json
import asyncio
from sqlalchemy.orm import Session
from database import engine, Base, get_db
from models import User
from auth_handler import create_access_token, decode_access_token
from state_manager import USER_CONTEXT_STORE
from ai_client import get_ai_response # <-- IMPORT FOR PHASE 5

# This command checks all models that inherit from Base and creates 
# the corresponding tables in the SQLite file if they don't exist.
Base.metadata.create_all(bind=engine)

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


# This function is run during the connection handshake (Phase 3 Dependency)
async def get_current_user_from_token(websocket: WebSocket, token: str = Query(...)):
    # 1. Use the REAL decoder to check the token
    username = decode_access_token(token) 
    
    # 2. Check the result
    if username is None:
        # If decode_access_token returns None, the token is invalid or expired.
        raise WebSocketDisconnect(
            code=status.WS_1008_POLICY_VIOLATION, 
            reason="Token is invalid or expired."
        )
    
    # 3. SUCCESS PATH: Return the authenticated username
    return username


app = FastAPI(title="Secure AI Backend")


# --- CORS Configuration ---
origins = [
    "http://localhost:8000", 
    "http://127.0.0.1:8000",
    "http://localhost:3000", 
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"], 
)


@app.post(
    "/api/v1/auth/login",
    response_model=TokenResponse, 
    responses={
        401: {"model": ErrorResponse, "description": "Authentication Failed"}
    }
)
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    # 1. Query the database for the user (Phase 4 Authentication)
    user = db.query(User).filter(User.username == credentials.username).first()

    # 2. Verify the user and password
    if user is None or user.hashed_password != credentials.password: 
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. If valid, generate and return the JWT
    token = create_access_token(user_id=user.username)
    return TokenResponse(token=token)
    

@app.websocket("/api/v1/ai/chat")
async def websocket_endpoint(
    websocket: WebSocket, 
    username: str = Depends(get_current_user_from_token)
):
    await websocket.accept()
    
    # 1. Initialize context for the user if it doesn't exist
    if username not in USER_CONTEXT_STORE:
        USER_CONTEXT_STORE[username] = []
        
    print(f"User {username} connected. History length: {len(USER_CONTEXT_STORE[username])}")
    
    try:
        while True:
            data = await websocket.receive_text()
            user_message = json.loads(data)
            question_text = user_message.get("data", "").strip()

            # 2. Add the new user message to the context store
            USER_CONTEXT_STORE[username].append({
                "role": "user",
                "content": question_text
            })

            # --- PHASE 5: EXTERNAL AI CALL ---
            
            # 3. Get the full history for context
            context_for_api = USER_CONTEXT_STORE[username]
            
            # CALL THE REAL AI FUNCTION (This replaces all placeholder logic)
            # This function handles the formatting and API request
            raw_ai_response = await asyncio.to_thread(get_ai_response, username, context_for_api)
            
            # --- END PHASE 5 ---

            # 4. Add AI's response to the context store
            USER_CONTEXT_STORE[username].append({
                "role": "ai",
                "content": raw_ai_response
            })
            
            # 5. Send the response back to the client
            await websocket.send_json({
                "type": "ai_response",
                "data": raw_ai_response,
                "status": "complete"
            })
            
    except WebSocketDisconnect:
        print(f"User {username} disconnected. Context retained.")
    except Exception as e:
        print(f"An unexpected error occurred for {username}: {e}")