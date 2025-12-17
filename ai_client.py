# ai_client.py
import os
import asyncio
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = None
# CHANGE THIS LINE: This specific ID is the most stable for v1beta calls
MODEL_NAME = "gemini-1.5-flash" 

async def initialize_ai_client():
    global client
    print("Attempting to initialize AI Client...")
    try:
        # Prioritize GEMINI_API_KEY from Render Environment Variables
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
        return "ERROR: AI service not available."

    # Using a flat string for the most basic compatibility with v0.6.0
    user_query = context_history[-1]["content"] if context_history else ""

    try:
        # Running in a thread to keep the WebSocket responsive
        # We pass the model name exactly as requested by the v1beta endpoint
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=MODEL_NAME,
            contents=user_query
        )
        
        if hasattr(response, 'text'):
            return response.text
        return str(response)
        
    except Exception as e:
        print(f"❌ Gemini API Call Failed: {str(e)}")
        # If gemini-1.5-flash fails again, we try the fallback 'gemini-pro'
        return f"AI Error: {str(e)}"