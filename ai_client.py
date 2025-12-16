# ai_client.py

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai import AsyncClient 
import asyncio 

load_dotenv() 

# Global variables for the client
client = None
MODEL_NAME = "gemini-2.5-flash"

# --- ASYNC INITIALIZATION FUNCTION ---
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

# --- ASYNC RESPONSE FUNCTION ---
async def get_ai_response(username: str, context_history: list[dict]) -> str:
    """
    Asynchronous function to call the external AI API using the full context.
    """
    # This check now runs after the startup hook should have set the client
    if not client:
        return "ERROR: AI service not available. Initialization failed."

    # 1. Format Context 
    formatted_content = []
    for message in context_history:
        # Map internal roles to API roles
        role = 'model' if message['role'] == 'ai' else 'user'
        formatted_content.append(types.Content(
            role=role, 
            parts=[types.Part.from_text(message['content'])]
        ))

    # 2. Call the API with the full conversation history
    try:
        # This is the ASYNCHRONOUS call and MUST be awaited.
        response = await client.models.generate_content(
            model=MODEL_NAME,
            contents=formatted_content,
        )
        
        return response.text
        
    except Exception as e:
        print(f"Error calling AI API for {username}: {e}")
        return "Internal AI processing error (API call failed)."