#!/usr/bin/env python
"""Wait for database to be ready before running migrations"""
import time
import sys
from sqlalchemy import create_engine, text


def wait_for_db(max_retries=30, delay=1):
    """Kiểm tra database sẵn sàng"""
    db_url = "postgresql://app_user:app_password@postgres:5432/file2learning"

    for attempt in range(max_retries):
        try:
            engine = create_engine(db_url)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✅ Database is ready!")
            return True
        except Exception as e:
            attempt_num = attempt + 1
            print(
                f"⏳ Waiting for database ({attempt_num}/{max_retries})... {str(e)[:50]}"
            )
            time.sleep(delay)

    print("❌ Database failed to become ready")
    return False


if __name__ == "__main__":
    if not wait_for_db():
        sys.exit(1)
