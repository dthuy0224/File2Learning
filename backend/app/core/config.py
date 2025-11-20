from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict, EnvSettingsSource
from typing import List, Optional, Union, Any, Dict
from pathlib import Path
import os
from dotenv import load_dotenv, find_dotenv

# Single-source env loading: prefer OS env (e.g., Docker). If running locally,
# load the project root .env by searching upwards from CWD.
_root_env = find_dotenv(filename=".env", usecwd=True)
if _root_env:
    load_dotenv(_root_env)


class CustomEnvSettingsSource(EnvSettingsSource):
    """Custom env source that handles comma-separated strings for List fields"""

    def __call__(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        for field_name, field_info in self.settings_cls.model_fields.items():
            env_val: str | None = os.getenv(field_name, None)
            if env_val is not None:
                # For List fields, don't try to parse as JSON if it's comma-separated
                # Check if field type is List
                field_type = field_info.annotation
                if field_type:
                    # Handle typing.List and list
                    try:
                        import typing

                        if hasattr(typing, "get_origin"):
                            origin = typing.get_origin(field_type)
                        else:
                            origin = getattr(field_type, "__origin__", None)

                        if origin is list or origin is List:
                            # If it's a list field and value doesn't look like JSON, keep as string
                            # The validator will handle the parsing
                            if not (
                                env_val.strip().startswith("[")
                                and env_val.strip().endswith("]")
                            ):
                                d[field_name] = env_val
                                continue
                    except Exception:
                        pass
                d[field_name] = env_val
        return d


class Settings(BaseSettings):
    # Basic app config
    PROJECT_NAME: str = "File2Learning"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # Database
    # Ưu tiên dùng biến môi trường, fallback về giá trị mặc định
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://app_user:app_password@postgres:5432/file2learning",
    )
    POSTGRESQL_DATABASE_URL: Optional[str] = None  # can override in prod

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Log db config (optional)
        # print("Database Configuration:")
        # print(f"   URL: {self.DATABASE_URL}")

    # CORS / Hosts
    ALLOWED_HOSTS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # Config CORS cho Backend
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # Frontend URL
    FRONTEND_URL: str = "http://localhost:3000"

    # AI/OpenAI
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # File uploads
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    UPLOAD_FOLDER: str = "uploads"
    ALLOWED_FILE_EXTENSIONS: List[str] = [".pdf", ".docx", ".txt", ".doc", ".docs"]

    # --- Email Configuration ---
    # Đổi tên SMTP_SERVER -> SMTP_HOST để khớp với file email.py
    SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 465))  # Mặc định 465 cho SSL
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
        return (
            v
            or "postgresql+psycopg2://app_user:app_password@postgres:5432/file2learning"
        )

    @field_validator("UPLOAD_FOLDER", mode="before")
    @classmethod
    def create_upload_folder(cls, v: str) -> str:
        upload_path = Path(v)
        upload_path.mkdir(exist_ok=True)
        return str(upload_path)

    @field_validator("ALLOWED_HOSTS", "BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_hosts(cls, v: Union[str, List[str], None]) -> List[str]:
        """Parse list from comma-separated string or list"""
        if v is None:
            return []
        if isinstance(v, str):
            # Handle empty string
            if not v.strip():
                return []
            # Split by comma and strip whitespace
            return [host.strip() for host in v.split(",") if host.strip()]
        elif isinstance(v, list):
            return v
        return []

    @field_validator("ALLOWED_FILE_EXTENSIONS", mode="before")
    @classmethod
    def parse_allowed_extensions(cls, v: Union[str, List[str], None]) -> List[str]:
        """Parse ALLOWED_FILE_EXTENSIONS from comma-separated string or list"""
        if v is None:
            return [".pdf", ".docx", ".txt", ".doc", ".docs"]
        if isinstance(v, str):
            # Handle empty string
            if not v.strip():
                return [".pdf", ".docx", ".txt", ".doc", ".docs"]
            # Split by comma and strip whitespace
            return [ext.strip() for ext in v.split(",") if ext.strip()]
        elif isinstance(v, list):
            return v
        return [".pdf", ".docx", ".txt", ".doc", ".docs"]

    model_config = SettingsConfigDict(
        case_sensitive=True, extra="allow", env_parse_none_str="", env_ignore_empty=True
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        # Use custom env source that handles comma-separated strings
        return (
            init_settings,
            CustomEnvSettingsSource(settings_cls),
            dotenv_settings,
            file_secret_settings,
        )

    def get_database_info(self) -> dict:
        return {
            "type": "PostgreSQL",
            "database": "file2learning",
            "url": self.DATABASE_URL,
            "host": "postgres",
            "connection_status": "Connected",
        }


settings = Settings()
