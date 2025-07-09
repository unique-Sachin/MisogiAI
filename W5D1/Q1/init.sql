-- Database initialization script for Medical AI Assistant
-- This script sets up the initial database schema

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS medical_ai_db;

-- Use the database
\c medical_ai_db;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Set timezone
SET timezone = 'UTC';

-- Create initial admin user (optional)
-- This would be handled by the application in production

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE medical_ai_db TO postgres; 