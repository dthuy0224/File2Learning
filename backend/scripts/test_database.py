#!/usr/bin/env python3
"""
Database connection and configuration test script
Tests database connectivity, user permissions, and extensions
"""
import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import text, inspect
from sqlalchemy.exc import OperationalError, ProgrammingError
from app.core.database import SessionLocal, engine
from app.core.config import settings


def test_database_connection():
    """Test basic database connection"""
    print("\n[TEST] Testing database connection...")
    try:
        db = SessionLocal()
        result = db.execute(text("SELECT 1 as test")).fetchone()
        db.close()
        if result and result[0] == 1:
            print("[OK] Database connection successful!")
            return True
        else:
            print("[FAIL] Database connection returned unexpected result")
            return False
    except OperationalError as e:
        print(f"[FAIL] Database connection failed: {e}")
        return False
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False


def test_database_name():
    """Test if connected to correct database"""
    print("\n[TEST] Testing database name...")
    try:
        db = SessionLocal()
        result = db.execute(text("SELECT current_database()")).fetchone()
        db.close()
        db_name = result[0] if result else None
        if db_name == "file2learning":
            print(f"[OK] Connected to correct database: {db_name}")
            return True
        else:
            print(f"[WARN] Connected to database: {db_name} (expected: file2learning)")
            return False
    except Exception as e:
        print(f"[FAIL] Error checking database name: {e}")
        return False


def test_user_permissions():
    """Test if app_user has correct permissions"""
    print("\n[TEST] Testing user permissions...")
    try:
        db = SessionLocal()
        # Check current user
        result = db.execute(text("SELECT current_user")).fetchone()
        current_user = result[0] if result else None
        print(f"   Current user: {current_user}")
        
        # Check if app_user exists
        result = db.execute(text("""
            SELECT EXISTS(
                SELECT FROM pg_roles WHERE rolname = 'app_user'
            )
        """)).fetchone()
        app_user_exists = result[0] if result else False
        
        if app_user_exists:
            print("[OK] app_user exists")
        else:
            print("[FAIL] app_user does not exist")
            return False
        
        # Check database privileges
        result = db.execute(text("""
            SELECT has_database_privilege('app_user', 'file2learning', 'CONNECT')
        """)).fetchone()
        has_connect = result[0] if result else False
        
        if has_connect:
            print("[OK] app_user has CONNECT privilege")
        else:
            print("[FAIL] app_user does not have CONNECT privilege")
            return False
        
        db.close()
        return True
    except Exception as e:
        print(f"[FAIL] Error checking permissions: {e}")
        return False


def test_extensions():
    """Test if required extensions are installed"""
    print("\n[TEST] Testing database extensions...")
    required_extensions = ["uuid-ossp", "pg_trgm"]
    try:
        db = SessionLocal()
        result = db.execute(text("""
            SELECT extname FROM pg_extension
        """)).fetchall()
        installed_extensions = [row[0] for row in result]
        db.close()
        
        print(f"   Installed extensions: {', '.join(installed_extensions)}")
        
        missing = []
        for ext in required_extensions:
            if ext not in installed_extensions:
                missing.append(ext)
        
        if not missing:
            print("[OK] All required extensions are installed")
            return True
        else:
            print(f"[FAIL] Missing extensions: {', '.join(missing)}")
            print(f"[INFO] You may need to run: CREATE EXTENSION IF NOT EXISTS \"{missing[0]}\";")
            return False
    except Exception as e:
        print(f"[FAIL] Error checking extensions: {e}")
        return False


def test_schema_permissions():
    """Test if app_user has schema permissions"""
    print("\n[TEST] Testing schema permissions...")
    try:
        db = SessionLocal()
        # Check if app_user has privileges on public schema
        result = db.execute(text("""
            SELECT has_schema_privilege('app_user', 'public', 'USAGE')
        """)).fetchone()
        has_usage = result[0] if result else False
        
        result = db.execute(text("""
            SELECT has_schema_privilege('app_user', 'public', 'CREATE')
        """)).fetchone()
        has_create = result[0] if result else False
        
        db.close()
        
        if has_usage and has_create:
            print("[OK] app_user has proper schema permissions")
            return True
        else:
            print(f"[WARN] Schema permissions - USAGE: {has_usage}, CREATE: {has_create}")
            return False
    except Exception as e:
        print(f"[FAIL] Error checking schema permissions: {e}")
        return False


def test_tables():
    """Test if tables exist (after migrations)"""
    print("\n[TEST] Testing database tables...")
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if tables:
            print(f"[OK] Found {len(tables)} table(s):")
            for table in sorted(tables):
                print(f"   - {table}")
            return True
        else:
            print("[INFO] No tables found (migrations may not have run yet)")
            return True  # Not a failure, just informational
    except Exception as e:
        print(f"[FAIL] Error checking tables: {e}")
        return False


def test_database_url():
    """Display database configuration"""
    print("\n[INFO] Database Configuration:")
    print(f"   URL: {settings.DATABASE_URL}")
    print(f"   Type: PostgreSQL")
    print(f"   Database: file2learning")
    
    # Parse connection info
    try:
        url = settings.DATABASE_URL
        if "app_user" in url:
            print("   User: app_user")
        if "@postgres:" in url or "@localhost:" in url:
            if "@postgres:" in url:
                print("   Host: postgres (Docker)")
            else:
                print("   Host: localhost")
                print("   [WARN] If connecting from host, make sure you're connecting to Docker container")
                print("   [WARN] Windows PostgreSQL may be running on port 5432 instead!")
    except Exception as e:
        print(f"   [WARN] Could not parse connection info: {e}")


def main():
    """Run all database tests"""
    print("=" * 60)
    print("Database Connection and Configuration Test")
    print("=" * 60)
    
    test_database_url()
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Database Name", test_database_name),
        ("User Permissions", test_user_permissions),
        ("Extensions", test_extensions),
        ("Schema Permissions", test_schema_permissions),
        ("Tables", test_tables),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"[FAIL] Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("[SUMMARY] Test Results Summary:")
    print("=" * 60)
    
    all_passed = True
    for test_name, success in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"   {test_name:<30} {status}")
        if not success:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("[SUCCESS] All tests passed! Database is configured correctly.")
        print("\nNext steps:")
        print("   1. Run migrations: python -m alembic upgrade head")
        print("   2. Seed data (optional): python scripts/seed_data.py")
        return 0
    else:
        print("[WARNING] Some tests failed. Please fix the issues above.")
        print("\nTroubleshooting:")
        print("   1. Make sure PostgreSQL container is running: docker-compose up postgres -d")
        print("   2. Check if init scripts ran correctly")
        print("   3. Verify DATABASE_URL in environment variables")
        return 1


if __name__ == "__main__":
    exit(main())

