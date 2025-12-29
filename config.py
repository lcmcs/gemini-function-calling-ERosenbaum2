"""
Configuration management for Gemini Function Calling demo.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Gemini API Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found. Please set it in your .env file or environment variables.\n"
        "Get your API key from: https://aistudio.google.com/app/apikey"
    )

# Minyan Finder API Configuration
MINYAN_API_BASE_URL = os.getenv('MINYAN_API_BASE_URL', 'http://localhost:5000')

# Gemini Model Configuration
# Try gemini-1.5-pro if gemini-1.5-flash doesn't work
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-1.5-pro')

def get_config():
    """Get configuration dictionary."""
    return {
        'gemini_api_key': GEMINI_API_KEY,
        'minyan_api_base_url': MINYAN_API_BASE_URL,
        'gemini_model': GEMINI_MODEL
    }

