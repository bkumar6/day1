# ai_client.py
import os
import asyncio
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# Global variables
client = None
MODEL_NAME = "gemini-1.5-flash"

async def initialize_ai_client():
    """Initializes the AI client during server startup."""
    global client
    print("Attempting to initialize AI Client...")
    try:
        # Use the standard Client which is stable in version 0.6.0
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ Error: GEMINI_API_KEY not found in environment.")
            return
            
        client = genai.Client(api_key=api_key)
        print("✅ AI Client initialized successfully.")
    except Exception as e:
        print(f"❌ Error initializing AI Client: {e}")
        client = None

async def get_ai_response(username: str, context_history: list[dict]) -> str:
    """Calls the AI API using a thread-safe wrapper to prevent blocking."""
    if not client:
        return "ERROR: AI service not available. Initialization failed."

    # 1. Format Context
    formatted_content = []
    for message in context_history:
        role = 'model' if message['role'] == 'ai' else 'user'
        formatted_content.append(types.Content(
            role=role,
            parts=[types.Part.from_text(message['content'])]
        ))

    # 2. Call the API using a Thread Pool to keep the server responsive
    try:
        # asyncio.to_thread runs the synchronous call in a separate thread
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=MODEL_NAME,
            contents=formatted_content
        )
        return response.text
    except Exception as e:
        print(f"❌ Error calling AI API for {username}: {e}")
        return "Internal AI processing error (API call failed)."