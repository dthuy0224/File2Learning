from pydantic import field_validator
from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    # Basic app config
    PROJECT_NAME: str = "File2Learning"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Database Configuration - PostgreSQL Setup
    # ===========================================
    # Default: PostgreSQL with dedicated user for production-ready setup
    # User: app_user (created specifically for this application)
    # Password: app_password (development only - change in production)
    # Database: file2learning (created in PostgreSQL container)
    DATABASE_URL: str = "postgresql+psycopg2://app_user:app_password@postgres:5432/file2learning"

    # SQLite fallback for development (if PostgreSQL is not available)
    SQLITE_DATABASE_URL: str = "sqlite:///./app.db"

    # PostgreSQL configuration - can be overridden via environment variable
    POSTGRESQL_DATABASE_URL: Optional[str] = None  # PostgreSQL URL for production

    # Force PostgreSQL configuration (ignore environment variables)
    # Logic: 1. Always try PostgreSQL connection with app_user
    #        2. Fallback to SQLite only if PostgreSQL is unavailable
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Force PostgreSQL connection (ignore environment variables)
        # Always try to use PostgreSQL with app_user first
        try:
            import psycopg2
            print("🔍 Testing PostgreSQL connection with app_user...")
            # Try localhost first (for host machine), then postgres (for Docker)
            for host in ["localhost", "postgres"]:
                # Try app_user first, then postgres user as fallback
                for user, password in [("app_user", "app_password"), ("postgres", "abc123")]:
                    try:
                        test_conn = psycopg2.connect(
                            host=host,
                            port=5432,
                            database="file2learning",
                            user=user,
                            password=password
                        )
                        print(f"✅ PostgreSQL connection successful via {host} with user {user}!")
                        # Store the working credentials
                        self._working_user = user
                        self._working_password = password
                        break
                    except Exception as host_error:
                        print(f"⚠️  Cannot connect via {host} with user {user}: {host_error}")
                        continue
                else:
                    continue  # Try next host
                break  # Found working connection
            else:
                raise Exception("Cannot connect to PostgreSQL via localhost or postgres")
            test_conn.close()
            print("✅ PostgreSQL connection successful! Using PostgreSQL.")
            # Use the working credentials
            self.DATABASE_URL = f"postgresql+psycopg2://{self._working_user}:{self._working_password}@localhost:5432/file2learning"
        except Exception as e:
            # PostgreSQL not available, fallback to SQLite
            print(f"⚠️  PostgreSQL not available ({e}), falling back to SQLite")
            print("🔧 Using SQLite for development fallback")
            self.DATABASE_URL = self.DATABASE_URL

        # Log final database configuration
        print(f"📊 Final Database Configuration:")
        print(f"   URL: {self.DATABASE_URL}")
        print(f"   Type: {'PostgreSQL' if 'postgresql' in self.DATABASE_URL else 'SQLite'}")
        print(f"   Database: {'file2learning' if 'postgresql' in self.DATABASE_URL else 'app.db'}")
    
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

    # OAuth providers
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    MICROSOFT_CLIENT_ID: Optional[str] = None
    MICROSOFT_CLIENT_SECRET: Optional[str] = None
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None

    # OAuth base URL for callbacks
    OAUTH_BASE_URL: str = "http://localhost:8000"
    
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
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "allow"
    }

    def get_database_info(self) -> dict:
        """Get database configuration information"""
        is_postgresql = "postgresql" in self.DATABASE_URL
        return {
            "type": "PostgreSQL" if is_postgresql else "SQLite",
            "database": "file2learning" if is_postgresql else "app.db",
            "url": self.DATABASE_URL,
            "host": "postgres" if is_postgresql else "local",
            "connection_status": "Connected" if is_postgresql else "Fallback mode"
        }


settings = Settings()
