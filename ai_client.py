# ai_client.py
import os
import requests
import asyncio
from dotenv import load_dotenv

load_dotenv()

client = None 

async def initialize_ai_client():
    """Simple confirmation for the REST client."""
    print("✅ AI REST Client ready.")
    return True

async def get_ai_response(username: str, context_history: list[dict]) -> str:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return "ERROR: API Key missing."

    # Use v1beta and the -latest suffix for maximum compatibility
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
    
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
        
        # Robust parsing of the Gemini REST response
        if response.status_code == 200:
            return result["candidates"][0]["content"]["parts"][0]["text"]
        else:
            # This will show the actual error message from Google in your test client
            return f"AI Error: {result.get('error', {}).get('message', 'Unknown Error')}"

    except Exception as e:
        print(f"❌ REST API Failure: {str(e)}")
        return f"AI Error: Connection failed."