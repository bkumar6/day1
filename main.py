from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, status
from typing import Optional

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


# (continued)

from fastapi import FastAPI, HTTPException, status

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