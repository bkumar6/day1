# ai_client.py
import os
import asyncio
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = None
# For version 0.6.0, try using 'gemini-1.5-flash' or 'models/gemini-1.5-flash'
MODEL_NAME = "models/gemini-1.5-flash" 

async def initialize_ai_client():
    global client
    print("Attempting to initialize AI Client...")
    try:
        # Check for both possible naming conventions
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            print("❌ Error: No API Key found in Environment Variables.")
            return
            
        client = genai.Client(api_key=api_key)
        print("✅ AI Client initialized successfully.")
    except Exception as e:
        print(f"❌ Error during initialization: {e}")
        client = None

async def get_ai_response(username: str, context_history: list[dict]) -> str:
    if not client:
        return "ERROR: AI service not available. Initialization failed."

    # Simplify contents for 0.6.0 compatibility
    user_query = context_history[-1]["content"] if context_history else ""

    try:
        # Execute the call in a thread to remain non-blocking
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=MODEL_NAME,
            contents=user_query
        )
        return response.text
    except Exception as e:
        # THIS PRINT IS CRITICAL: Check your Render logs for this output!
        print(f"❌ Gemini API Call Failed for {username}: {str(e)}")
        return f"AI Error: {str(e)}"