#!/usr/bin/env python3
"""
Database test script for running from HOST (Windows)
This script detects if connecting to Docker container or local PostgreSQL
"""
import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

import os
from sqlalchemy import text, create_engine
from sqlalchemy.exc import OperationalError
from app.core.config import settings

def detect_postgresql_source():
    """Detect which PostgreSQL we're connecting to"""
    print("\n[INFO] Detecting PostgreSQL source...")
    
    # Try to connect and get version
    try:
        # Use postgres user to test connection
        test_url = settings.DATABASE_URL.replace("app_user:app_password", "postgres:abc123")
        if "@postgres:" in test_url:
            test_url = test_url.replace("@postgres:", "@localhost:")
        
        engine = create_engine(test_url.replace("file2learning", "postgres"), pool_pre_ping=True)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"   PostgreSQL version: {version[:80]}...")
            
            if "Alpine" in version or "linux" in version.lower():
                print("   [DETECTED] Docker container (PostgreSQL 15)")
                return "docker"
            elif "Windows" in version or "msv" in version.lower():
                print("   [DETECTED] Local Windows PostgreSQL (PostgreSQL 17)")
                return "windows"
    except Exception as e:
        print(f"   [WARN] Could not detect: {e}")
    
    return "unknown"

def main():
    """Main test function"""
    print("=" * 60)
    print("Database Test from HOST (Windows)")
    print("=" * 60)
    
    source = detect_postgresql_source()
    
    if source == "windows":
        print("\n[WARNING] You are connecting to PostgreSQL on Windows, not Docker container!")
        print("\nSolutions:")
        print("  1. Stop Windows PostgreSQL service:")
        print("     net stop postgresql-x64-17")
        print("  2. Or change Docker container port in docker-compose.yml")
        print("  3. Or run test from inside container:")
        print("     docker-compose exec backend python scripts/test_database.py")
        print("\n[INFO] To test Docker container database, use:")
        print("   docker-compose exec backend python scripts/test_database.py")
        return 1
    elif source == "docker":
        print("\n[OK] Connecting to Docker container PostgreSQL")
        # Run normal test
        from scripts.test_database import main as test_main
        return test_main()
    else:
        print("\n[ERROR] Could not connect to PostgreSQL")
        return 1

if __name__ == "__main__":
    exit(main())

