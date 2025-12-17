# ai_client.py
import os
import requests
import asyncio
from dotenv import load_dotenv

load_dotenv()

# We keep these for the main.py compatibility
client = None 

async def initialize_ai_client():
    """No complex initialization needed for REST calls."""
    print("✅ AI REST Client ready.")
    return True

async def get_ai_response(username: str, context_history: list[dict]) -> str:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return "ERROR: API Key missing."

    # Use the official v1 endpoint URL
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    # Get the last message from user
    user_text = context_history[-1]["content"] if context_history else "Hello"

    # Standard Google AI REST payload
    payload = {
        "contents": [{
            "parts": [{"text": user_text}]
        }]
    }

    try:
        # Run the blocking request in a thread to keep the WebSocket alive
        response = await asyncio.to_thread(
            requests.post, 
            url, 
            json=payload, 
            timeout=10
        )
        
        result = response.json()
        
        # Dig the text out of the response
        if "candidates" in result:
            return result["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return f"AI Error: {result.get('error', {}).get('message', 'Unknown Error')}"

    except Exception as e:
        print(f"❌ REST API Failure: {str(e)}")
        return f"AI Error: {str(e)}"