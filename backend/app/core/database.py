from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings


# 1. Tạo Engine
def create_engine_with_settings():
    engine_settings = {
        "pool_size": 20,
        "max_overflow": 30,
        "pool_pre_ping": True,
        "pool_recycle": 3600,
        "echo": False,
    }
    return create_engine(settings.DATABASE_URL, **engine_settings)


engine = create_engine_with_settings()

# 2. Tạo Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Tạo Base (Các model sẽ kế thừa từ đây)
Base = declarative_base()


# 4. Hàm Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
