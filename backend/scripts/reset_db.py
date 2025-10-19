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

        # Drop all tables and recreate schema
        from sqlalchemy import text
        db = SessionLocal()

        # Get all table names
        result = db.execute(text("""
            SELECT tablename FROM pg_tables
            WHERE schemaname = 'public'
            AND tablename NOT IN ('alembic_version')
        """))
        tables = [row[0] for row in result]

        # Drop tables in reverse dependency order
        for table in reversed(tables):
            try:
                db.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
                print(f"  ✅ Dropped table: {table}")
            except Exception as e:
                print(f"  ⚠️  Error dropping {table}: {e}")

        db.commit()
        db.close()

        print("🔧 Running migrations...")
        os.system("python -m alembic upgrade heads")

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
        SELECT tablename FROM pg_tables
        WHERE schemaname = 'public'
        AND tablename NOT IN ('alembic_version')
        ORDER BY tablename;
        """

        result = db.execute(text(tables_query))
        tables = [row[0] for row in result]

        for table in tables:
            print(f"\n🏷️  Table: {table}")

            # Get column info
            columns_query = """
            SELECT
                column_name,
                data_type,
                is_nullable,
                column_default,
                CASE WHEN column_name IN (
                    SELECT column_name FROM information_schema.key_column_usage
                    WHERE table_name = :table_name AND constraint_name LIKE '%_pkey'
                ) THEN 'PRIMARY KEY' ELSE '' END as is_primary_key
            FROM information_schema.columns
            WHERE table_name = :table_name
            ORDER BY ordinal_position;
            """
            result = db.execute(text(columns_query), {"table_name": table})
            columns = result.fetchall()

            for col in columns:
                col_name, col_type, is_nullable, col_default, pk = col
                not_null = "NOT NULL" if is_nullable == "NO" else "NULL"
                print(f"  - {col_name:<20} {col_type:<15} {not_null:<10} {pk}")

            # Get indexes
            indexes_query = """
            SELECT
                indexname as index_name,
                indexdef
            FROM pg_indexes
            WHERE tablename = :table_name;
            """
            result = db.execute(text(indexes_query), {"table_name": table})
            indexes = result.fetchall()

            if indexes:
                print("  Indexes:")
                for idx in indexes:
                    idx_name = idx[0]
                    print(f"    - {idx_name}")

        # Show record counts
        print("\n📊 Record Counts:")
        print("=" * 30)
        for table in tables:
            count_query = text(f"SELECT COUNT(*) FROM {table};")
            result = db.execute(count_query)
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
