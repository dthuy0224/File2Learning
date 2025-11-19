#!/bin/bash
set -e

echo "🔄 Waiting for database to be ready..."
python /app/scripts/wait_for_db.py

echo "📋 Running Alembic migrations..."
cd /app
alembic upgrade head || echo "⚠️ Alembic migration encountered issues, running schema fix..."

echo "🔧 Applying schema fixes (for new columns)..."
python /app/check_schema.py

echo "🚀 Starting backend server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
