#!/usr/bin/env python3
"""
Simple script to test database connection from host
"""
import psycopg2
import sys

def test_connection(host, port, database, user, password):
    """Test database connection"""
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()
        print(f"[OK] Connection successful!")
        print(f"     PostgreSQL version: {version[0][:50]}...")
        cur.close()
        conn.close()
        return True
    except psycopg2.OperationalError as e:
        print(f"[FAIL] Connection failed: {e}")
        return False
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("Testing database connection from host...")
    print("=" * 60)
    
    # Test with app_user
    print("\n[TEST] Connecting with app_user...")
    success = test_connection("localhost", 5432, "file2learning", "app_user", "app_password")
    
    if not success:
        print("\n[TEST] Trying with postgres user...")
        test_connection("localhost", 5432, "file2learning", "postgres", "abc123")
    
    sys.exit(0 if success else 1)

