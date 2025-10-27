
-- Initialize database for File2Learning
-- This script runs when PostgreSQL container starts

-- Create the main database if it doesn't exist
SELECT 'CREATE DATABASE file2learning'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'file2learning')\gexec

-- Connect to the database and create extensions
\c file2learning;

-- Create extensions for full-text search and UUID support
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";


-- Tạo user app_user 
DO
$$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'app_user') THEN
      CREATE USER app_user WITH PASSWORD 'app_password';
   END IF;
END
$$;

-- Cấp quyền cho app_user
GRANT ALL PRIVILEGES ON DATABASE file2learning TO app_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO app_user;

ALTER ROLE app_user SET search_path TO public;

-- Optional: Create indexes for better performance
-- These will be created by Alembic migrations, but can be added here for reference

-- Create a default admin user (this will be handled by the application)
-- Note: Password should be hashed by the application, not stored in plain text
-- This is just a placeholder for documentation
-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE file2learning TO postgres;

-- Set up search path
ALTER DATABASE file2learning SET search_path TO public, public;

-- Create schema if needed (optional)
-- CREATE SCHEMA IF NOT EXISTS learning;
