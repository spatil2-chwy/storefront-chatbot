from functools import lru_cache
import os
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables once at import time
load_dotenv()

@lru_cache(maxsize=None)
def get_env_var(key: str, default: Optional[str] = None, *, required: bool = False) -> str:
    """Retrieve an environment variable with optional default / required flag.

    Args:
        key: Name of the environment variable.
        default: Value if the variable is not set.
        required: If True, raises ValueError when the variable is missing.

    Returns:
        The environment variable value (or default).
    """
    value = os.getenv(key, default)
    if required and value is None:
        raise ValueError(f"{key} is not set. Please check your environment or .env file.")
    return value  # type: ignore


@lru_cache(maxsize=None)
def get_openai_client(api_key_env: str = "OPENAI_API_KEY_2") -> OpenAI:
    """Return a cached OpenAI client initialized with the API key from env."""
    api_key = get_env_var(api_key_env, required=True)
    return OpenAI(api_key=api_key) 