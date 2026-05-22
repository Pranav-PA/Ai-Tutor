"""Configuration management for AI Semester Companion."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
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
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:38173",
    "http://127.0.0.1:38173",
]
