# ai_client.py

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables from .env file (for local development)
load_dotenv() 

# --- AI CLIENT INITIALIZATION ---
# The client will automatically use the GEMINI_API_KEY environment variable.
try:
    # Ensure the client is initialized when the script starts
    client = genai.Client()
    # Define the model to use
    MODEL_NAME = "gemini-2.5-flash"
    print("AI Client initialized successfully.")
except Exception as e:
    # This error should now be fixed on Render, but we keep the handler
    print(f"Error initializing AI client: {e}")
    client = None
    MODEL_NAME = None

def get_ai_response(username: str, context_history: list[dict]) -> str:
    """
    Synchronous function that calls the external AI API using the full context.
    This function runs in a separate thread via asyncio.to_thread.
    """
    if not client:
        return "ERROR: AI service not available due to initialization failure."

    # 1. Format Context for the Gemini API
    formatted_content = []
    for message in context_history:
        # Map your internal roles ('user', 'ai') to the required API roles ('user', 'model')
        role = 'model' if message['role'] == 'ai' else 'user'
        
        formatted_content.append(types.Content(
            role=role, 
            parts=[types.Part.from_text(message['content'])]
        ))

    # 2. Call the API with the full conversation history
    try:
        # NOTE: This is a synchronous (blocking) call.
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=formatted_content,
        )
        
        # 3. Return the generated text
        return response.text
        
    except Exception as e:
        print(f"Error calling AI API for {username}: {e}")
        # Return a simple error to the user if the API call itself fails
        return "Internal AI processing error (API call failed)."