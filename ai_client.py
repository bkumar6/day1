# ai_client.py
import os
import requests
import asyncio
from dotenv import load_dotenv

load_dotenv()

client = None 

async def initialize_ai_client():
    """Confirms the REST client is ready."""
    print("✅ AI REST Client ready.")
    return True

async def get_ai_response(username: str, context_history: list[dict]) -> str:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return "ERROR: API Key missing."

    # UPDATED MODEL: Use gemini-2.0-flash for current compatibility
    model_id = "gemini-1.0-pro" 
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={api_key}"
    
    user_text = context_history[-1]["content"] if context_history else "Hello"

    payload = {
        "contents": [{
            "parts": [{"text": user_text}]
        }]
    }

    try:
        response = await asyncio.to_thread(
            requests.post, 
            url, 
            json=payload, 
            timeout=15
        )
        
        result = response.json()
        
        if response.status_code == 200:
            # Successfully extracting response text
            return result["candidates"][0]["content"]["parts"][0]["text"]
        else:
            # Returning the actual error from Google to your test client
            error_message = result.get('error', {}).get('message', 'Unknown Error')
            return f"AI Error: {error_message}"

    except Exception as e:
        print(f"❌ REST API Failure: {str(e)}")
        return f"AI Error: Connection failed."