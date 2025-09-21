from pydantic import field_validator
from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    # Basic app config
    PROJECT_NAME: str = "AI Learning Material Generator"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Database
    DATABASE_URL: str = "sqlite:///./app.db"  # Default SQLite for development
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # AI/OpenAI
    OPENAI_API_KEY: Optional[str] = None
    
    # Redis (for caching and sessions)
    REDIS_URL: str = "redis://localhost:6379"
    
    # File uploads
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    UPLOAD_FOLDER: str = "uploads"
    ALLOWED_FILE_EXTENSIONS: List[str] = [".pdf", ".docx", ".txt", ".doc"]
    
    # Email (for notifications)
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str]) -> str:
        if v and v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+psycopg2://", 1)
        return v or "sqlite:///./app.db"
    
    @field_validator("UPLOAD_FOLDER", mode="before")
    @classmethod
    def create_upload_folder(cls, v: str) -> str:
        upload_path = Path(v)
        upload_path.mkdir(exist_ok=True)
        return str(upload_path)

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "allow"
    }


settings = Settings()
