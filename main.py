# main.py

from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, status, WebSocket, WebSocketDisconnect, Query, Depends
from sqlalchemy.orm import Session
import json

from database import engine, Base, get_db
from models import User
from auth_handler import create_access_token, decode_access_token
from state_manager import USER_CONTEXT_STORE
from ai_client import get_ai_response, initialize_ai_client


# --- Initial Setup ---
Base.metadata.create_all(bind=engine)


# --- Schemas ---
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
async def get_current_user_from_token(
    websocket: WebSocket,
    token: str = Query(...)
):
    username = decode_access_token(token)
    if username is None:
        raise WebSocketDisconnect(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Token is invalid or expired"
        )
    return username


# --- App ---
app = FastAPI(title="Secure AI Backend")


# --- CORS ---
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


# --- Startup Event ---
@app.on_event("startup")
def startup_event():
    """
    Initialize Gemini client ONCE when the app starts.
    """
    initialize_ai_client()


# --- REST API ---
@app.post(
    "/api/v1/auth/login",
    response_model=TokenResponse,
    responses={401: {"model": ErrorResponse}},
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


# --- WebSocket Endpoint ---
@app.websocket("/api/v1/ai/chat")
async def websocket_endpoint(
    websocket: WebSocket,
    username: str = Depends(get_current_user_from_token),
):
    await websocket.accept()

    if username not in USER_CONTEXT_STORE:
        USER_CONTEXT_STORE[username] = []

    print(f"🟢 {username} connected | Context length: {len(USER_CONTEXT_STORE[username])}")

    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            question_text = payload.get("data", "").strip()

            # Store user message
            USER_CONTEXT_STORE[username].append({
                "role": "user",
                "content": question_text
            })

            # AI call
            ai_response = await get_ai_response(
                username=username,
                context_history=USER_CONTEXT_STORE[username]
            )

            # Store AI response
            USER_CONTEXT_STORE[username].append({
                "role": "ai",
                "content": ai_response
            })

            await websocket.send_json({
                "type": "ai_response",
                "data": ai_response,
                "status": "complete"
            })

    except WebSocketDisconnect:
        print(f"🔌 {username} disconnected — context retained")

    except Exception as e:
        print(f"❌ Error for {username}: {e}")
