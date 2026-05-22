"""Settings and user profile routes."""
import os
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.database.models import User
from backend.models.schemas import UserCreate, UserResponse, UserUpdate, SettingsUpdate, SettingsResponse
from backend.config import APP_DATA_DIR

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
    return SettingsResponse(
        has_openai_key=bool(os.getenv("OPENAI_API_KEY") or settings.get("openai_api_key")),
        has_gemini_key=bool(os.getenv("GEMINI_API_KEY") or settings.get("gemini_api_key")),
        preferred_provider=settings.get("preferred_provider", "openai"),
        theme=settings.get("theme", "dark")
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

    _save_settings(settings)
    return {"message": "Settings updated successfully"}


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
