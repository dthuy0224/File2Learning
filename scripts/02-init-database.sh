#!/bin/bash
set -e

# This script runs on the file2learning database
# It's executed after the database is created by POSTGRES_DB

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "file2learning" <<'EOSQL'
    -- Create extensions for full-text search and UUID support
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pg_trgm";

    -- Grant schema privileges to app_user
    GRANT ALL PRIVILEGES ON SCHEMA public TO app_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO app_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO app_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO app_user;

    -- Set up database search path
    ALTER DATABASE file2learning SET search_path TO public;
EOSQL

