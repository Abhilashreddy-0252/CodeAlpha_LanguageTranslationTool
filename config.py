import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory
BASE_DIR = Path(__file__).resolve().parent

# Load .env file
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# Google Cloud Translate API Key
GOOGLE_TRANSLATE_API_KEY = os.getenv("GOOGLE_TRANSLATE_API_KEY", "").strip()

# Google Cloud Translate v2 API Endpoint
GOOGLE_TRANSLATE_ENDPOINT = "https://translation.googleapis.com/language/translate/v2"

# Application Metadata & UI Settings
APP_NAME = "AI Language Translation Tool"
APP_SUBTITLE = "Smart Multi-Language & Speech Dashboard"
APP_VERSION = "1.0.0"
WINDOW_SIZE = "980x720"
MIN_WINDOW_SIZE = (850, 600)

# Path to icon file
ICON_PATH = BASE_DIR / "assets" / "icon.ico"

# Maximum character limit for translation input
MAX_CHAR_LIMIT = 5000

def reload_api_key():
    """Reload API key from .env file at runtime if updated."""
    load_dotenv(dotenv_path=ENV_PATH, override=True)
    return os.getenv("GOOGLE_TRANSLATE_API_KEY", "").strip()
