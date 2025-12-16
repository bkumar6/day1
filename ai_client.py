# ai_client.py

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables from .env file
load_dotenv() 

# Initialize the Gemini Client using the environment variable
# The client automatically looks for the GEMINI_API_KEY environment variable.
try:
    client = genai.Client()
    # Define the model to use
    MODEL_NAME = "gemini-2.5-flash"
    print("AI Client initialized successfully.")
except Exception as e:
    print(f"Error initializing AI client: {e}")
    client = None
    MODEL_NAME = None

def get_ai_response(username: str, context_history: list[dict]) -> str:
    """
    Takes the user's history and calls the external AI API.
    
    Args:
        username: The user making the request.
        context_history: A list of dicts representing the chat history.
    
    Returns:
        The text response from the AI.
    """
    if not client:
        return "ERROR: AI service not available due to initialization failure."

    # 1. Format Context for the Gemini API
    # The API expects roles 'user' and 'model' (not 'ai') and a specific content format.
    formatted_content = []
    for message in context_history:
        # Map your internal roles to the required API roles
        role = 'model' if message['role'] == 'ai' else 'user'
        
        formatted_content.append(types.Content(
            role=role, 
            parts=[types.Part.from_text(message['content'])]
        ))

    # 2. Call the API with the full conversation history
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=formatted_content,
        )
        
        # 3. Return the generated text
        return response.text
        
    except Exception as e:
        print(f"Error calling AI API for {username}: {e}")
        return "Internal AI processing error."