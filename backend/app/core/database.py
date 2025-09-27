from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create SQLAlchemy engine
def create_engine_with_settings():
    """Create database engine with PostgreSQL settings"""

    # PostgreSQL specific settings
    engine_settings = {
        "pool_size": 20,  # Number of persistent connections
        "max_overflow": 30,  # Additional connections beyond pool_size
        "pool_pre_ping": True,  # Verify connections before use
        "pool_recycle": 3600,  # Recycle connections after 1 hour
        "echo": False,  # Set to True for SQL query logging in development
    }

    return create_engine(settings.DATABASE_URL, **engine_settings)

engine = create_engine_with_settings()

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
