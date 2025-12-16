# auth_handler.py
import time
from jose import jwt, JWTError
from fastapi import status, HTTPException

# --- JWT Configuration ---
SECRET_KEY = "YOUR_SUPER_SECRET_KEY_REPLACE_ME" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # Token validity period

# --- Function 1: Create JWT Token ---
def create_access_token(user_id: str) -> str:
    """Generates a JWT token for the authenticated user."""
    
    # Define the claims (payload) for the token
    to_encode = {
        "user_id": user_id,
        "iss": "backend",  # Issuer
        # Calculate expiration time: current time + expiry minutes
        "exp": time.time() + (ACCESS_TOKEN_EXPIRE_MINUTES * 60) 
    }
    
    # Encode the payload using the secret key and algorithm
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- Function 2: Decode/Verify JWT Token (Used in WebSocket dependency) ---
def decode_access_token(token: str) -> str | None:
    """Decodes and validates a JWT token, returning the user_id if valid."""
    try:
        # Decode and verify the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check if the token has expired
        if payload.get("exp") < time.time():
            return None # Token expired
            
        return payload.get("user_id")
        
    except JWTError:
        # This catches signature errors, wrong algorithm, etc.
        return None # Invalid token
    except Exception:
        # Catch any other unexpected decoding errors
        return None