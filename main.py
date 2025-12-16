# main.py

from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, status
from fastapi import WebSocket, WebSocketDisconnect, Query, Depends
from typing import Annotated 
import json
import asyncio
from sqlalchemy.orm import Session
from database import engine, Base, get_db
from models import User
from auth_handler import create_access_token, decode_access_token
from state_manager import USER_CONTEXT_STORE
from ai_client import get_ai_response # Final import for Phase 5


# --- Initial Setup ---
Base.metadata.create_all(bind=engine)

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    status: str = "success"
    token: str

class ErrorResponse(BaseModel):
    status: str = "error"
    message: str


# --- Dependencies ---
async def get_current_user_from_token(websocket: WebSocket, token: str = Query(...)):
    username = decode_access_token(token) 
    
    if username is None:
        raise WebSocketDisconnect(
            code=status.WS_1008_POLICY_VIOLATION, 
            reason="Token is invalid or expired."
        )
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


# --- REST API Endpoint ---
@app.post(
    "/api/v1/auth/login",
    response_model=TokenResponse, 
    responses={
        401: {"model": ErrorResponse, "description": "Authentication Failed"}
    }
)
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == credentials.username).first()

    if user is None or user.hashed_password != credentials.password: 
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = create_access_token(user_id=user.username)
    return TokenResponse(token=token)
    

# --- WebSocket Endpoint (Final Logic) ---
@app.websocket("/api/v1/ai/chat")
async def websocket_endpoint(
    websocket: WebSocket, 
    username: str = Depends(get_current_user_from_token)
):
    await websocket.accept()
    
    if username not in USER_CONTEXT_STORE:
        USER_CONTEXT_STORE[username] = []
        
    print(f"User {username} connected. History length: {len(USER_CONTEXT_STORE[username])}")
    
    try:
        while True:
            data = await websocket.receive_text()
            user_message = json.loads(data)
            question_text = user_message.get("data", "").strip()

            # 1. Add user message to context store
            USER_CONTEXT_STORE[username].append({
                "role": "user",
                "content": question_text
            })

            # 2. Prepare context for API call
            context_for_api = USER_CONTEXT_STORE[username]
            
            # --- PHASE 5 CRITICAL FIX: ASYNCIO.TO_THREAD ---
            # Call the synchronous get_ai_response in a separate thread to prevent
            # blocking the main event loop and resolve the timeout warning.
            raw_ai_response = await asyncio.to_thread(
                get_ai_response, 
                username, 
                context_for_api
            )
            
            # 3. Add AI's response to the context store
            USER_CONTEXT_STORE[username].append({
                "role": "ai",
                "content": raw_ai_response
            })
            
            # 4. Send the response back to the client
            await websocket.send_json({
                "type": "ai_response",
                "data": raw_ai_response,
                "status": "complete"
            })
            
    except WebSocketDisconnect:
        print(f"User {username} disconnected. Context retained.")
    except Exception as e:
        print(f"An unexpected error occurred for {username}: {e}")