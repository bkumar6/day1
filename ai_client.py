# ai_client.py
import os
import asyncio
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = None
# We go back to the modern model name, but fix the client routing
MODEL_NAME = "gemini-1.5-flash" 

async def initialize_ai_client():
    global client
    print("Attempting to initialize Gemini AI Client...")
    try:
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ Error: No API Key found.")
            return
            
        # FORCE the client to use the Google AI Studio backend, not Vertex AI
        # This is done by passing the api_key directly to the Client 
        # and ensuring it's not looking for Google Cloud credentials
        client = genai.Client(api_key=api_key, http_options={'api_version': 'v1'})
        print("✅ Gemini AI Client initialized on v1 API.")
    except Exception as e:
        print(f"❌ Initialization Error: {e}")
        client = None

async def get_ai_response(username: str, context_history: list[dict]) -> str:
    if not client:
        return "ERROR: AI service not available."

    user_query = context_history[-1]["content"] if context_history else "Hello"

    try:
        # We run this in a thread to prevent blocking
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=MODEL_NAME,
            contents=user_query
        )
        
        return response.text
        
    except Exception as e:
        # If it still fails, we'll see the exact reason
        print(f"❌ API Failure: {str(e)}")
        return f"AI Error: {str(e)}"