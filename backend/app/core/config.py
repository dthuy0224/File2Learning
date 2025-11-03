from pydantic import field_validator
from pydantic_settings import BaseSettings
from typing import List, Optional
from pathlib import Path
import os
from dotenv import load_dotenv, find_dotenv

# Single-source env loading: prefer OS env (e.g., Docker). If running locally,
# load the project root .env by searching upwards from CWD.
_root_env = find_dotenv(filename=".env", usecwd=True)
if _root_env:
    load_dotenv(_root_env)

class Settings(BaseSettings):
    # Basic app config
    PROJECT_NAME: str = "File2Learning"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Database
    DATABASE_URL: str = "postgresql+psycopg2://app_user:app_password@postgres:5432/file2learning"
    POSTGRESQL_DATABASE_URL: Optional[str] = None  # can override in prod
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Log db config (optional)
        print("📊 Database Configuration:")
        print(f"   URL: {self.DATABASE_URL}")
        print(f"   Type: PostgreSQL")
        print(f"   Database: file2learning")
    
    # CORS / Hosts
    ALLOWED_HOSTS: List[str] = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]


    # Frontend URL 
    FRONTEND_URL: str = "http://localhost:3000"
    
    # AI/OpenAI
    OPENAI_API_KEY: Optional[str] = None
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # File uploads
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    UPLOAD_FOLDER: str = "uploads"
    ALLOWED_FILE_EXTENSIONS: List[str] = [".pdf", ".docx", ".txt", ".doc"]
    
    # Email
    SMTP_SERVER: Optional[str] = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    SMTP_FROM_EMAIL: Optional[str] = os.getenv("SMTP_FROM_EMAIL")


    # OAuth providers
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = None
    MICROSOFT_CLIENT_ID: Optional[str] = None
    MICROSOFT_CLIENT_SECRET: Optional[str] = None
    MICROSOFT_REDIRECT_URI: Optional[str] = None
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None
    GITHUB_REDIRECT_URI: Optional[str] = None

    # OAuth base URL
    OAUTH_BASE_URL: str = "http://localhost:8000"
    
    # Validators
    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str]) -> str:
        if v and v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+psycopg2://", 1)
        return v or "postgresql+psycopg2://app_user:app_password@postgres:5432/file2learning"
    
    @field_validator("UPLOAD_FOLDER", mode="before")
    @classmethod
    def create_upload_folder(cls, v: str) -> str:
        upload_path = Path(v)
        upload_path.mkdir(exist_ok=True)
        return str(upload_path)

    model_config = {
        "case_sensitive": True,
        "extra": "allow"
    }

    def get_database_info(self) -> dict:
        return {
            "type": "PostgreSQL",
            "database": "file2learning",
            "url": self.DATABASE_URL,
            "host": "postgres",
            "connection_status": "Connected"
        }


settings = Settings()
