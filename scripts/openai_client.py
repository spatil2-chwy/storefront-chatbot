from openai import OpenAI
from dotenv import load_dotenv
import os
from typing import Optional

# Load environment variables
load_dotenv()

# Global OpenAI client instance
_openai_client: Optional[OpenAI] = None

def get_openai_client() -> OpenAI:
    """
    Get or create the OpenAI client instance.
    This ensures the API key is loaded only once and the client is reused.
    
    Returns:
        OpenAI: The OpenAI client instance
        
    Raises:
        ValueError: If OPENAI_API_KEY is not set in environment variables
    """
    global _openai_client
    
    if _openai_client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set. Please check your .env file.")
        
        _openai_client = OpenAI(api_key=api_key)
    
    return _openai_client

def reset_openai_client():
    """
    Reset the OpenAI client instance. Useful for testing or when you need to 
    reinitialize the client with different settings.
    """
    global _openai_client
    _openai_client = None 