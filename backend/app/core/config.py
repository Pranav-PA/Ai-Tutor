from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # Application
    app_name: str = "AI Learning Engine"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/learningagent"
    
    # Redis
    redis_url: str = "redis://redis:6379/0"

    # Auth
    secret_key: str = "change-this-secret-key-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4"

    # Vector DB
    faiss_index_path: str = "./data/faiss_index"
    embedding_model: str = "all-MiniLM-L6-v2"

    # File Storage
    upload_dir: str = "./data/uploads"
    max_upload_size: int = 52428800  # 50MB

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
