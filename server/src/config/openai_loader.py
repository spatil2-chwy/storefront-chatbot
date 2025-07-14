from openai import OpenAI
from dotenv import load_dotenv
import os
from typing import Optional

# Load environment variables
load_dotenv()

# Global OpenAI client instance
_openai_client: Optional[OpenAI] = None

def get_openai_client() -> OpenAI:
    global _openai_client
    
    if _openai_client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set. Please check your .env file.")
        
        _openai_client = OpenAI(api_key=api_key)
    
    return _openai_client

def reset_openai_client():
    global _openai_client
    _openai_client = None 