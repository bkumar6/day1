# main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, Depends, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
import json

from database import engine, Base, get_db
from models import User
from auth_handler import create_access_token, decode_access_token
from state_manager import USER_CONTEXT_STORE
from ai_client import get_ai_response, initialize_ai_client

# --- Initial Setup ---
Base.metadata.create_all(bind=engine)
app = FastAPI(title="Secure AI Backend")

# --- Schemas ---
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    token: str

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Startup Event ---
@app.on_event("startup")
async def startup_event():
    await initialize_ai_client()

# --- Auth Dependencies ---
async def get_current_user_from_token(websocket: WebSocket, token: str = Query(...)):
    username = decode_access_token(token)
    if username is None:
        # Don't accept the connection if token is invalid
        return None
    return username

# --- REST API (Login Endpoint) ---
@app.post("/api/v1/auth/login", response_model=TokenResponse)
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == credentials.username).first()
    if user is None or user.hashed_password != credentials.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    token = create_access_token(user_id=user.username)
    return TokenResponse(token=token)

# --- WebSocket Endpoint ---
@app.websocket("/api/v1/ai/chat")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...) # Extract token from query params
):
    # Authenticate immediately
    username = decode_access_token(token)
    if username is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()
    
    # Requirement: AI Memory initialization
    if username not in USER_CONTEXT_STORE:
        USER_CONTEXT_STORE[username] = []

    print(f"🟢 {username} connected")

    try:
        while True:
            # 1. Receive data
            data = await websocket.receive_text()
            payload = json.loads(data)
            question_text = payload.get("data", "").strip()

            # 2. Update Memory (User Side)
            USER_CONTEXT_STORE[username].append({"role": "user", "content": question_text})

            # 3. Get AI Response (Passing full history for memory)
            ai_response = await get_ai_response(
                username=username,
                context_history=USER_CONTEXT_STORE[username]
            )

            # 4. Update Memory (AI Side)
            USER_CONTEXT_STORE[username].append({"role": "ai", "content": ai_response})

            # 5. Send Structured Log Data (Task requirement: Timestamp + Q + A)
            await websocket.send_json({
                "type": "ai_response",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "query": question_text,
                "data": ai_response,
                "status": "complete"
            })

    except WebSocketDisconnect:
        print(f"🔌 {username} disconnected.")
    except Exception as e:
        print(f"❌ Error: {e}")