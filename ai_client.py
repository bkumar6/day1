
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai import AsyncClient 
import asyncio # <-- Need this for the async initialization

load_dotenv() 

# Global variables for the client
client = None
MODEL_NAME = "gemini-2.5-flash"

async def initialize_ai_client():
    """Initializes the global AI client in an async context."""
    global client
    print("Attempting to initialize AI AsyncClient...")
    try:
        # Initialize the ASYNCHRONOUS client
        client = AsyncClient() 
        print("AI AsyncClient initialized successfully.")
    except Exception as e:
        print(f"Error initializing AI AsyncClient: {e}")
        client = None

async def get_ai_response(username: str, context_history: list[dict]) -> str:
    """
    Asynchronous function to call the external AI API using the full context.
    """
    if not client:
        return "ERROR: AI service not available. Initialization failed."

    formatted_content = []
    for message in context_history:
        role = 'model' if message['role'] == 'ai' else 'user'
        formatted_content.append(types.Content(
            role=role, 
            parts=[types.Part.from_text(message['content'])]
        ))

    try:
        # This MUST be awaited.
        response = await client.models.generate_content(
            model=MODEL_NAME,
            contents=formatted_content,
        )
        
        return response.text
        
    except Exception as e:
        print(f"Error calling AI API for {username}: {e}")
        return "Internal AI processing error (API call failed)."