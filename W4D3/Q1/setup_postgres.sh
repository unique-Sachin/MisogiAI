#!/bin/bash

# PostgreSQL Setup Script for MCP Discord Server
# This script sets up PostgreSQL database for testing

set -e

echo "🐘 Setting up PostgreSQL for MCP Discord Server"
echo "================================================="

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is not installed!"
    echo "Please install PostgreSQL first:"
    echo "  macOS: brew install postgresql"
    echo "  Ubuntu: sudo apt-get install postgresql postgresql-contrib"
    echo "  Windows: Download from https://www.postgresql.org/download/"
    exit 1
fi

# Check if PostgreSQL is running
if ! pg_isready -q; then
    echo "❌ PostgreSQL is not running!"
    echo "Please start PostgreSQL first:"
    echo "  macOS: brew services start postgresql"
    echo "  Ubuntu: sudo systemctl start postgresql"
    echo "  Windows: Start PostgreSQL service"
    exit 1
fi

echo "✅ PostgreSQL is installed and running"

# Database configuration
DB_NAME="mcp_discord"
DB_USER="mcp_user"
DB_PASSWORD="mcp_password"

echo "📊 Creating database and user..."

# Create database and user
psql -c "DROP DATABASE IF EXISTS $DB_NAME;" -U postgres 2>/dev/null || true
psql -c "DROP USER IF EXISTS $DB_USER;" -U postgres 2>/dev/null || true

psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" -U postgres
psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;" -U postgres
psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;" -U postgres

echo "✅ Database '$DB_NAME' created with user '$DB_USER'"

# Test connection
echo "🔍 Testing database connection..."
PGPASSWORD=$DB_PASSWORD psql -h localhost -U $DB_USER -d $DB_NAME -c "SELECT version();" > /dev/null

if [ $? -eq 0 ]; then
    echo "✅ Database connection successful!"
else
    echo "❌ Database connection failed!"
    exit 1
fi

echo ""
echo "🎉 PostgreSQL setup complete!"
echo "Database URL: postgresql+asyncpg://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME"
echo ""
echo "Next steps:"
echo "1. Make sure your .env file has the correct DATABASE_URL"
echo "2. Run: python3 -m uvicorn app.main:app --reload"
echo "3. Test with: python3 test_helper.py" 