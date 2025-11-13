-- Initialize database for File2Learning
-- This script runs when PostgreSQL container starts for the first time
-- Note: This script only runs if the data directory is empty
-- This script runs on the default 'postgres' database to create users

-- Create the app_user if it doesn't exist
DO
$$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'app_user') THEN
      CREATE USER app_user WITH PASSWORD 'app_password';
   ELSE
      -- Update password if user exists (useful for development)
      ALTER USER app_user WITH PASSWORD 'app_password';
   END IF;
END
$$;

-- Grant privileges to app_user on the file2learning database
-- Note: Database 'file2learning' is already created by POSTGRES_DB environment variable
GRANT ALL PRIVILEGES ON DATABASE file2learning TO app_user;

-- Set search path for app_user role
ALTER ROLE app_user SET search_path TO public;
