"""Configuration management for AI Semester Companion."""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Base paths - support bundled mode (PyInstaller) and desktop app
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent.parent

# Allow APP_DATA_DIR override from environment (used by desktop app)
_app_data_env = os.getenv("APP_DATA_DIR")
if _app_data_env:
    APP_DATA_DIR = Path(_app_data_env)
else:
    APP_DATA_DIR = BASE_DIR / "app-data"

UPLOADS_DIR = APP_DATA_DIR / "uploads"
VECTORS_DIR = APP_DATA_DIR / "vectors"
GENERATED_DIR = APP_DATA_DIR / "generated"
PROGRESS_DIR = APP_DATA_DIR / "progress"
CACHE_DIR = APP_DATA_DIR / "cache"

# Create directories
for dir_path in [APP_DATA_DIR, UPLOADS_DIR, VECTORS_DIR, GENERATED_DIR, PROGRESS_DIR, CACHE_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# AI Settings
DEFAULT_PROVIDER = os.getenv("DEFAULT_PROVIDER", "openai")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")

# Temperature settings
TEACHING_TEMPERATURE = 0.3
QUIZ_TEMPERATURE = 0.7
GENERAL_TEMPERATURE = 0.5

# Document processing
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".pptx", ".txt", ".png", ".jpg", ".jpeg"}

# Vector DB
CHROMA_PERSIST_DIR = str(VECTORS_DIR)

# Server
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "18080"))
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:38173",
    "http://127.0.0.1:38173",
    "http://localhost:18080",
    "http://127.0.0.1:18080",
    "file://",  # Electron file:// protocol
    "app://.",  # Electron custom protocol
]

# Allow all origins in desktop mode for flexibility
if os.getenv("DESKTOP_MODE") == "true":
    CORS_ORIGINS = ["*"]
