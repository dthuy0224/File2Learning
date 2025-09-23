#!/usr/bin/env python3
"""
Database reset script - drops all tables and recreates with sample data

WARNING: This will delete all existing data!
"""
import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

import os
from sqlalchemy import text

from app.core.database import SessionLocal, engine
from seed_data import seed_database


def reset_database():
    """Reset database - drop all tables and recreate"""
    print("⚠️  WARNING: This will delete ALL existing data!")
    
    # In development, we can safely reset
    if os.getenv("ENV", "development") != "development":
        print("❌ This script can only be run in development environment!")
        return False
    
    try:
        print("🗑️  Dropping all tables...")
        
        # Drop all tables by dropping the database file (SQLite only)
        db_path = "app.db"
        if os.path.exists(db_path):
            os.remove(db_path)
            print("✅ Database file removed")
        
        print("🔧 Running migrations...")
        os.system("python -m alembic upgrade head")
        
        print("🌱 Seeding database...")
        seed_database()
        
        return True
        
    except Exception as e:
        print(f"❌ Error during database reset: {e}")
        return False


def show_schema():
    """Display database schema information"""
    db = SessionLocal()
    try:
        print("\n📋 Database Schema Summary:")
        print("=" * 50)
        
        # Get table info
        tables_query = """
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name != 'alembic_version'
        ORDER BY name;
        """
        
        result = db.execute(text(tables_query))
        tables = [row[0] for row in result]
        
        for table in tables:
            print(f"\n🏷️  Table: {table}")
            
            # Get column info
            columns_query = f"PRAGMA table_info({table});"
            result = db.execute(text(columns_query))
            columns = result.fetchall()
            
            for col in columns:
                col_name = col[1]
                col_type = col[2]
                not_null = "NOT NULL" if col[3] else "NULL"
                pk = "PRIMARY KEY" if col[5] else ""
                print(f"  - {col_name:<20} {col_type:<15} {not_null:<10} {pk}")
            
            # Get indexes
            indexes_query = f"PRAGMA index_list({table});"
            result = db.execute(text(indexes_query))
            indexes = result.fetchall()
            
            if indexes:
                print("  Indexes:")
                for idx in indexes:
                    idx_name = idx[1]
                    unique = "UNIQUE" if idx[2] else ""
                    print(f"    - {idx_name} {unique}")
        
        # Show record counts
        print(f"\n📊 Record Counts:")
        print("=" * 30)
        for table in tables:
            count_query = f"SELECT COUNT(*) FROM {table};"
            result = db.execute(text(count_query))
            count = result.scalar()
            print(f"{table:<20}: {count}")
            
    except Exception as e:
        print(f"❌ Error showing schema: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Database management script')
    parser.add_argument('--reset', action='store_true', help='Reset database with sample data')
    parser.add_argument('--schema', action='store_true', help='Show database schema')
    
    args = parser.parse_args()
    
    if args.reset:
        success = reset_database()
        if success:
            show_schema()
    elif args.schema:
        show_schema()
    else:
        print("Usage:")
        print("  python reset_db.py --reset   # Reset database with sample data")
        print("  python reset_db.py --schema  # Show current schema")
