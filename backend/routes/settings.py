"""Settings and user profile routes."""
import os
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.database.models import User
from backend.models.schemas import UserCreate, UserResponse, UserUpdate, SettingsUpdate, SettingsResponse
from backend.config import APP_DATA_DIR
from backend.services.ai_provider import get_available_providers

router = APIRouter(prefix="/settings", tags=["settings"])

SETTINGS_FILE = os.path.join(str(APP_DATA_DIR), "settings.json")


def _load_settings() -> dict:
    """Load settings from file."""
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    return {"preferred_provider": "openai", "theme": "dark"}


def _save_settings(settings: dict):
    """Save settings to file."""
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=2)


@router.get("", response_model=SettingsResponse)
def get_settings():
    """Get current settings."""
    settings = _load_settings()
    
    # Check Ollama availability
    ollama_available = False
    try:
        import httpx
        ollama_url = settings.get("ollama_base_url", os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
        resp = httpx.get(f"{ollama_url}/api/tags", timeout=2.0)
        ollama_available = resp.status_code == 200
    except Exception:
        pass
    
    return SettingsResponse(
        has_openai_key=bool(os.getenv("OPENAI_API_KEY") or settings.get("openai_api_key")),
        has_gemini_key=bool(os.getenv("GEMINI_API_KEY") or settings.get("gemini_api_key")),
        preferred_provider=settings.get("preferred_provider", "openai"),
        theme=settings.get("theme", "dark"),
        ollama_available=ollama_available,
        ollama_model=settings.get("ollama_model", os.getenv("OLLAMA_MODEL", "llama3.1"))
    )


@router.put("")
def update_settings(update: SettingsUpdate):
    """Update settings."""
    settings = _load_settings()

    if update.openai_api_key is not None:
        settings["openai_api_key"] = update.openai_api_key
        os.environ["OPENAI_API_KEY"] = update.openai_api_key

    if update.gemini_api_key is not None:
        settings["gemini_api_key"] = update.gemini_api_key
        os.environ["GEMINI_API_KEY"] = update.gemini_api_key

    if update.preferred_provider is not None:
        settings["preferred_provider"] = update.preferred_provider
        os.environ["AI_PROVIDER"] = update.preferred_provider

    if update.theme is not None:
        settings["theme"] = update.theme

    # Ollama settings
    if hasattr(update, 'ollama_base_url') and update.ollama_base_url is not None:
        settings["ollama_base_url"] = update.ollama_base_url
        os.environ["OLLAMA_BASE_URL"] = update.ollama_base_url
    
    if hasattr(update, 'ollama_model') and update.ollama_model is not None:
        settings["ollama_model"] = update.ollama_model
        os.environ["OLLAMA_MODEL"] = update.ollama_model

    _save_settings(settings)
    return {"message": "Settings updated successfully"}


@router.get("/providers")
def get_providers():
    """Get available AI providers and their status."""
    return {"providers": get_available_providers()}


@router.post("/providers/test")
def test_provider(data: dict):
    """Test connection to a specific provider."""
    provider = data.get("provider")
    
    if provider == "ollama":
        import httpx
        url = data.get("url", os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
        try:
            response = httpx.get(f"{url}/api/tags", timeout=5.0)
            if response.status_code == 200:
                models = [m["name"] for m in response.json().get("models", [])]
                return {"success": True, "message": f"Connected! {len(models)} models available.", "models": models}
        except Exception as e:
            return {"success": False, "message": f"Cannot connect to Ollama at {url}: {str(e)}"}
    
    elif provider == "openai":
        key = data.get("api_key", os.getenv("OPENAI_API_KEY", ""))
        if not key:
            return {"success": False, "message": "No API key provided"}
        try:
            from openai import OpenAI
            client = OpenAI(api_key=key)
            client.models.list()
            return {"success": True, "message": "OpenAI connection successful!"}
        except Exception as e:
            return {"success": False, "message": f"OpenAI error: {str(e)}"}
    
    elif provider == "gemini":
        key = data.get("api_key", os.getenv("GEMINI_API_KEY", ""))
        if not key:
            return {"success": False, "message": "No API key provided"}
        try:
            import google.generativeai as genai
            genai.configure(api_key=key)
            genai.list_models()
            return {"success": True, "message": "Gemini connection successful!"}
        except Exception as e:
            return {"success": False, "message": f"Gemini error: {str(e)}"}
    
    return {"success": False, "message": "Unknown provider"}


# ---- User Profile Routes ----
@router.get("/profile", response_model=UserResponse)
def get_profile(db: Session = Depends(get_db)):
    """Get or create user profile."""
    user = db.query(User).first()
    if not user:
        user = User(name="Student", learning_style="balanced", preferred_provider="openai")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@router.put("/profile", response_model=UserResponse)
def update_profile(update: UserUpdate, db: Session = Depends(get_db)):
    """Update user profile."""
    user = db.query(User).first()
    if not user:
        user = User(name="Student")
        db.add(user)
        db.commit()
        db.refresh(user)

    update_data = update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user
