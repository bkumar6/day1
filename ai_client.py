# ai_client.py
import os
import requests
import asyncio
from dotenv import load_dotenv

load_dotenv()

# Keep these global variables for main.py compatibility
client = None 

async def initialize_ai_client():
    """No complex initialization needed for direct REST calls."""
    print("✅ AI REST Client ready.")
    return True

async def get_ai_response(username: str, context_history: list[dict]) -> str:
    # Use the key from your environment
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return "ERROR: API Key missing in server environment."

    # Using the v1 production endpoint directly
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    # Get the latest user message
    user_text = context_history[-1]["content"] if context_history else "Hello"

    # Exact JSON format required by Google's API
    payload = {
        "contents": [{
            "parts": [{"text": user_text}]
        }]
    }

    try:
        # Run the blocking network request in a separate thread 
        # to keep your WebSocket responsive
        response = await asyncio.to_thread(
            requests.post, 
            url, 
            json=payload, 
            timeout=15
        )
        
        data = response.json()
        
        # Check for successful response
        if response.status_code == 200:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            error_msg = data.get("error", {}).get("message", "Unknown API Error")
            return f"AI Error: {error_msg}"

    except Exception as e:
        print(f"❌ REST API Failure: {str(e)}")
        return f"AI Error: Connection failed."