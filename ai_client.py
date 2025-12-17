# ai_client.py
import os
import requests
import asyncio
from dotenv import load_dotenv

load_dotenv()

# Global variable for compatibility with main.py
client = None 

async def initialize_ai_client():
    """Confirms the Groq REST client is ready."""
    print("✅ Groq AI Client ready.")
    return True

async def get_ai_response(username: str, context_history: list[dict]) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "ERROR: Groq API Key missing in environment."

    url = "https://api.groq.com/openai/v1/chat/completions"
    
    # Map context to Groq/OpenAI format: assistant instead of ai
    messages = []
    for m in context_history:
        role = "assistant" if m["role"] == "ai" else "user"
        messages.append({"role": role, "content": m["content"]})

    # Using Llama 3.3 70B - it's free, smart, and extremely fast
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "temperature": 0.7
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        # Run the network request in a separate thread to keep WebSockets alive
        response = await asyncio.to_thread(
            requests.post, 
            url, 
            json=payload, 
            headers=headers, 
            timeout=15
        )
        
        data = response.json()
        
        if response.status_code == 200:
            return data["choices"][0]["message"]["content"]
        else:
            error_msg = data.get("error", {}).get("message", "Unknown Groq Error")
            return f"AI Error: {error_msg}"

    except Exception as e:
        print(f"❌ Groq API Failure: {str(e)}")
        return "AI Error: Connection to Groq failed."