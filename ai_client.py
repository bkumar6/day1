# ai_client.py
import os
import asyncio
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = None
# gemini-pro is the most reliable fallback for older SDK versions
MODEL_NAME = "gemini-pro" 

async def initialize_ai_client():
    global client
    print("Attempting to initialize AI Client...")
    try:
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ Error: No API Key found.")
            return
            
        client = genai.Client(api_key=api_key)
        print("✅ AI Client initialized successfully.")
    except Exception as e:
        print(f"❌ Initialization Error: {e}")
        client = None

async def get_ai_response(username: str, context_history: list[dict]) -> str:
    if not client:
        return "ERROR: AI service not available."

    # Get the latest user message content as a simple string
    user_query = context_history[-1]["content"] if context_history else "Hello"

    try:
        # Using to_thread for non-blocking execution
        # Passing contents as a simple string for maximum compatibility
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=MODEL_NAME,
            contents=user_query
        )
        
        # Robust text extraction
        if hasattr(response, 'text'):
            return response.text
        return str(response)
        
    except Exception as e:
        print(f"❌ API Failure: {str(e)}")
        return f"AI Error: {str(e)}"