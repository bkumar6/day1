import os
import asyncio
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# Global variables
client = None
MODEL_NAME = "gemini-2.5-flash"

def initialize_ai_client():
    """
    Initializes the global Gemini client.
    This is SYNC because google-genai does not provide an async client.
    """
    global client
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY not found in environment variables")

        client = genai.Client(api_key=api_key)
        print("✅ Gemini client initialized successfully")

    except Exception as e:
        print(f"❌ Error initializing Gemini client: {e}")
        client = None


def _sync_generate_content(formatted_content):
    """
    Internal synchronous Gemini call.
    """
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=formatted_content,
    )
    return response.text


async def get_ai_response(username: str, context_history: list[dict]) -> str:
    """
    Async-safe Gemini call using thread offloading.
    """
    if not client:
        return "ERROR: AI service not available. Initialization failed."

    formatted_content = []

    for message in context_history:
        role = "model" if message["role"] == "ai" else "user"
        formatted_content.append(
            types.Content(
                role=role,
                parts=[types.Part.from_text(message["content"])]
            )
        )

    try:
        # Run blocking Gemini call in a thread
        response_text = await asyncio.to_thread(
            _sync_generate_content,
            formatted_content
        )
        return response_text

    except Exception as e:
        print(f"❌ Gemini API error for {username}: {e}")
        return "Internal AI processing error."
